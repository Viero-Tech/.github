#!/usr/bin/env bash
set -euo pipefail

# Usage: ./deploy-to-repos.sh [repo-name]
# If repo-name is given, deploy to that repo only. Otherwise deploy to all.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
MAPPING="$SCRIPT_DIR/repo-mapping.json"
ORG="Viero-Tech"
BRANCH="chore/copilot-config"
TIMESTAMP=$(date +%Y-%m-%d)
SINGLE_REPO="${1:-}"
WORK_DIR=$(mktemp -d)

trap 'rm -rf "$WORK_DIR"' EXIT

deploy_repo() {
  local repo=$1
  local category=$2      # long name: nestjs-backend, nextjs-frontend, etc.
  local short_category=$3 # short name: nestjs, nextjs, etc.

  echo "=== Deploying to $repo (category: $category, short: $short_category) ==="

  cd "$WORK_DIR"
  gh repo clone "$ORG/$repo" "$repo" -- --depth 1 -b dev 2>/dev/null || {
    echo "WARN: Could not clone $repo (no dev branch?). Skipping."
    return 0
  }
  cd "$repo"

  # Create branch
  git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"

  # Create directories
  mkdir -p .github/instructions .github/workflows

  # Copy instruction files
  cp "$ROOT_DIR/review-instructions/code-review.instructions.md" \
     .github/instructions/code-review.instructions.md
  cp "$ROOT_DIR/copilot-instructions/${category}.instructions.md" \
     ".github/instructions/${category}.instructions.md"

  # Copy CI caller workflow (uses short category name)
  cp "$ROOT_DIR/per-repo-workflows/ci-${short_category}.yml" \
     .github/workflows/ci.yml

  # Copy Copilot setup steps (uses short category name)
  cp "$ROOT_DIR/copilot-setup-steps/${short_category}.yml" \
     .github/workflows/copilot-setup-steps.yml

  # Copy CODEOWNERS to repo root
  cp "$ROOT_DIR/CODEOWNERS-template" CODEOWNERS

  # Commit and push
  git add .github/ CODEOWNERS
  if git diff --cached --quiet; then
    echo "No changes for $repo. Skipping."
    cd "$WORK_DIR"
    rm -rf "$repo"
    return 0
  fi

  git commit -m "chore: add Copilot review config and CI workflow"
  git push -u origin "$BRANCH"

  # Create PR
  gh pr create \
    --repo "$ORG/$repo" \
    --base dev \
    --head "$BRANCH" \
    --title "chore: add Copilot code review and CI pipeline" \
    --body "Adds:
- Copilot review instructions (stack-specific + shared review behavior)
- CI workflow (calls reusable workflow from .github org repo)
- Copilot setup steps (enables agentic review mode)
- CODEOWNERS (requires code-reviewers team approval)

Part of org-wide Copilot Code Review rollout."

  echo "PR created for $repo"
  cd "$WORK_DIR"
  rm -rf "$repo"
}

# Parse mapping and deploy
if [ -n "$SINGLE_REPO" ]; then
  RESULT=$(python3 -c "
import json, sys
m = json.load(open('$MAPPING'))
mapping = {'nestjs': 'nestjs-backend', 'nextjs': 'nextjs-frontend', 'flutter': 'flutter-app', 'prisma': 'prisma-schema', 'python': 'python-ai', 'generic': 'generic'}
for cat, repos in m.items():
  if cat == 'skip': continue
  if '$SINGLE_REPO' in repos:
    print(f'{mapping.get(cat, cat)} {cat}')
    sys.exit(0)
print('NOT_FOUND')
")
  if [ "$RESULT" = "NOT_FOUND" ]; then
    echo "ERROR: Repo $SINGLE_REPO not found in mapping (or in skip list)."
    exit 1
  fi
  read CATEGORY SHORT_CATEGORY <<< "$RESULT"
  deploy_repo "$SINGLE_REPO" "$CATEGORY" "$SHORT_CATEGORY"
else
  python3 -c "
import json
m = json.load(open('$MAPPING'))
mapping = {'nestjs': 'nestjs-backend', 'nextjs': 'nextjs-frontend', 'flutter': 'flutter-app', 'prisma': 'prisma-schema', 'python': 'python-ai', 'generic': 'generic'}
for cat, repos in m.items():
  if cat == 'skip': continue
  for repo in repos:
    print(f'{repo} {mapping.get(cat, cat)} {cat}')
" | while read repo category short_category; do
    deploy_repo "$repo" "$category" "$short_category"
  done
fi

echo "Done!"
