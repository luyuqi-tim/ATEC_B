#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/experiments/mink_wholebody/runtime.sh"
cd "$ROOT"
exec /usr/bin/python3 -u "$ROOT/experiments/mink_wholebody/supervise.py" "$@"
