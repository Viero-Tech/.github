#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./deploy-claude-reviewer.sh                  # deploy to all in-scope repos
#   ./deploy-claude-reviewer.sh <repo-name>      # deploy to one repo
#   ./deploy-claude-reviewer.sh --dry-run        # print what would change, no git ops
#   ./deploy-claude-reviewer.sh --no-claude-md   # workflows only (skip CLAUDE.md)
#
# Deploys per-repo Claude reviewer config:
#   - .github/workflows/claude-review.yml   (auto-review caller stub)
#   - .github/workflows/claude-mention.yml  (@claude mention caller stub)
#   - CLAUDE.md                             (per-stack template, skip if exists)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
MAPPING="$SCRIPT_DIR/repo-mapping.json"
ORG="Viero-Tech"
BRANCH="chore/claude-reviewer"

DRY_RUN=0
NO_CLAUDE_MD=0
SINGLE_REPO=""

# Parse flags and a possible single-repo positional
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --no-claude-md) NO_CLAUDE_MD=1 ;;
    -*) echo "ERROR: unknown flag $arg" >&2; exit 2 ;;
    *)
      if [ -z "$SINGLE_REPO" ]; then SINGLE_REPO="$arg"
      else echo "ERROR: multiple repo args" >&2; exit 2; fi
      ;;
  esac
done

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

dry() {
  if [ "$DRY_RUN" = "1" ]; then echo "  [dry-run] $*"; else "$@"; fi
}

deploy_repo() {
  local repo=$1
  local short_category=$2 # nestjs, nextjs, flutter, prisma, python, generic
  local template_name

  case "$short_category" in
    nestjs) template_name="nestjs-backend.md" ;;
    nextjs) template_name="nextjs-frontend.md" ;;
    prisma) template_name="prisma-schema.md" ;;
    flutter) template_name="flutter-app.md" ;;
    python) template_name="python-ai.md" ;;
    generic) template_name="generic.md" ;;
    *) echo "ERROR: unknown stack '$short_category' for $repo"; return 1 ;;
  esac

  echo "=== $repo (stack: $short_category, template: $template_name) ==="

  if [ "$DRY_RUN" = "1" ]; then
    echo "  [dry-run] would copy per-repo-workflows/claude-review.yml -> .github/workflows/claude-review.yml"
    echo "  [dry-run] would copy per-repo-workflows/claude-mention.yml -> .github/workflows/claude-mention.yml"
    if [ "$NO_CLAUDE_MD" = "0" ]; then
      echo "  [dry-run] would copy claude-md-templates/$template_name -> CLAUDE.md (only if no existing CLAUDE.md)"
    fi
    echo "  [dry-run] would commit + push + open PR on $ORG/$repo (base: dev)"
    return 0
  fi

  cd "$WORK_DIR"
  rm -rf "$repo"

  # Try dev first, fall back to main
  local base_branch=""
  if gh repo clone "$ORG/$repo" "$repo" -- --depth 1 -b dev 2>/dev/null; then
    base_branch="dev"
  elif gh repo clone "$ORG/$repo" "$repo" -- --depth 1 -b main 2>/dev/null; then
    base_branch="main"
  else
    echo "WARN: Could not clone $repo on dev or main. Skipping."
    return 0
  fi

  cd "$repo"
  git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"

  mkdir -p .github/workflows

  cp "$ROOT_DIR/per-repo-workflows/claude-review.yml"  .github/workflows/claude-review.yml
  cp "$ROOT_DIR/per-repo-workflows/claude-mention.yml" .github/workflows/claude-mention.yml

  if [ "$NO_CLAUDE_MD" = "0" ]; then
    if [ -e CLAUDE.md ]; then
      echo "  CLAUDE.md already exists, leaving as-is"
    else
      cp "$ROOT_DIR/claude-md-templates/$template_name" CLAUDE.md
      echo "  CLAUDE.md created from $template_name"
    fi
  fi

  git add .github/workflows/claude-review.yml .github/workflows/claude-mention.yml CLAUDE.md 2>/dev/null || true
  if git diff --cached --quiet; then
    echo "  No changes for $repo. Skipping."
    cd "$WORK_DIR" && rm -rf "$repo"
    return 0
  fi

  git -c commit.gpgsign=false -c core.hooksPath=/dev/null \
      commit -m "chore: add claude reviewer caller stubs and per-stack CLAUDE.md"
  git push -u origin "$BRANCH" 2>&1 | tail -5

  gh pr create \
    --repo "$ORG/$repo" \
    --base "$base_branch" \
    --head "$BRANCH" \
    --title "chore: add claude reviewer (org-wide rollout)" \
    --body "Adds the Claude Code Reviewer to this repo as part of the org-wide rollout.

**Files:**
- \`.github/workflows/claude-review.yml\`: auto-review on PR open / push / reopen / ready-for-review (calls \`reusable-claude-review.yml\` in \`Viero-Tech/.github\`)
- \`.github/workflows/claude-mention.yml\`: respond to \`@claude\` mentions in PR comments / reviews / issues
$([ "$NO_CLAUDE_MD" = "0" ] && echo "- \`CLAUDE.md\`: per-stack code-review conventions (template: \`$template_name\`)")

**Auth:** AWS Bedrock via OIDC. Org vars \`AWS_BEDROCK_ROLE_ARN\` + \`AWS_BEDROCK_REGION\` resolve at workflow runtime; the IAM role's trust policy is scoped to \`repo:Viero-Tech/*\`.

**No code changes.** Pure config addition. CI on this PR should pass; the new \`Claude Code Review\` workflow will fire on subsequent pushes." 2>&1 | tail -3

  echo "  PR created"
  cd "$WORK_DIR" && rm -rf "$repo"
}

if [ -n "$SINGLE_REPO" ]; then
  RESULT=$(python3 -c "
import json, sys
m = json.load(open('$MAPPING'))
for cat, repos in m.items():
  if cat == 'skip': continue
  if '$SINGLE_REPO' in repos:
    print(cat); sys.exit(0)
print('NOT_FOUND')
")
  if [ "$RESULT" = "NOT_FOUND" ]; then
    echo "ERROR: Repo $SINGLE_REPO not found in mapping (or in skip list)."
    exit 1
  fi
  deploy_repo "$SINGLE_REPO" "$RESULT"
else
  python3 -c "
import json
m = json.load(open('$MAPPING'))
for cat, repos in m.items():
  if cat == 'skip': continue
  for repo in repos:
    print(f'{repo} {cat}')
" | while read repo short_category; do
    deploy_repo "$repo" "$short_category" || echo "  FAILED: $repo, continuing"
  done
fi

echo "Done."
