# full-stack-carbon - one-stop bundle of the six carbon tools (git submodules) with shared
# per-tool Python envs and the in-repo hands-on tutorials. See README.md.
ROOT  := $(CURDIR)
export MPLBACKEND := Agg

.PHONY: help submodules setup setup-full clean tutorial-act tutorial-fairco2

help: ; @printf '%s\n' \
  "full-stack-carbon suite targets:" \
  "  make submodules      init the six tool submodules (+ MicroGreen modeling dep)" \
  "  make setup           build per-tool Python envs (uv-first)" \
  "  make setup-full      + heavy extras (MicroGreen hardware stack, Fair-CO2 forecasting)" \
  "  make tutorial-act    run ACT's in-repo hands-on tutorial (ACT/tutorial/TUTORIAL.md)" \
  "  make tutorial-fairco2 run Fair-CO2's in-repo hands-on tutorial (Fair-CO2/tutorial/TUTORIAL.md)" \
  "  make clean           remove the per-tool envs (.envs) and repo-local uv (.uv)"

submodules: ; git submodule update --init && git -C MicroGreen submodule update --init EmbodiedCarbonModeling

setup: ; bash scripts/bootstrap.sh
setup-full: ; FULL=1 bash scripts/bootstrap.sh

# ACT's and Fair-CO2's hands-on tutorials live IN their tool repos (ACT/tutorial, Fair-CO2/tutorial);
# these targets run them with the suite's per-tool env. ACT's uses the real act_model CLI directly
# (no wrapper); fairco2 calls the in-repo tutorial.sh via $PYTHON. (EServe's hands-on is its own
# repo's Quick Start — see EServe/README.md.)
tutorial-act: ; @for b in ACT/tutorial/exercises/sensitivity.yaml ACT/tutorial/solutions/sensitivity_solved.yaml ACT/tutorial/solutions/poweredge2.yaml; do PYTHONPATH=$(ROOT)/ACT $(ROOT)/.envs/act/bin/python -m act.act_model -m $$b -o /tmp/act-tut >/dev/null && echo "[ACT] $$b -> $$(grep '^total_carbon:' /tmp/act-tut/act_report.yaml)"; done && grep -q '^total_carbon: 72\.55' /tmp/act-tut/act_report.yaml && echo "  OK: poweredge2 ~= 72.55 kg" || { echo "  FAIL: poweredge2 != 72.55"; exit 1; }

tutorial-fairco2: ; @PYTHON=$(ROOT)/.envs/fair-co2/bin/python bash $(ROOT)/Fair-CO2/tutorial/tutorial.sh --swing llama --expect swing=2.02 && PYTHON=$(ROOT)/.envs/fair-co2/bin/python bash $(ROOT)/Fair-CO2/tutorial/tutorial.sh --workloads exercises/workloads.json --expect faiss_rup=253.8 --expect faiss_shapley=761.5 --expect faiss_fairco2=571.2

clean: ; rm -rf $(ROOT)/.envs $(ROOT)/.uv
