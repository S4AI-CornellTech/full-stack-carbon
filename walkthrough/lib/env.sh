# Sourced by each walkthrough segment's run.sh.
# Exposes SUITE_ROOT and a helper to locate a tool's isolated interpreter.
WALK_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALK_ROOT="$(dirname "$WALK_LIB_DIR")"
SUITE_ROOT="$(dirname "$WALK_ROOT")"
ENVS_DIR="$SUITE_ROOT/.envs"

tool_py() {  # tool_py <tool> -> absolute path to that tool's venv python
  local py="$ENVS_DIR/$1/bin/python"
  if [ ! -x "$py" ]; then
    echo "ERROR: env '$1' not found at $py — run: scripts/bootstrap.sh $1" >&2
    return 1
  fi
  echo "$py"
}

export MPLBACKEND=Agg
export PYTHONDONTWRITEBYTECODE=1   # keep submodules clean when we import their modules
