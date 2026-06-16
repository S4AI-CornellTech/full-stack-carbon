#!/usr/bin/env bash
# Segment 6 - Fair-CO2: fairly attribute the server's embodied carbon to co-located jobs.
#
#   ./run.sh            AE recompute from Fair-CO2's committed colocation matrices
#   ./run.sh --golden   restore the committed golden figures/result (zero compute)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/env.sh
source "$HERE/../lib/env.sh"

PY="$(tool_py fair-co2)"
mkdir -p "$HERE/figures"

if [ "${1:-}" = "--golden" ]; then
  exec "$PY" "$HERE/recompute.py" --golden
fi
exec "$PY" "$HERE/recompute.py"
