# full-stack-carbon - suite orchestration. See README.md for the walkthrough story.
ROOT  := $(CURDIR)
WALK  := $(ROOT)/walkthrough
PYACT := $(ROOT)/.envs/act/bin/python
export MPLBACKEND := Agg

.PHONY: help submodules setup setup-full \
        demo-act demo-coffee demo-carbonclarity demo-microgreen demo-eserve demo-fairco2 \
        all-demos verify golden clean tutorial-act tutorial-eserve tutorial-fairco2

help: ; @printf '%s\n' \
  "full-stack-carbon suite targets:" \
  "  make submodules      init the six tool submodules (+ MicroGreen modeling dep)" \
  "  make setup           build per-tool Python envs (walkthrough deps)" \
  "  make setup-full      + heavy extras (MicroGreen hardware stack, Fair-CO2 forecasting)" \
  "  make all-demos       run all six walkthrough segments in order, then verify" \
  "  make demo-<tool>     one segment: act coffee carbonclarity microgreen eserve fairco2" \
  "  make tutorial-act    run the segment-1 hands-on tutorial BOMs (01_act/TUTORIAL.md)" \
  "  make tutorial-eserve run the segment-5 hands-on tutorial (05_eserve/TUTORIAL.md)" \
  "  make tutorial-fairco2 run the segment-6 hands-on tutorial (06_fairco2/TUTORIAL.md)" \
  "  make verify          check the cross-segment carbon handoffs line up" \
  "  make golden          show committed golden figures/results (zero compute)" \
  "  make clean           remove envs and regenerated figures"

submodules: ; git submodule update --init && git -C MicroGreen submodule update --init EmbodiedCarbonModeling

setup: ; bash scripts/bootstrap.sh
setup-full: ; FULL=1 bash scripts/bootstrap.sh

demo-act: ; bash $(WALK)/01_act/run.sh
demo-carbonclarity: ; bash $(WALK)/02_carbonclarity/run.sh
demo-coffee: ; bash $(WALK)/03_coffee/run.sh
demo-microgreen: ; bash $(WALK)/04_microgreen/run.sh
demo-eserve: ; bash $(WALK)/05_eserve/run.sh
demo-fairco2: ; bash $(WALK)/06_fairco2/run.sh

tutorial-act: ; @for b in exercises/sensitivity.yaml solutions/sensitivity_solved.yaml; do bash $(WALK)/01_act/tutorial.sh $$b; done && bash $(WALK)/01_act/tutorial.sh solutions/poweredge2.yaml --expect 72.55

tutorial-eserve: ; @bash $(WALK)/05_eserve/tutorial.sh --gpu H100HGX --host --expect gpu=103 --expect host=3355.4 --expect crossover=25.1 && bash $(WALK)/05_eserve/tutorial.sh --gpu-file exercises/gpu_l4.json && bash $(WALK)/05_eserve/tutorial.sh --gpu-file solutions/my_gpu.json --host

tutorial-fairco2: ; @bash $(WALK)/06_fairco2/tutorial.sh --swing llama --expect swing=2.02 && bash $(WALK)/06_fairco2/tutorial.sh --workloads exercises/workloads.json --expect faiss_rup=253.8 --expect faiss_shapley=761.5 --expect faiss_fairco2=571.2

all-demos: demo-act demo-carbonclarity demo-coffee demo-microgreen demo-eserve demo-fairco2 verify

verify: ; $(PYACT) $(WALK)/lib/verify_chain.py

golden: ; @for s in 01_act 02_carbonclarity 03_coffee 04_microgreen 05_eserve 06_fairco2; do bash $(WALK)/$$s/run.sh --golden; done

clean: ; rm -rf $(ROOT)/.envs $(ROOT)/.uv $(WALK)/*/figures
