#!/usr/bin/env bash
# Create isolated per-tool Python environments for the full-stack-carbon suite.
#
# The six tools carry mutually incompatible pins (numpy 2.3.4 / 2.3.5 / 2.4.3,
# Python 3.11 vs 3.12), so a single shared environment is impossible. Each tool
# therefore gets its own venv under .envs/<tool>/.
#
# By default we install only what each tool's hands-on tutorial needs. The heavy,
# optional pieces (MicroGreen's on-device hardware + Streamlit stack, Fair-CO2's
# demand-forecasting path) are gated behind FULL=1.
#
# Usage:
#   scripts/bootstrap.sh                 # build every tool's env (tutorial deps)
#   scripts/bootstrap.sh act eserve      # build only the named tools
#   FULL=1 scripts/bootstrap.sh          # also install heavy/optional extras
#
# Self-contained: prefers a system `uv`; else uses python3.x already on PATH; and if a
# needed interpreter is missing, provisions a repo-local `uv` under .uv/ (its binary,
# managed Pythons, and cache all stay inside the repo — nothing is installed machine-wide).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UV_DIR="$ROOT/.uv"
UV="$(command -v uv || true)"
# Reuse a repo-local uv from a previous run (and keep its Pythons + cache in-repo).
if [ -z "$UV" ] && [ -x "$UV_DIR/venv/bin/uv" ]; then
  UV="$UV_DIR/venv/bin/uv"
  export UV_PYTHON_INSTALL_DIR="$UV_DIR/python" UV_CACHE_DIR="$UV_DIR/cache"
fi
TOOLS=("$@")

ensure_local_uv() {  # install a repo-local uv (once) when a needed Python is missing; sets $UV
  [ -n "$UV" ] && return 0
  echo "  no uv and 'python$1' not on PATH — installing a repo-local uv under .uv/ (nothing machine-wide)"
  local pyboot; pyboot="$(command -v python3 || command -v python || true)"
  [ -z "$pyboot" ] && { echo "  ERROR: need python3 (or uv) to bootstrap; install either and re-run." >&2; exit 1; }
  mkdir -p "$UV_DIR"
  "$pyboot" -m venv "$UV_DIR/venv" >/dev/null 2>&1 \
    || { echo "  ERROR: could not create $UV_DIR/venv with '$pyboot'." >&2; exit 1; }
  "$UV_DIR/venv/bin/python" -m pip install --quiet --disable-pip-version-check uv \
    || { echo "  ERROR: could not pip-install uv (offline?). Install uv, or put python3.11 + python3.12 on PATH." >&2; exit 1; }
  UV="$UV_DIR/venv/bin/uv"
  export UV_PYTHON_INSTALL_DIR="$UV_DIR/python" UV_CACHE_DIR="$UV_DIR/cache"
  echo "  repo-local uv ready ($("$UV" --version 2>/dev/null))"
}

want() {  # want <tool> -> success if it should be built (no args = all)
  [ "${#TOOLS[@]}" -eq 0 ] && return 0
  local t; for t in "${TOOLS[@]}"; do [ "$t" = "$1" ] && return 0; done
  return 1
}

mkenv() {  # mkenv <name> <python-version>
  local d="$ROOT/.envs/$1"
  if [ -d "$d" ]; then echo "  env '$1' exists, reusing"; return 0; fi
  echo "  creating env '$1' (python $2)"
  # No uv and the exact interpreter isn't on PATH → provision a repo-local uv to supply it.
  if [ -z "$UV" ] && ! command -v "python$2" >/dev/null 2>&1; then ensure_local_uv "$2"; fi
  if [ -n "$UV" ]; then "$UV" venv --python "$2" "$d" >/dev/null
  else "python$2" -m venv "$d"; fi
}

pipin() {  # pipin <name> <pip-args...>
  if [ -n "$UV" ]; then "$UV" pip install --quiet --python "$ROOT/.envs/$1/bin/python" "${@:2}"
  else "$ROOT/.envs/$1/bin/python" -m pip install --quiet "${@:2}"; fi
}

echo "full-stack-carbon: bootstrapping envs under $ROOT/.envs"
if [ -n "$UV" ]; then echo "using uv ($("$UV" --version 2>/dev/null))"
else echo "no system uv — will use python3.x on PATH, fetching a repo-local uv into .uv/ only if a version is missing"; fi

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
