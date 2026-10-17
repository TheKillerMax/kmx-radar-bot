#!/usr/bin/env bash
# Commit has already been created. Push without force and recover a narrow
# non-fast-forward race with external GitHub writers. Never bypass branch rules.
set -euo pipefail

for attempt in 1 2 3 4; do
  if output="$(git push origin HEAD:main 2>&1)"; then
    printf '%s\n' "$output"
    exit 0
  fi
  printf '%s\n' "$output" >&2

  if grep -Eqi 'GH006|GH013|protected branch|repository rule|permission denied|403|authentication failed' <<< "$output"; then
    echo "Repository authorization/rules rejected push; never bypassing protection." >&2
    exit 1
  fi
  if ! grep -Eqi 'non-fast-forward|fetch first|failed to push some refs|stale info' <<< "$output"; then
    echo "Push failed for a reason other than a known race; not retrying." >&2
    exit 1
  fi
  if (( attempt == 4 )); then
    echo "Push failed after bounded retry; preserving remote main unchanged." >&2
    exit 1
  fi
  echo "Remote main advanced; rebasing only the unpublished local commit." >&2
  git fetch origin main
  if ! git rebase origin/main; then
    git rebase --abort || true
    echo "Rebase conflict: stopped safely. Recovery must reconcile this change." >&2
    exit 1
  fi
  sleep "$attempt"
done
