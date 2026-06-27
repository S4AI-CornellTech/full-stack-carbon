#!/usr/bin/env bash
# Segment 1 - ACT tutorial: run ANY bill-of-materials through the real act_model CLI.
# This is the participant-facing runner for the hands-on tutorial (see TUTORIAL.md).
# It does not touch the canonical demo (run.sh) or its golden/handoff.
#
#   ./tutorial.sh <bom.yaml>                 run a tutorial BOM, print its carbon report
#   ./tutorial.sh <bom.yaml> --expect <kg>   also assert total_carbon ~= <kg> (used by CI)
#
# <bom.yaml> is resolved relative to this segment directory if it is not absolute,
# e.g.:  ./tutorial.sh exercises/sensitivity.yaml
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/env.sh
source "$HERE/../lib/env.sh"

BOM="${1:?usage: tutorial.sh <bom.yaml> [--expect <kg>]}"
case "$BOM" in /*) : ;; *) BOM="$HERE/$BOM" ;; esac
[ -f "$BOM" ] || { echo "ERROR: BOM not found: $BOM" >&2; exit 1; }

EXPECT=""
if [ "${2:-}" = "--expect" ]; then EXPECT="${3:?--expect needs a number}"; fi

PY="$(tool_py act)"
OUT="$HERE/figures/tutorial"
mkdir -p "$OUT"

echo "[01_act tutorial] $(basename "$BOM")"
( cd "$SUITE_ROOT/ACT" \
    && PYTHONPATH="$SUITE_ROOT/ACT" "$PY" -m act.act_model -m "$BOM" -o "$OUT" >/dev/null )

REPORT="$OUT/act_report.yaml"
echo "  $(grep -E '^total_carbon:' "$REPORT")"
grep -A12 '^result_by_category:' "$REPORT" | sed 's/^/  /'

if [ -n "$EXPECT" ]; then
  total="$(grep -E '^total_carbon:' "$REPORT" | grep -oE '[0-9]+\.?[0-9]*' | head -1)"
  awk -v g="$total" -v e="$EXPECT" \
    'BEGIN{d=(g>e?g-e:e-g); tol=(0.05>0.001*e?0.05:0.001*e); exit(d<=tol?0:1)}' \
    && echo "  OK: total ~= $EXPECT kg" \
    || { echo "  FAIL: total $total != expected $EXPECT kg" >&2; exit 1; }
fi
