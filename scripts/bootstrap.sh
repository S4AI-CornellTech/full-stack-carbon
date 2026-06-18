#!/usr/bin/env bash
# Create isolated per-tool Python environments for the full-stack-carbon suite.
#
# The six tools carry mutually incompatible pins (numpy 2.3.4 / 2.3.5 / 2.4.3,
# Python 3.11 vs 3.12), so a single shared environment is impossible. Each tool
# therefore gets its own venv under .envs/<tool>/.
#
# By default we install only what each tool's WALKTHROUGH demo needs. The heavy,
# optional pieces (MicroGreen's on-device hardware + Streamlit stack, Fair-CO2's
# demand-forecasting path) are gated behind FULL=1.
#
# Usage:
#   scripts/bootstrap.sh                 # build every tool's env (walkthrough deps)
#   scripts/bootstrap.sh act eserve      # build only the named tools
#   FULL=1 scripts/bootstrap.sh          # also install heavy/optional extras
#
# Prefers `uv` (fast, can fetch pinned interpreters); falls back to python -m venv.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UV="$(command -v uv || true)"
TOOLS=("$@")

want() {  # want <tool> -> success if it should be built (no args = all)
  [ "${#TOOLS[@]}" -eq 0 ] && return 0
  local t; for t in "${TOOLS[@]}"; do [ "$t" = "$1" ] && return 0; done
  return 1
}

mkenv() {  # mkenv <name> <python-version>
  local d="$ROOT/.envs/$1"
  if [ -d "$d" ]; then echo "  env '$1' exists, reusing"; return 0; fi
  echo "  creating env '$1' (python $2)"
  if [ -n "$UV" ]; then "$UV" venv --python "$2" "$d" >/dev/null
  else "python$2" -m venv "$d"; fi
}

pipin() {  # pipin <name> <pip-args...>
  if [ -n "$UV" ]; then "$UV" pip install --quiet --python "$ROOT/.envs/$1/bin/python" "${@:2}"
  else "$ROOT/.envs/$1/bin/python" -m pip install --quiet "${@:2}"; fi
}

echo "full-stack-carbon: bootstrapping envs under $ROOT/.envs"
[ -n "$UV" ] && echo "using uv ($("$UV" --version))" || echo "uv not found; using python -m venv"

if want act;           then echo "[act]";           mkenv act 3.12;           pipin act pyyaml pint matplotlib; fi
if want coffee;        then echo "[coffee]";        mkenv coffee 3.12;        pipin coffee -r "$ROOT/COFFEE/requirements.txt" matplotlib; fi
if want carbonclarity; then echo "[carbonclarity]"; mkenv carbonclarity 3.11; pipin carbonclarity -r "$ROOT/CarbonClarity/requirements.txt"; fi
if want eserve;        then echo "[eserve]";        mkenv eserve 3.12;        pipin eserve -e "$ROOT/EServe" -e "$ROOT/ACT" matplotlib; fi
if want microgreen;    then echo "[microgreen]";    mkenv microgreen 3.11;    pipin microgreen -e "$ROOT/ACT" numpy==2.4.3 pandas==2.3.3 matplotlib==3.10.8; fi
if want fair-co2;      then echo "[fair-co2]";      mkenv fair-co2 3.12;      pipin fair-co2 matplotlib seaborn numpy pandas scipy; fi

if [ "${FULL:-0}" = "1" ]; then
  echo "FULL=1: installing heavy/optional extras"
  if want microgreen; then
    # MicroGreen's complete hardware + Streamlit stack, minus macOS-only pyobjc (breaks on Linux).
    tmp="$(mktemp)"; grep -v '^pyobjc' "$ROOT/MicroGreen/requirements.txt" > "$tmp"
    pipin microgreen -r "$tmp"; rm -f "$tmp"
  fi
  if want fair-co2; then
    # Demand-forecasting path: Prophet needs a C++ toolchain/cmdstan; datasets pulls HuggingFace.
    pipin fair-co2 prophet datasets
  fi
fi

echo "done. Activate a tool with:  source .envs/<tool>/bin/activate"
