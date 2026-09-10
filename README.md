# Viero-Tech/.github

Org-wide shared configuration for the Viero GitHub organization.

| Path | What it is |
|---|---|
| `profile/README.md` | The public organization profile shown at [github.com/Viero-Tech](https://github.com/Viero-Tech). |
| `.github/workflows/reusable-*.yml` | Reusable CI and review workflows that every product repository calls. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Default pull request template for every repository in the organization. |
| `.github/dependabot.yml` | Weekly GitHub Actions updates for this repository. |
| `CODEOWNERS` | Every change here requires the devops team. |

For members: the engineering landing page, the per-repo caller stubs and the rollout scripts live in the private `.github-private` repository.

## Reusable workflows

A repository opts in with a caller workflow at `.github/workflows/ci.yml`:

```yaml
name: CI
on:
  pull_request:
    branches: [dev, staging]
jobs:
  ci:
    uses: Viero-Tech/.github/.github/workflows/reusable-ci-nestjs.yml@main
```

The caller job must be named `ci`. Every CI workflow ends in a `ci-summary` job, and the branch rulesets require the check `ci / ci-summary`, so the job name is part of the contract.

| Workflow | Jobs | Inputs and defaults |
|---|---|---|
| `reusable-ci-nestjs.yml` | lint, typecheck, test, ci-summary | `node-version` 22, `pnpm-version` 9, `submodules` false, `prisma-generate` false. Secret `ssh-key` for submodule checkout. |
| `reusable-ci-nextjs.yml` | lint, typecheck, test, ci-summary | `node-version` 22, `pnpm-version` 9 |
| `reusable-ci-prisma.yml` | validate, ci-summary | `node-version` 22 |
| `reusable-ci-flutter.yml` | analyze, test, ci-summary | `flutter-version` 3.8.1 |
| `reusable-ci-python.yml` | lint, test, ci-summary | `python-version` 3.10 |
| `reusable-ci-generic.yml` | lint, typecheck, ci-summary | `node-version` 22 |
| `reusable-claude-review.yml` | review | `aws_role_arn` (required), `aws_region`, `bedrock_model_id`, `extra_prompt`, `skip_drafts` true, `use_sticky_comment` true, `claude_args_extra` |
| `reusable-claude-mention.yml` | claude | `aws_role_arn` (required), `aws_region`, `bedrock_model_id`, `extra_prompt`, `claude_args_extra` |

pnpm version: if the repository pins `packageManager` in `package.json`, pass `pnpm-version: ''` so the pin wins. Passing both makes `pnpm/action-setup` fail with "Multiple versions of pnpm specified".

The two Claude workflows review pull requests and answer `@claude` mentions. They authenticate to Amazon Bedrock through GitHub OIDC; the caller passes the role ARN and region from repository variables, so no long-lived key is stored anywhere.

## Changing this repository

Every caller pins `@main`, so a change here lands in every repository on its next run. Open a pull request. The `protect-main` ruleset requires two approvals and a devops code-owner review; the devops team can bypass through a pull request.
