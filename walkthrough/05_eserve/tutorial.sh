#!/usr/bin/env bash
# Segment 5 - EServe tutorial runner (see TUTORIAL.md). Wraps tutorial.py in the eserve env.
# Does not touch the canonical demo (run.sh) or its golden/handoff.
#   ./tutorial.sh --gpu H100HGX --host
#   ./tutorial.sh --gpu-file exercises/gpu_l4.json --host --grid-ci 30 --util 0.5
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/env.sh
source "$HERE/../lib/env.sh"
PY="$(tool_py eserve)"
exec "$PY" "$HERE/tutorial.py" "$@"
