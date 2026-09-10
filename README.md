# Viero-Tech/.github

Shared configuration for the Viero GitHub organization.

| Path | Purpose |
|---|---|
| `profile/README.md` | Public organization profile displayed at [github.com/Viero-Tech](https://github.com/Viero-Tech). |
| `.github/workflows/reusable-*.yml` | Reusable CI and review workflows called by the organization's repositories. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Default pull request template for all repositories in the organization. |
| `.github/dependabot.yml` | Weekly GitHub Actions dependency updates for this repository. |
| `CODEOWNERS` | Changes to this repository require review by the devops team. |

Internal documentation, caller workflow templates and rollout scripts are maintained in the private `.github-private` repository.

## Reusable workflows

A repository opts in by adding a caller workflow at `.github/workflows/ci.yml`:

```yaml
name: CI
on:
  pull_request:
    branches: [dev, staging]
jobs:
  ci:
    uses: Viero-Tech/.github/.github/workflows/reusable-ci-nestjs.yml@main
```

The caller job must be named `ci`. Each CI workflow ends with a `ci-summary` job, and branch rulesets require the `ci / ci-summary` status check.

| Workflow | Jobs | Inputs (default) |
|---|---|---|
| `reusable-ci-nestjs.yml` | lint, typecheck, test, ci-summary | `node-version` (22), `pnpm-version` (9), `submodules` (false), `prisma-generate` (false). Secret `ssh-key` for submodule checkout. |
| `reusable-ci-nextjs.yml` | lint, typecheck, test, ci-summary | `node-version` (22), `pnpm-version` (9) |
| `reusable-ci-prisma.yml` | validate, ci-summary | `node-version` (22) |
| `reusable-ci-flutter.yml` | analyze, test, ci-summary | `flutter-version` (3.8.1) |
| `reusable-ci-python.yml` | lint, test, ci-summary | `python-version` (3.10) |
| `reusable-ci-generic.yml` | lint, typecheck, ci-summary | `node-version` (22) |
| `reusable-claude-review.yml` | review | `aws_role_arn` (required), `aws_region`, `bedrock_model_id`, `extra_prompt`, `skip_drafts` (true), `use_sticky_comment` (true), `claude_args_extra` |
| `reusable-claude-mention.yml` | claude | `aws_role_arn` (required), `aws_region`, `bedrock_model_id`, `extra_prompt`, `claude_args_extra` |

### Notes

- If a repository pins `packageManager` in `package.json`, pass `pnpm-version: ''` so the pinned version is used. Specifying both causes `pnpm/action-setup` to fail with "Multiple versions of pnpm specified".
- The Claude workflows review pull requests and respond to `@claude` mentions. They authenticate to Amazon Bedrock through GitHub OIDC using a role ARN and region supplied by the calling repository; no long-lived credentials are stored.

## Contributing

All callers reference these workflows at `@main`, so a change here takes effect in every repository on its next run. Submit changes through a pull request. The `protect-main` ruleset requires two approvals including a devops code-owner review.
