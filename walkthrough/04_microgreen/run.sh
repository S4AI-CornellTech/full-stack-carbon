#!/usr/bin/env bash
# Segment 4 - MicroGreen: embodied carbon of edge MCU boards (a side-branch).
#
#   ./run.sh            recompute from MicroGreen's committed board_carbon.csv
#   ./run.sh --golden   restore the committed golden figures/result (zero compute)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/env.sh
source "$HERE/../lib/env.sh"

PY="$(tool_py microgreen)"
mkdir -p "$HERE/figures"

if [ "${1:-}" = "--golden" ]; then
  exec "$PY" "$HERE/recompute.py" --golden
fi
exec "$PY" "$HERE/recompute.py"
