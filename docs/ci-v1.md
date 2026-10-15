# Shared CI workflows, version 1

Audience: engineers wiring a repository to the organization's shared CI.

This repository publishes one reusable workflow per stack. A repository calls one of them from a small `ci.yml` and gets lint, typecheck, build, tests, a dependency audit and one aggregated check, `ci / ci-summary`, that branch protection requires.

| Workflow | Stack |
|---|---|
| `ci-nestjs.yml` | Node + TypeScript backend (NestJS or similar), pnpm |
| `ci-nextjs.yml` | Node + TypeScript frontend (Next.js or similar), pnpm |
| `ci-prisma.yml` | Repository that owns a Prisma schema and its migrations, pnpm |
| `ci-python.yml` | Python service, pip and requirements files |
| `ci-flutter.yml` | Flutter app or package |
| `pr-policy.yml` | Closes pull requests that skip the promotion path |

The older `reusable-ci-*.yml` files are frozen and kept only for callers that have not moved yet.

## Calling a workflow

```yaml
name: ci
on:
  pull_request:
    branches: [dev, staging, prod]
concurrency:
  group: ci-${{ github.event.pull_request.number }}
  cancel-in-progress: true
permissions:
  contents: read
  packages: read
jobs:
  ci:
    uses: Viero-Tech/.github/.github/workflows/ci-nestjs.yml@v1
    with:
      prisma: true
      database: postgres
      migrate-script: db:migrate
```

- Name the job `ci`. The required check is then `ci / ci-summary`.
- Do not add `paths-ignore`. A pull request that changes only Markdown files or `docs/` finishes in seconds with a green check.
- Set `concurrency` in the caller. The shared workflows define none, because a concurrency group inside a reusable workflow is evaluated in the caller's context and would cancel sibling calls.
- Grant `contents: read` and `packages: read`. A reusable workflow cannot raise permissions above what the caller grants.

## What the repository must provide

| Stack | File | Example |
|---|---|---|
| Node stacks | `.nvmrc` in the working directory or any parent | `22` |
| Node stacks | `packageManager` in the `package.json` next to `pnpm-lock.yaml` | `"packageManager": "pnpm@10.28.1"` |
| Node stacks | `pnpm-lock.yaml` in the working directory or any parent | |
| Python | `.python-version` in the working directory or any parent | `3.11` |
| Python | `requirements.txt` and `requirements-dev.txt` (ruff, pytest, and mypy when enabled, pinned) | `ruff==0.17.0` |
| Flutter | `pubspec.yaml` in the working directory; the exact SDK version as the `flutter-version` input | `3.35.7` |

When a file is missing, the `preflight` job fails at once with a message that names the file to add.

In a pnpm workspace, point `working-directory` at the package. Install runs where the lockfile is; every other command runs in the package.

## Jobs

| Job | nestjs | nextjs | prisma | python | flutter |
|---|---|---|---|---|---|
| `preflight` | toolchain files, inputs, changed files | same | same | same | same |
| `branch-policy` | promotion source check | same | same | same | same |
| `lint` | `eslint . --max-warnings=N` | same | `prisma format --check` | `ruff check .` | `flutter analyze` |
| `typecheck` | `tsc --noEmit` | same | `prisma validate` | `mypy` (opt-in) | covered by `flutter analyze` |
| `build` | `pnpm run build` | same, with `build-env` | | | |
| `test` | `test:ci` script, else `test` | same | migrations applied to an empty database, then compared with the schema | `pytest` | `flutter test` |
| `e2e` | opt-in script, services available | opt-in script | | | |
| `contract` | opt-in script, services available | opt-in script | | | |
| `audit` | `pnpm audit --audit-level=high` when the PR changes the lockfile | same | same | `pip-audit` when the PR changes a requirements file | |
| `ci-summary` | the required check | same | same | same | same |

With `prisma: true`, `prisma generate` runs after install in every Node job that runs code, so lint, typecheck, build and tests see the generated client.

### ci-summary

`ci-summary` runs after every other job, whatever their result, and fails when:

- any job failed or was cancelled;
- a job was skipped although it is switched on. A skip is accepted only for a job switched off by its input, for every code job on a docs-only change, and for `audit` when the lockfile or requirements did not change.

Its output `failed-jobs` lists the jobs that caused a failure.

### branch-policy

On a pull request, `branch-policy` fails when the head branch is not the promotion source of the base branch. The default rules are `staging:dev,prod:staging`: `staging` accepts only `dev`, `prod` accepts only `staging`. Other bases have no rule. An organization owner can still merge such a pull request as a hotfix through the ruleset bypass.

## Inputs

### ci-nestjs.yml

