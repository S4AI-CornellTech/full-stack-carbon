#!/usr/bin/env bash
# Segment 2 - COFFEE: embodied carbon of emerging FeFET (HZO) on-chip memory.
#
#   ./run.sh            recompute from COFFEE + its committed FeFET/CMOS archs
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
