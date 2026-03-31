#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAPPING="$SCRIPT_DIR/repo-mapping.json"
ORG="Viero-Tech"
BRANCH="chore/remove-copilot-config"
WORK_DIR=$(mktemp -d)

trap 'rm -rf "$WORK_DIR"' EXIT

python3 -c "
import json
m = json.load(open('$MAPPING'))
for cat, repos in m.items():
  if cat == 'skip': continue
  for repo in repos: print(repo)
" | while read repo; do
  echo "=== Rolling back $repo ==="
  cd "$WORK_DIR"
  gh repo clone "$ORG/$repo" "$repo" -- --depth 1 -b dev 2>/dev/null || continue
  cd "$repo"
  git checkout -b "$BRANCH"

  rm -f .github/instructions/code-review.instructions.md
  rm -f .github/instructions/*.instructions.md
  rm -f .github/workflows/ci.yml
  rm -f .github/workflows/copilot-setup-steps.yml
  rm -f CODEOWNERS

  git add -A
  if git diff --cached --quiet; then
    echo "Nothing to rollback for $repo"
    cd "$WORK_DIR" && rm -rf "$repo"
    continue
  fi

  git commit -m "chore: remove Copilot review config and CI workflow"
  git push -u origin "$BRANCH"
  gh pr create --repo "$ORG/$repo" --base dev --head "$BRANCH" \
    --title "chore: rollback Copilot code review config" \
    --body "Removes Copilot review instructions, CI workflow, setup steps, and CODEOWNERS."

  cd "$WORK_DIR" && rm -rf "$repo"
done

echo "Rollback PRs created."
