#!/usr/bin/env bash
set -euo pipefail
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/public_boundary.py
