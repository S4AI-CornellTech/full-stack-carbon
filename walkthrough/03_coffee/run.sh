#!/usr/bin/env bash
# Segment 3 - COFFEE: the FeFET (HZO) memory-technology trade-off (density inversion).
#
#   ./run.sh            recompute from COFFEE + its committed FeFET/CMOS archs + nvm_areas.csv
#   ./run.sh --golden   restore the committed golden figures/result (zero compute)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/env.sh
source "$HERE/../lib/env.sh"

PY="$(tool_py coffee)"
mkdir -p "$HERE/figures"

if [ "${1:-}" = "--golden" ]; then
  exec "$PY" "$HERE/recompute.py" --golden
fi
exec "$PY" "$HERE/recompute.py"
