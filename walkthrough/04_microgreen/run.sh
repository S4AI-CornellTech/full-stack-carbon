#!/usr/bin/env bash
# Segment 4 - MicroGreen: the carbon-optimal edge MCU is NOT fixed - it flips.
#
#   ./run.sh            run MicroGreen's carbon sweep (~1 min) + compute the flip
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
