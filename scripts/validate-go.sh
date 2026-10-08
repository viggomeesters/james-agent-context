#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

"${PYTHON:-python3}" - "$REPO_ROOT" <<'PY'
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
project = json.loads((root / ".go" / "project.json").read_text(encoding="utf-8"))
version = project["required_stack_version"]
stack_ref = project["stack_ref"]
assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version)
assert stack_ref == f"v{version}"
assert (root / "go").is_file()
assert (root / "scripts" / "bootstrap-stack.sh").is_file()
PY

STACK="$(bash "$REPO_ROOT/scripts/bootstrap-stack.sh")"
EXPECTED_REF="$("${PYTHON:-python3}" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["stack_ref"])' "$REPO_ROOT/.go/project.json")"
EXPECTED_REMOTE="https://github.com/viggomeesters/go-workflow-stack.git"

[ "$(git -C "$STACK" remote get-url origin)" = "$EXPECTED_REMOTE" ]
[ "$(git -C "$STACK" cat-file -t "refs/tags/$EXPECTED_REF")" = "tag" ]
[ "$(git -C "$STACK" rev-parse HEAD)" = "$(git -C "$STACK" rev-parse "refs/tags/$EXPECTED_REF^{commit}")" ]

exec "$REPO_ROOT/go" validate "$REPO_ROOT"