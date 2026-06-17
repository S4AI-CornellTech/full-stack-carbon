#!/usr/bin/env bash
# Segment 2 - CarbonClarity: embodied carbon is a distribution, not a point.
# Sweeps 28/10/7 nm logic nodes; per cm2 reports mean (= ACT plug-in), 95th pct,
# p95/mean and P(actual > mean) from CarbonClarity's fab-uncertainty model.
#
#   ./run.sh            recompute the CPA distributions from committed input distributions
#   ./run.sh --golden   restore the committed golden figures/result (zero compute)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/env.sh
source "$HERE/../lib/env.sh"

PY="$(tool_py carbonclarity)"
mkdir -p "$HERE/figures"

if [ "${1:-}" = "--golden" ]; then
  exec "$PY" "$HERE/recompute.py" --golden
fi
exec "$PY" "$HERE/recompute.py"