| Input | Type | Default | Purpose |
|---|---|---|---|
| `working-directory` | string | `.` | Package to check |
| `prisma` | boolean | `false` | Run `prisma generate` before lint, typecheck, build and tests |
| `build` | boolean | `true` | Run `pnpm run build` |
| `test` | boolean | `true` | Run unit tests. Zero tests fail the job unless this is `false` |
| `e2e` | boolean | `false` | Run the e2e job |
| `e2e-script` | string | `test:e2e` | Script the e2e job runs |
| `contract` | boolean | `false` | Run the contract job |
| `contract-script` | string | `contract` | Script the contract job runs |
| `lint-max-warnings` | string | `0` | ESLint warning budget |
| `database` | string | `none` | `none`, `postgres` (16) or `postgis` (16 + 3.5) service for test, e2e and contract |
| `database-image` | string | | Replaces the default database image |
| `database-port` | string | `5432` | Host port of the database service |
| `database-name` | string | `ci` | Database created in the service |
| `database-password` | string | `postgres` | Password of the `postgres` user, CI only |
| `redis` | boolean | `false` | Redis service for test, e2e and contract |
| `migrate-script` | string | | Script run before test, e2e and contract |
| `node-options` | string | | `NODE_OPTIONS` for test, e2e and contract |
| `env` | string | | Non-secret `KEY=value` lines exported to build, test, e2e and contract. CI-only values; the workflow refuses names it sets itself (`DATABASE_URL`, `REDIS_URL`, `NODE_OPTIONS`, `NODE_AUTH_TOKEN`, `CI`, `PATH`, `GITHUB_*`, `RUNNER_*`, `ACTIONS_*`) |
| `branch-rules` | string | `staging:dev,prod:staging` | Promotion sources |
| `timeout-minutes` | number | `15` | Timeout of each job except e2e |
| `e2e-timeout-minutes` | number | `30` | Timeout of the e2e job |

With a database, test, e2e and contract see `DATABASE_URL=postgresql://postgres:<password>@localhost:<port>/<name>`. With Redis, they see `REDIS_URL=redis://localhost:6379`.

### ci-nextjs.yml

Same as `ci-nestjs.yml` without the database, Redis and `migrate-script` inputs, plus:

| Input | Type | Default | Purpose |
|---|---|---|---|
| `build-env` | string | | Non-secret `KEY=value` lines exported to the build job |

`NEXT_TELEMETRY_DISABLED=1` is set for every job.

### ci-prisma.yml

| Input | Type | Default | Purpose |
|---|---|---|---|
| `working-directory` | string | `.` | Package holding the schema |
| `schema-path` | string | `prisma/schema.prisma` | Schema file or schema directory, relative to `working-directory` |
| `test` | boolean | `true` | Run the migration check |
| `database` | string | `postgres` | `postgres` or `postgis` |
| `database-image` | string | | Replaces the default database image |
| `branch-rules` | string | `staging:dev,prod:staging` | Promotion sources |
| `timeout-minutes` | number | `15` | Timeout of each job |

Prisma 6 and Prisma 7 are supported. On Prisma 7, `migrate deploy` and the drift check read the datasource from `prisma.config.ts`, which must take its URL from `DATABASE_URL`.

### ci-python.yml

| Input | Type | Default | Purpose |
|---|---|---|---|
| `working-directory` | string | `.` | Project to check |
| `requirements-file` | string | `requirements.txt` | Runtime requirements |
| `dev-requirements-file` | string | `requirements-dev.txt` | Tooling requirements |
| `mypy` | boolean | `false` | Run mypy with the repository's configuration |
| `test` | boolean | `true` | Run pytest. No tests collected is a failure |
| `branch-rules` | string | `staging:dev,prod:staging` | Promotion sources |
| `timeout-minutes` | number | `15` | Timeout of each job |

### ci-flutter.yml

| Input | Type | Default | Purpose |
|---|---|---|---|
| `flutter-version` | string | required | Exact Flutter SDK version |
| `working-directory` | string | `.` | Directory holding `pubspec.yaml` |
| `test` | boolean | `true` | Run `flutter test` |
| `branch-rules` | string | `staging:dev,prod:staging` | Promotion sources |
| `timeout-minutes` | number | `15` | Timeout of each job |

### pr-policy.yml

```yaml
name: pr-policy
on:
  pull_request:
    types: [opened, reopened, edited]
    branches: [staging, prod]
permissions:
  contents: read
  pull-requests: write
jobs:
  policy:
    uses: Viero-Tech/.github/.github/workflows/pr-policy.yml@v1
    secrets:
      membership-token: ${{ secrets.ORG_MEMBERSHIP_READ_TOKEN }}
```

| Input or secret | Default | Purpose |
|---|---|---|
| `branch-rules` | `staging:dev,prod:staging` | Promotion sources |
| `owner-logins` | | Comma-separated logins treated as owners when no token is passed |
| `membership-token` (secret) | | Token that can read organization membership; an author with role `admin` is an owner |

A pull request whose head is not the promotion source of its base is closed with a comment, unless its author is an organization owner. `GITHUB_TOKEN` cannot read organization membership, so pass `membership-token` or `owner-logins`; with neither, the job fails and closes nothing. An `edited` event is acted on only when the base branch changed.

## Releases

1. Every change arrives by pull request. The `selftest` workflow runs actionlint, unit tests for the shell logic, and each shared workflow against the fixtures in `.github/fixtures` (pass, fail-lint, fail-type, fail-test, and a run with jobs switched off). Its check is `ci / ci-summary`.
2. After merge to `main`, canary repositories call `@main`.
3. When the canaries stay green, tag the merge commit with an immutable `vX.Y.Z` and move `v1` to it:

   ```sh
   git tag -a v1.0.0 -m "v1.0.0" <commit>
   git tag -f v1 v1.0.0
   git push origin v1.0.0
   git push --force origin v1
   ```

4. Callers use `@v1`. A caller that needs a fixed version uses `@vX.Y.Z`.
5. A breaking change (a removed or renamed input, a new required file, a changed check name) is released as `v2` and adopted by pull request in each repository. `v1` keeps receiving fixes.

Tags are protected by a ruleset: only maintainers of this repository create or move them, and `vX.Y.Z` tags are never moved or deleted.
