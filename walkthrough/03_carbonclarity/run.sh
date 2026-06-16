#!/usr/bin/env bash
# Segment 3 - CarbonClarity: fab-uncertainty band around the R740 CPU die's embodied carbon.
#
#   ./run.sh            recompute the CPA distribution from committed input distributions
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
