"""Unit tests for the shell logic embedded in the shared CI workflows.

The fixture runs in selftest.yml prove the workflows end to end. These tests
cover the branches a fixture cannot reach cheaply: an unexpectedly skipped
job, a docs-only change, a missing version file, promotion rules, and a
pnpm workspace whose lockfile sits above the working directory.

Each test extracts a step's `run:` script from the workflow file and runs it
with bash, so the code under test is exactly the code that ships.

Usage: python3 .github/selftest/test_workflow_scripts.py   (needs PyYAML, git, jq, bash)
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
NODE_STACKS = ["ci-nestjs.yml", "ci-nextjs.yml", "ci-prisma.yml"]
ALL_STACKS = NODE_STACKS + ["ci-python.yml", "ci-flutter.yml"]

failures = []


def check(condition, message):
    if condition:
        print(f"  ok   {message}")
    else:
        print(f"  FAIL {message}")
        failures.append(message)


def step_script(workflow, job, step_name):
    data = yaml.safe_load((WORKFLOWS / workflow).read_text())
    for step in data["jobs"][job]["steps"]:
        if step.get("name") == step_name:
            script = step["run"]
            assert "${{" not in script, f"{workflow}:{job} '{step_name}' must read inputs from env, not expressions"
            return script, step.get("env", {})
    raise KeyError(f"{workflow}: no step '{step_name}' in job '{job}'")


def run_script(script, env, cwd):
    with tempfile.NamedTemporaryFile("w+", delete=False) as output:
        output_path = output.name
    full_env = {"PATH": os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp"), "GITHUB_OUTPUT": output_path}
    full_env.update(env)
    proc = subprocess.run(["bash", "-c", script], cwd=cwd, env=full_env, capture_output=True, text=True)
    outputs = {}
    for line in Path(output_path).read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            outputs[key] = value
    os.unlink(output_path)
    return proc.returncode, proc.stdout + proc.stderr, outputs


# ---------------------------------------------------------------- ci-summary

def test_summary(workflow):
    print(f"{workflow}: ci-summary")
    script, _ = step_script(workflow, "ci-summary", "Summarise job results")
    cases = [
        ("all enabled jobs succeed", "lint success true\ntest success true\n", 0, ""),
        ("a job switched off by its input is skipped", "lint success true\ntest skipped false\n", 0, ""),
        ("docs-only change skips every heavy job", "preflight success true\nlint skipped false\ntest skipped false\n", 0, ""),
        ("an enabled job is skipped", "lint success true\ntest skipped true\n", 1, "test"),
        ("a job fails", "lint failure true\ntest success true\n", 1, "lint"),
        ("a job is cancelled", "lint cancelled true\n", 1, "lint"),
        ("a disabled job is cancelled", "e2e cancelled false\n", 1, "e2e"),
        ("a missing result is not a pass", "lint  true\n", 1, "lint"),
        ("several jobs fail", "lint failure true\ntypecheck success true\ntest failure true\n", 1, "lint test"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for title, states, want_code, want_failed in cases:
            code, log, outputs = run_script(script, {"JOB_STATES": states}, tmp)
            check(code == want_code and outputs.get("failed-jobs") == want_failed,
                  f"{title} -> exit {want_code}, failed-jobs '{want_failed}' (got {code}, '{outputs.get('failed-jobs')}')")


# ------------------------------------------------------------- branch-policy

def test_branch_policy(workflow):
    print(f"{workflow}: branch-policy")
    script, _ = step_script(workflow, "branch-policy", "Check promotion source")
    default_rules = "staging:dev,prod:staging"
    cases = [
        ("dev into staging", "pull_request", "staging", "dev", default_rules, 0),
        ("feature into staging", "pull_request", "staging", "feat/x", default_rules, 1),
        ("staging into prod", "pull_request", "prod", "staging", default_rules, 0),
        ("dev into prod", "pull_request", "prod", "dev", default_rules, 1),
        ("feature into dev", "pull_request", "dev", "feat/x", default_rules, 0),
        ("custom rules: main into prod", "pull_request", "prod", "main", "prod:main", 0),
        ("custom rules: feature into prod", "pull_request", "prod", "feat/x", "prod:main", 1),
        ("not a pull request", "push", "", "", default_rules, 0),
        ("malformed rules", "pull_request", "staging", "dev", "staging", 1),
        ("rules with shell characters", "pull_request", "staging", "dev", "staging:$(id)", 1),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for title, event, base, head, rules, want in cases:
            env = {"EVENT_NAME": event, "BASE_REF": base, "HEAD_REF": head, "BRANCH_RULES": rules}
            code, _, _ = run_script(script, env, tmp)
            check(code == want, f"{title} -> exit {want} (got {code})")


# ------------------------------------------------------------ git scaffolding

def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"})


def make_repo(tmp, files, changed):
    """A repository whose HEAD^1..HEAD diff is exactly `changed`."""
    repo = Path(tmp) / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    for path, content in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    for path, content in changed.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", "change")
    return repo


NODE_WORKSPACE = {
    ".nvmrc": "22\n",
    "package.json": '{"private": true, "packageManager": "pnpm@10.28.1"}\n',
    "pnpm-lock.yaml": "lockfileVersion: '9.0'\n",
    "pnpm-workspace.yaml": "packages:\n  - 'apps/*'\n",
    "apps/api/package.json": '{"name": "api"}\n',
    "apps/api/src/main.ts": "export {};\n",
    "README.md": "x\n",
}


def node_env(workflow, overrides):
    _, step_env = step_script(workflow, "preflight", "Resolve toolchain and changes")
    env = {}
    for key, value in step_env.items():
        value = str(value)
        if "${{" not in value:
            env[key] = value
    defaults = {
        "EVENT_NAME": "pull_request", "WORKING_DIRECTORY": "apps/api", "LINT_MAX_WARNINGS": "0",
        "DATABASE": "postgres" if workflow == "ci-prisma.yml" else "none", "DATABASE_IMAGE": "",
        "DATABASE_PORT": "5432", "DATABASE_NAME": "ci", "DATABASE_PASSWORD": "postgres", "REDIS": "false",
        "MIGRATE_SCRIPT": "", "E2E_SCRIPT": "test:e2e", "CONTRACT_SCRIPT": "contract", "BUILD_ENV": "",
    }
    for key, value in defaults.items():
        env.setdefault(key, value)
    env.update(overrides)
    return env


def test_node_preflight(workflow):
    print(f"{workflow}: preflight")
    script, _ = step_script(workflow, "preflight", "Resolve toolchain and changes")

    def run(files, changed, overrides):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp, files, changed)
            return run_script(script, node_env(workflow, overrides), repo)

    code, log, out = run(NODE_WORKSPACE, {"apps/api/src/main.ts": "export const a = 1;\n"}, {})
    check(code == 0 and out.get("install-root") == "." and out.get("node-version-file") == ".nvmrc"
          and out.get("lockfile") == "pnpm-lock.yaml" and out.get("package-json") == "package.json",
          f"workspace member resolves lockfile, .nvmrc and packageManager from the root ({code}, {out})")
    check(out.get("docs-only") == "false" and out.get("lockfile-changed") == "false",
          "a code change is not docs-only and leaves the lockfile unchanged")

    code, _, out = run(NODE_WORKSPACE, {"README.md": "y\n", "docs/guide.md": "z\n", "docs/img.png": "p"}, {})
    check(code == 0 and out.get("docs-only") == "true", "markdown and docs/ changes are docs-only")

    code, _, out = run(NODE_WORKSPACE, {"apps/api/NOTES.md": "n\n", "apps/api/src/main.ts": "export const b = 2;\n"}, {})
    check(out.get("docs-only") == "false", "markdown plus code is not docs-only")

    code, _, out = run(NODE_WORKSPACE, {"pnpm-lock.yaml": "lockfileVersion: '9.0'\n# changed\n"}, {})
    check(code == 0 and out.get("lockfile-changed") == "true", "a lockfile change is detected")

    code, _, out = run(NODE_WORKSPACE, {}, {"EVENT_NAME": "workflow_dispatch"})
    check(code == 0 and out.get("docs-only") == "false" and out.get("lockfile-changed") == "true",
          "outside a pull request everything runs, audit included")

    code, _, out = run(NODE_WORKSPACE, {"apps/api/src/main.ts": "export const c = 3;\n"}, {"WORKING_DIRECTORY": "."})
    check(code == 0 and out.get("install-root") == ".", "working-directory '.' resolves the root")

    no_nvmrc = {k: v for k, v in NODE_WORKSPACE.items() if k != ".nvmrc"}
    code, log, _ = run(no_nvmrc, {"apps/api/src/main.ts": "x"}, {})
    check(code == 1 and ".nvmrc" in log, "a missing .nvmrc fails and names the file")

    no_pm = {**NODE_WORKSPACE, "package.json": '{"private": true}\n'}
    code, log, _ = run(no_pm, {"apps/api/src/main.ts": "x"}, {})
    check(code == 1 and "packageManager" in log, "a missing packageManager fails and names the field")

    npm_pm = {**NODE_WORKSPACE, "package.json": '{"packageManager": "npm@10.0.0"}\n'}
    code, log, _ = run(npm_pm, {"apps/api/src/main.ts": "x"}, {})
    check(code == 1 and "packageManager" in log, "a non-pnpm packageManager fails")

    no_lock = {k: v for k, v in NODE_WORKSPACE.items() if k != "pnpm-lock.yaml"}
    code, log, _ = run(no_lock, {"apps/api/src/main.ts": "x"}, {})
    check(code == 1 and "pnpm-lock.yaml" in log, "a missing lockfile fails and names the file")

    for title, overrides in [
        ("working-directory outside the repository", {"WORKING_DIRECTORY": "../x"}),
        ("absolute working-directory", {"WORKING_DIRECTORY": "/etc"}),
        ("missing working-directory", {"WORKING_DIRECTORY": "apps/web"}),
        ("unknown database", {"DATABASE": "mysql"}),
        ("non-numeric warning budget", {"LINT_MAX_WARNINGS": "many"}),
        ("privileged database port", {"DATABASE_PORT": "80"}),
        ("script name with shell characters", {"E2E_SCRIPT": "e2e; id"}),
        ("malformed build-env line", {"BUILD_ENV": "NOT A PAIR"}),
    ]:
        code, _, _ = run(NODE_WORKSPACE, {"apps/api/src/main.ts": "x"}, overrides)
        check(code == 1, f"{title} fails")

    if workflow == "ci-prisma.yml":
        code, log, _ = run(NODE_WORKSPACE, {"apps/api/src/main.ts": "x"}, {"DATABASE": "none"})
        check(code == 1, "the prisma stack refuses database none")
    else:
        code, _, out = run(NODE_WORKSPACE, {"apps/api/src/main.ts": "x"}, {"DATABASE": "postgis", "REDIS": "true"})
        check(code == 0 and out.get("database-image", "").startswith("postgis/postgis:")
              and out.get("redis-image", "").startswith("redis:"), "postgis and redis resolve their default images")
        code, _, out = run(NODE_WORKSPACE, {"apps/api/src/main.ts": "x"},
                           {"DATABASE": "postgres", "DATABASE_IMAGE": "postgres:17-alpine"})
        check(out.get("database-image") == "postgres:17-alpine", "database-image overrides the default")
        code, _, out = run(NODE_WORKSPACE, {"apps/api/src/main.ts": "x"}, {})
        check(out.get("database-image") == "" and out.get("redis-image") == "", "database none starts no service")


PYTHON_PROJECT = {
    ".python-version": "3.12\n",
    "requirements.txt": "httpx==0.28.1\n",
    "requirements-dev.txt": "pytest==9.1.1\nruff==0.17.0\n",
    "app/main.py": "x = 1\n",
}


def test_python_preflight():
    print("ci-python.yml: preflight")
    script, _ = step_script("ci-python.yml", "preflight", "Resolve toolchain and changes")
    base_env = {"EVENT_NAME": "pull_request", "WORKING_DIRECTORY": ".", "REQUIREMENTS_FILE": "requirements.txt",
                "DEV_REQUIREMENTS_FILE": "requirements-dev.txt", "MYPY": "false"}

    def run(files, changed, overrides):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp, files, changed)
            return run_script(script, {**base_env, **overrides}, repo)

    code, _, out = run(PYTHON_PROJECT, {"app/main.py": "x = 2\n"}, {})
    check(code == 0 and out.get("python-version-file") == ".python-version" and out.get("requirements-changed") == "false",
          f"a code change resolves .python-version and leaves requirements unchanged ({out})")
    code, _, out = run(PYTHON_PROJECT, {"requirements.txt": "httpx==0.28.2\n"}, {})
    check(out.get("requirements-changed") == "true", "a requirements change is detected")
    code, _, out = run(PYTHON_PROJECT, {"README.md": "x\n"}, {})
    check(out.get("docs-only") == "true", "a markdown-only change is docs-only")
    code, log, _ = run({k: v for k, v in PYTHON_PROJECT.items() if k != ".python-version"}, {"app/main.py": "y"}, {})
    check(code == 1 and ".python-version" in log, "a missing .python-version fails and names the file")
    code, log, _ = run({**PYTHON_PROJECT, "requirements-dev.txt": "pytest==9.1.1\n"}, {"app/main.py": "y"}, {})
    check(code == 1 and "ruff" in log, "dev requirements without ruff fail")
    code, log, _ = run(PYTHON_PROJECT, {"app/main.py": "y"}, {"MYPY": "true"})
    check(code == 1 and "mypy" in log, "mypy on without mypy in dev requirements fails")
    code, log, _ = run({k: v for k, v in PYTHON_PROJECT.items() if k != "requirements.txt"}, {"app/main.py": "y"}, {})
    check(code == 1 and "requirements.txt" in log, "a missing requirements file fails")


def test_flutter_preflight():
    print("ci-flutter.yml: preflight")
    script, _ = step_script("ci-flutter.yml", "preflight", "Resolve toolchain and changes")
    files = {"app/pubspec.yaml": "name: a\n", "app/lib/a.dart": "void main() {}\n"}
    base_env = {"EVENT_NAME": "pull_request", "WORKING_DIRECTORY": "app", "FLUTTER_VERSION": "3.35.7"}

    def run(changed, overrides):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp, files, changed)
            return run_script(script, {**base_env, **overrides}, repo)

    code, _, out = run({"app/lib/a.dart": "void main() { }\n"}, {})
    check(code == 0 and out.get("docs-only") == "false", "a code change runs analyze and tests")
    code, _, out = run({"docs/x.md": "x"}, {})
    check(code == 0 and out.get("docs-only") == "true", "a docs change is docs-only")
    code, _, _ = run({"app/lib/a.dart": "x"}, {"FLUTTER_VERSION": "^3.8.1"})
    check(code == 1, "a version range is rejected")
    code, _, _ = run({"app/lib/a.dart": "x"}, {"WORKING_DIRECTORY": "."})
    check(code == 1, "a directory without pubspec.yaml fails")


def test_shared_scripts_identical():
    print("shared scripts are identical across workflows")
    for job, step in [("branch-policy", "Check promotion source"), ("ci-summary", "Summarise job results")]:
        scripts = {wf: step_script(wf, job, step)[0] for wf in ALL_STACKS}
        check(len(set(scripts.values())) == 1, f"'{step}' is the same in every ci-*.yml")
    scripts = {wf: step_script(wf, "preflight", "Resolve toolchain and changes")[0] for wf in NODE_STACKS}
    check(len(set(scripts.values())) == 1, "the Node preflight is the same in ci-nestjs, ci-nextjs and ci-prisma")


def main():
    for workflow in ALL_STACKS:
        test_summary(workflow)
        test_branch_policy(workflow)
    for workflow in NODE_STACKS:
        test_node_preflight(workflow)
    test_python_preflight()
    test_flutter_preflight()
    test_shared_scripts_identical()
    if failures:
        print(f"\n{len(failures)} check(s) failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
