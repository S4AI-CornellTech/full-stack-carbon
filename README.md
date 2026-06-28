# Full-Stack Carbon

A unified suite of lab tools for **carbon modeling of computer hardware and systems** —
from device design & manufacturing, through server provisioning, to software carbon
attribution in the cloud. The six tools are bundled here as git submodules, each with its
own **self-contained hands-on tutorial**, sharing one set of per-tool Python environments.

## The tools
| Tool | Layer | What it models |
|------|-------|----------------|
| [ACT](https://github.com/S4AI-CornellTech/ACTv2) | chip / server | Embodied + operational carbon from a bill-of-materials |
| [COFFEE](https://github.com/S4AI-CornellTech/COFFEE) | emerging memory | Life-cycle carbon of HZO FeFET memory (a density / endurance trade-off) |
| [CarbonClarity](https://github.com/S4AI-CornellTech/CarbonClarity) | uncertainty | Probabilistic embodied carbon — distributions & risk, not point estimates |
| [MicroGreen](https://github.com/S4AI-CornellTech/MicroGreen) | edge / IoT | Carbon-aware design-space exploration (embodied vs operational) for edge devices |
| [EServe](https://github.com/S4AI-CornellTech/EServe) (a.k.a. EcoServe) | server | Carbon-aware LLM serving — embodied + operational across the fleet |
| [Fair-CO2](https://github.com/S4AI-CornellTech/fair-co2) | datacenter | Fair (Shapley-based) carbon attribution for co-located workloads |

## Quickstart
**No global install needed.** `make setup` uses a system [`uv`](https://docs.astral.sh/uv/) if you
have one; otherwise it provisions a **repo-local** `uv` under `.uv/` (gitignored) — its binary, the
per-tool Pythons (3.11 / 3.12), and its cache all stay inside the repo, so nothing is installed
machine-wide. (First run needs a `python3` and network to bootstrap; `make clean` / `rm -rf .uv .envs`
removes everything.)

**Platforms:** Linux and macOS (CI runs on Linux). On Windows, run it inside [WSL](https://learn.microsoft.com/windows/wsl/).

```bash
git clone https://github.com/S4AI-CornellTech/full-stack-carbon.git
cd full-stack-carbon
git submodule update --init
git -C MicroGreen submodule update --init EmbodiedCarbonModeling  # MicroGreen modeling dep
make setup          # build the isolated per-tool Python envs (uv-first)
```
Then run a hands-on tutorial (next section), or `make help` for all targets.

## Hands-on tutorials

The **ACT** and **Fair-CO2** tutorials live in their tool repo under `<Tool>/tutorial/`; **EServe**'s
hands-on is its repo's own **Quick Start**. Each runs in that tool's isolated environment
(`.envs/<tool>/`, built by `make setup`). From the suite root, **activate the env, run, then
`deactivate`:**

**ACT** — drive the real `act_model` CLI on bill-of-materials files you edit:
```bash
source .envs/act/bin/activate
cd ACT
python -m act.act_model -m tutorial/solutions/poweredge2.yaml -o /tmp/act-out
cat /tmp/act-out/act_report.yaml        # then edit a BOM under tutorial/ and re-run
deactivate
```

**EServe** — model a GPU accelerator and its host: its hands-on is the EServe repo's own **Quick Start**
(`EServe/README.md`, with runnable `EServe/examples/`), in the `eserve` env (`source .envs/eserve/bin/activate`).

**Fair-CO2** — attribute a shared server's carbon fairly across co-located jobs:
```bash
source .envs/fair-co2/bin/activate
cd Fair-CO2/tutorial
python tutorial.py
deactivate
```

The full ACT and Fair-CO2 tutorials are in `<Tool>/tutorial/TUTORIAL.md`. Shortcut — no activation
needed — from the suite root: `make tutorial-act` / `make tutorial-fairco2`.

## Environments
The tools carry mutually incompatible pins (numpy 2.3.4 / 2.3.5 / 2.4.3; Python 3.11
vs 3.12), so each gets its **own** virtual environment under `.envs/<tool>/`, created
by `scripts/bootstrap.sh`. Heavy/optional pieces (MicroGreen's on-device hardware +
Streamlit stack, Fair-CO2's Prophet/HuggingFace forecasting path) are gated behind
`make setup-full`.

## Layout
```
ACT/ COFFEE/ CarbonClarity/ MicroGreen/ EServe/ Fair-CO2/   # the six tool submodules
  ACT/tutorial/  Fair-CO2/tutorial/                         # ACT & Fair-CO2 in-repo tutorials
scripts/bootstrap.sh  per-tool environment builder
Makefile            orchestration (make help)
```

## Notes
- Submodules use HTTPS URLs so the suite clones anonymously for artifact evaluation.
- `make setup` only builds the per-tool envs under `.envs/` — it never modifies a submodule's
  tracked files. The hands-on tutorials live inside the tool repos themselves
  (`ACT/tutorial/`, `Fair-CO2/tutorial/`; EServe's is its repo Quick Start).

## Citation
See `CITATION.cff` and each tool's own README for per-tool references.
