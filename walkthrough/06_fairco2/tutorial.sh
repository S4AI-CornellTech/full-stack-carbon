#!/usr/bin/env bash
# Segment 6 - Fair-CO2 tutorial runner (see TUTORIAL.md). Wraps tutorial.py in the fair-co2 env.
# Does not touch the canonical demo (run.sh); the Fair-CO2 submodule is only ever read.
#   ./tutorial.sh --workloads exercises/workloads.json
#   ./tutorial.sh --swing llama
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/env.sh
source "$HERE/../lib/env.sh"
PY="$(tool_py fair-co2)"
exec "$PY" "$HERE/tutorial.py" "$@"
