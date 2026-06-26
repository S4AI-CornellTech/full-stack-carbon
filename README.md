# Full-Stack Carbon

A unified suite of lab tools for **carbon modeling of computer hardware and systems** —
from device design & manufacturing, through server provisioning, to software carbon
attribution in the cloud. The six tools are bundled here as git submodules with a
single guided walkthrough that ties them into one story: **the life of a data center**.

> **Collaborators / reviewers:** start with **[CONTRIBUTING.md](CONTRIBUTING.md)** — the handoff guide: current state, the branch model (review on `act-core`, nothing merged to `main`), how to run, and how to continue.

## The tools
| Tool | Layer | What it models |
|------|-------|----------------|
| [ACT](ACT) | chip / server | Embodied + operational carbon from a bill-of-materials |
| [COFFEE](COFFEE) | emerging memory | Life-cycle carbon of HZO FeFET memory (a density / endurance trade-off) |
| [CarbonClarity](CarbonClarity) | uncertainty | Probabilistic embodied carbon — distributions & risk, not point estimates |
| [MicroGreen](MicroGreen) | edge / IoT | Carbon-aware design-space exploration (embodied vs operational) for edge devices |
| [EServe](EServe) (a.k.a. EcoServe) | server | Carbon-aware LLM serving — embodied + operational across the fleet |
| [Fair-CO2](Fair-CO2) | datacenter | Fair (Shapley-based) carbon attribution for co-located workloads |

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
git checkout act-core
git submodule update --init
git -C MicroGreen submodule update --init EmbodiedCarbonModeling   # modeling dep only
make setup          # build isolated per-tool Python envs (uv-first)
make all-demos      # run the six-tool walkthrough, then verify the chain
make golden         # or: show committed backup figures with zero compute
```
See **[walkthrough/README.md](walkthrough/README.md)** for the guided story, and
`make help` for all targets.

## Environments
The tools carry mutually incompatible pins (numpy 2.3.4 / 2.3.5 / 2.4.3; Python 3.11
vs 3.12), so each gets its **own** virtual environment under `.envs/<tool>/`, created
by `scripts/bootstrap.sh`. Heavy/optional pieces (MicroGreen's on-device hardware +
Streamlit stack, Fair-CO2's Prophet/HuggingFace forecasting path) are gated behind
`make setup-full`.

## Layout
```
ACT/ COFFEE/ CarbonClarity/ MicroGreen/ EServe/ Fair-CO2/   # the six tool submodules
walkthrough/        the six-segment guided example (the workshop centerpiece)
scripts/bootstrap.sh  per-tool environment builder
Makefile            orchestration (make help)
```

## Notes
- Submodules use HTTPS URLs so the suite clones anonymously for artifact evaluation.
- The walkthrough never modifies a submodule: it reuses each tool's code/data in place
  and writes only into `walkthrough/<segment>/figures/` (gitignored).

## Citation
See `CITATION.cff` and each tool's own README for per-tool references.
