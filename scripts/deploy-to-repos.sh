#\!/usr/bin/env bash
set -euo pipefail

# Usage: ./deploy-to-repos.sh [repo-name]
# If repo-name is given, deploy to that repo only. Otherwise deploy to all.
#
# Deploys per-repo standard config:
#   - .github/workflows/ci.yml  (CI caller workflow)
#   - CODEOWNERS                (org-wide reviewer policy)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
MAPPING="$SCRIPT_DIR/repo-mapping.json"
ORG="Viero-Tech"
BRANCH="chore/standard-config"
SINGLE_REPO="${1:-}"
WORK_DIR=$(mktemp -d)

trap 'rm -rf "$WORK_DIR"' EXIT

deploy_repo() {
  local repo=$1
  local short_category=$2 # nestjs, nextjs, flutter, prisma, python, generic

  echo "=== Deploying to $repo (stack: $short_category) ==="

  cd "$WORK_DIR"
  gh repo clone "$ORG/$repo" "$repo" -- --depth 1 -b dev 2>/dev/null || {
    echo "WARN: Could not clone $repo (no dev branch?). Skipping."
    return 0
  }
  cd "$repo"

  git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"

  mkdir -p .github/workflows

  # CI caller workflow (calls reusable workflow from .github org repo)
  cp "$ROOT_DIR/per-repo-workflows/ci-${short_category}.yml" \
     .github/workflows/ci.yml

  # CODEOWNERS at repo root
  cp "$ROOT_DIR/CODEOWNERS-template" CODEOWNERS

  git add .github/ CODEOWNERS
  if git diff --cached --quiet; then
    echo "No changes for $repo. Skipping."
    cd "$WORK_DIR" && rm -rf "$repo"
    return 0
  fi

  git commit -m "chore: add CI workflow and CODEOWNERS"
  git push -u origin "$BRANCH"

  gh pr create \
    --repo "$ORG/$repo" \
    --base dev \
    --head "$BRANCH" \
    --title "chore: add CI pipeline and CODEOWNERS" \
    --body "Adds:
- CI workflow (calls reusable workflow from .github org repo)
- CODEOWNERS (requires code-reviewers team approval)"

  echo "PR created for $repo"
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
    deploy_repo "$repo" "$short_category"
  done
fi

echo "Done\!"
