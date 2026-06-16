# The life of a data center — a carbon walkthrough

A single guided example that runs **six lab tools, one at a time**, in narrative
order, to trace carbon across the life of a data center: from designing and
manufacturing the silicon, through provisioning servers, to attributing the carbon
of the software that runs on them.

Every segment is **artifact-evaluation style**: it recomputes its result from
committed intermediate data (no live workloads, no cluster), writes a figure +
`result.json`, and can fall back to a committed golden with `--golden`. Each segment
also runs **standalone** — the value one segment hands the next is committed into the
next segment's `inputs/`, so no segment depends on another having just run.

## Run it
```bash
make setup            # one-time: per-tool Python envs
make all-demos        # run all six in order, then verify the chain
# or one at a time:
make demo-act         # demo-coffee, demo-carbonclarity, demo-microgreen, demo-eserve, demo-fairco2
make golden           # show the committed backup figures/numbers (zero compute)
make verify           # assert the cross-tool handoffs line up
```

## The story
| # | Tool | Beat | Headline (recomputed) |
|---|------|------|------------------------|
| 1 | **ACT** | A server is designed & manufactured | Dell R740 ≈ **1,523 kgCO2e** embodied (storage-dominated) |
| 2 | **COFFEE** | *branch:* emerging FeFET memory | HZO FeFET adds **+20%** energy-per-area vs CMOS |
| 3 | **CarbonClarity** | How trustworthy is that number? | R740 CPU die **7.3 kgCO2e** (P10–P90 5.2–9.6) |
| 4 | **MicroGreen** | *branch:* the edge tier | 8 edge boards, **0.18–1.14 kgCO2e**, IC-dominated |
| 5 | **EServe** | A server is provisioned (H100) | H100 HGX ≈ **154 kgCO2e** embodied (HBM + SoC) |
| 6 | **Fair-CO2** | Software is attributed its share | Co-location **halves** each job's attributed embodied carbon |

The **spine is 1 → 5 → 6** (manufacture → provision → attribute); **2** and **4** are
labelled side-branches (a silicon what-if and the edge tier). The carry-forward
quantity is embodied carbon, changing units as it descends the stack:
kgCO2e/cm² → per-component → per-server → per-workload.

## How the chain is real (not just narrated)
ACT's R740 embodied carbon (1,523 kgCO2e) and EServe's H100 figure (154 kgCO2e) are
committed into Fair-CO2's `inputs/`, and `make verify` asserts they match end to end.
Fair-CO2 itself hardcodes an ACT-derived per-CPU constant
(`ACT_cpu_chip_cf = 18530` gCO2e, `colocation/process_colocation_sweep.py:43`) — the
same kind of number ACT produces in segment 1 (related by method, not identical,
because that constant was computed for the node's actual Xeon, not the illustrative BOM).

## Anatomy of a segment
Each `NN_<tool>/` directory contains:
- `run.sh` — recompute the result (or `--golden` to restore the committed backup)
- `recompute.py` — the segment logic (uses `lib/walk.py` helpers)
- `inputs/` — committed handoffs from prior segments + any committed intermediate data
- `figures/` — regenerated outputs (gitignored)
- `golden/` — committed backup figures + `result.json` (the zero-compute fallback)
- `TALKING_POINTS.md` — the slide content for that tool's presentation (tool owners
  author the actual deck from this)
