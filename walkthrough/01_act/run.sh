#!/usr/bin/env bash
# Segment 1 - ACT: embodied + operational carbon of the Dell PowerEdge R740 from its BOM.
#
#   ./run.sh            recompute from ACT + the committed dellr740 BOM
#   ./run.sh --golden   restore the committed golden figures/result (zero compute)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/env.sh
source "$HERE/../lib/env.sh"

PY="$(tool_py act)"
mkdir -p "$HERE/figures"

if [ "${1:-}" = "--golden" ]; then
  exec "$PY" "$HERE/recompute.py" --golden
fi

echo "[01_act] running ACT on act/boms/dellr740.yaml ..."
( cd "$SUITE_ROOT/ACT" \
    && PYTHONPATH="$SUITE_ROOT/ACT" "$PY" -m act.act_model \
         -m act/boms/dellr740.yaml -o "$HERE/figures" )
exec "$PY" "$HERE/recompute.py"
