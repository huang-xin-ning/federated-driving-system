#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$project_root/src${PYTHONPATH:+:$PYTHONPATH}"
"$project_root/.venv/bin/python" -m unittest discover -s "$project_root/tests" -v
