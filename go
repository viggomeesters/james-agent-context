#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK="${GO_STACK:-}"
if [ -z "$STACK" ] || [ ! -f "$STACK/cli/go.py" ]; then
  for candidate in "$REPO_ROOT/../go-workflow-stack" "$HOME/github/go-workflow-stack" "$HOME/Dev/go-workflow-stack"; do
    if [ -f "$candidate/cli/go.py" ]; then STACK="$candidate"; break; fi
  done
fi
if [ -z "$STACK" ] || [ ! -f "$STACK/cli/go.py" ]; then
  echo "go-workflow-stack not found; set GO_STACK or clone it beside this repository" >&2
  exit 2
fi
export GO_STACK="$STACK"
exec python3 "$STACK/cli/go.py" "$@"
