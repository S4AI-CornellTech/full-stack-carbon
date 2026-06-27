# The life of a data center — a carbon walkthrough

Six lab tools, run one at a time, in narrative order. The thread that ties them
together: **at every scale, the naive carbon number misleads.** Each tool starts from
a number you might naively report, then reveals the decision or trade-off that number
hides. Underneath all six is one recurring tension — **embodied (manufacturing) carbon
vs operational (running) carbon** — and the lesson that point estimates, static
breakdowns, and proportional splits all give the wrong answer.

Every segment is **artifact-evaluation style**: it recomputes from committed data (no
live workloads, no cluster), writes a figure + `result.json`, and falls back to a
committed golden with `--golden`. Each segment runs standalone.

## Run it
```bash
make setup        # one-time: per-tool Python envs
make all-demos    # run all six in order, then verify the chain
# or one at a time, in story order:
make demo-act     # demo-carbonclarity, demo-coffee, demo-microgreen, demo-eserve, demo-fairco2
make golden       # committed backup figures/numbers (zero compute)
make verify       # assert the cross-tool carbon handoffs line up
```

## The story: naive number → real decision
| # | Tool | The naive number | The real point |
|---|------|------------------|----------------|
| 1 | **ACT** | "the server is 1,523 kgCO2e" | one deterministic, **embodied-only** number — the foundation, and the thing the rest complicates |
| 2 | **CarbonClarity** | "…so report 1,523" | it's a **distribution**: ACT ≈ the *mean* (~50% exceedance); report the **95th percentile (~1.3×)**, and uncertainty **grows at advanced nodes** |
| 3 | **COFFEE** | "FeFET memory costs +11% carbon" | wrong axis: **+11% per cm² but ~4.3× *less* per MB** (+ lower leakage) — a life-cycle **trade-off FeFET wins** |
| 4 | **MicroGreen** | "this MCU has the lowest embodied carbon" | the **carbon-optimal device flips** with light / inference-rate / lifetime (>10×); energy-efficiency ≠ the carbon winner |
| 5 | **EServe** | "the H100 is 154 kgCO2e" | the **host dominates** (~1,084 kg vs the GPU's ~103, now DRAM-led); and **embodied outweighs operational only below ~11 gCO2e/kWh** — beneath real grids, so the grid *and node size* decide (storage on act_core's bare-die NAND; GPU memory the paper-backed 0.24) |
| 6 | **Fair-CO2** | "split shared carbon by usage" | that proportional split (the industry default) is **~80% unfair** (up to 279%) vs a Shapley ground truth — Fair-CO2 fixes it **~4–6×** at **600,000× less compute** |

## The throughline: the embodied↔operational crossover, at every scale
Embodied carbon dominates at the **edge** (MicroGreen: tiny devices, ~75% embodied);
operational carbon dominates in the **data center** (EServe) on essentially every real
grid — *embodied wins only on the very cleanest grids*, below ~11 gCO2e/kWh (and on
lighter, lower-power nodes, whose crossover rises higher). The same co-optimization
recurs at every tier; only the dominant term changes. Segments **4→5 are deliberately
paired** to show that crossover, and **Fair-CO2 (6) is the climax**: once the carbon is
built and burned, *splitting it fairly* is its own hard problem — and getting it right
is what lets anyone act on it.

## How the chain is real (not just narrated)
ACT's R740 embodied carbon (1,523 kg) and EServe's H100 figure (~103 kg) are committed
into Fair-CO2's `inputs/`, and `make verify` asserts they match end to end — Fair-CO2
even hardcodes an ACT-derived per-CPU constant, `ACT_cpu_chip_cf = 18,530` gCO2e
(`colocation/process_colocation_sweep.py:43`).

## Anatomy of a segment
Each `NN_<tool>/` directory contains:
- `run.sh` — recompute the result (or `--golden` to restore the committed backup)
- `recompute.py` — the segment logic (uses `lib/walk.py` helpers)
- `inputs/` — committed handoffs from prior segments + any committed intermediate data
- `figures/` — regenerated outputs (gitignored)
- `golden/` — committed backup figures + `result.json` (the zero-compute fallback)
- `TALKING_POINTS.md` — slide content for that tool's presentation, with honesty
  caveats where committed data is partial (tool owners author the actual deck)

**Segments 1 (ACT), 5 (EServe), and 6 (Fair-CO2)** carry hands-on tutorials — the per-tool hands-on
format: each has `TUTORIAL.md` (a ~20-min guided walkthrough), a `tutorial.*` runner (drive the real
tool from editable config files), `exercises/` (participant-editable starters), and `solutions/`
(reference configs + `EXPECTED.md`). Run them with `make tutorial-act` / `tutorial-eserve` /
`tutorial-fairco2`.
