#!/usr/bin/env bash
set -euo pipefail

# Resolve only the repository's immutable go-workflow-stack runtime. A project
# launcher must never fall back to a mutable neighbouring checkout.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_FILE="$REPO_ROOT/.go/project.json"
STACK_REMOTE="https://github.com/viggomeesters/go-workflow-stack.git"

for forbidden_override in GO_STACK GO_STACK_REF GO_STACK_REMOTE GO_STACK_ALLOW_DEV; do
  if [ -n "${!forbidden_override:-}" ]; then
    echo "$forbidden_override cannot override this repository's immutable stack runtime" >&2
    exit 5
  fi
done

read_project_field() {
  "${PYTHON:-python3}" - "$PROJECT_FILE" "$1" <<'PY'
import json
import sys

project = json.load(open(sys.argv[1], encoding="utf-8"))
print(project[sys.argv[2]])
PY
}

STACK_VERSION="$(read_project_field required_stack_version)"
STACK_REF="$(read_project_field stack_ref)"
if [[ ! "$STACK_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || [ "$STACK_REF" != "v$STACK_VERSION" ]; then
  echo ".go/project.json must pin a release version and matching immutable tag" >&2
  exit 4
fi

STACK="${XDG_CACHE_HOME:-${HOME:?HOME is required}/.cache}/go-workflow-stack/$STACK_REF"

runtime_matches() {
  local checkout="$1" tagged_commit head
  [ "$(git -C "$checkout" remote get-url origin 2>/dev/null || true)" = "$STACK_REMOTE" ] || return 1
  [ "$(git -C "$checkout" cat-file -t "refs/tags/$STACK_REF" 2>/dev/null || true)" = "tag" ] || return 1
  tagged_commit="$(git -C "$checkout" rev-parse -q --verify "refs/tags/$STACK_REF^{commit}" 2>/dev/null || true)"
  head="$(git -C "$checkout" rev-parse HEAD 2>/dev/null || true)"
  [ -n "$tagged_commit" ] && [ "$head" = "$tagged_commit" ]
}

valid_checkout() {
  [ -e "$STACK/.git" ] && [ "$(git -C "$STACK" rev-parse --is-inside-work-tree 2>/dev/null || true)" = "true" ]
}

if ! valid_checkout; then
  mkdir -p "$(dirname "$STACK")"
  git clone --branch "$STACK_REF" --depth 1 "$STACK_REMOTE" "$STACK"
elif [ -n "$(git -C "$STACK" status --porcelain)" ]; then
  echo "pinned go-workflow-stack cache is dirty: $STACK" >&2
  exit 3
elif ! runtime_matches "$STACK"; then
  echo "existing stack cache origin/tag/HEAD mismatch; refusing automatic cache repair" >&2
  exit 4
fi

if [ ! -f "$STACK/cli/go.py" ] || ! runtime_matches "$STACK"; then
  echo "pinned go-workflow-stack runtime does not match $STACK_REMOTE at $STACK_REF" >&2
  exit 4
fi

printf '%s\n' "$STACK"