# EServe — hands-on: provisioning is a carbon decision (≈20 min)

Model a GPU accelerator's **embodied carbon**, add the **host server** it racks into, and find the
**grid crossover** where building the box outweighs running it. This follows the 5-minute EServe intro
(`TALKING_POINTS.md`).

You'll use EServe's real calculators through a helper, `tutorial.sh`, which models a GPU (and optionally
its host) and computes the embodied-vs-operational crossover:

```bash
cd walkthrough/05_eserve
./tutorial.sh --gpu H100HGX --host         # GPU + host embodied + the grid crossover
```

Prereq: `make setup` built the `eserve` env. Paths below are relative to `walkthrough/05_eserve/`.

**What a GPU config is.** A small JSON of fields EServe turns into carbon: `tdp`, `memory_size` (GB),
`memory_type` (HBM3e/HBM3/HBM2e/GDDR6/…), `soc_area`/`soc_cf` (the chip), `pcb_area`, `lifetime_years`,
`suggested_psu`. The bundled set is `EServe/config/gpuconfigs.json` (use by `--gpu NAME`); the editable
copies for this tutorial live in `exercises/` (use by `--gpu-file …`, so the submodule stays clean).

---

## Stage 1 — Read the H100 accelerator (≈3 min)

```bash
./tutorial.sh --gpu H100HGX
```
**GPU embodied ≈ 103 kg**, broken into SoC 41.5 · PDN 28.8 · memory 19.2 (HBM3) · cooling 6.5 · PCB 1.2
· connection 0.9. This is the slide everyone shows for "GPU carbon" — and (spoiler) it's the *small
half*. The memory uses the paper-backed **HBM3 = 0.24 kgCO2e/GB** (`act_core`, EcoServe Table 1), the
same coefficient ACT would use — not the old unsourced 0.85.

---

## Stage 2 — Compare accelerators, then edit a field (≈5 min)

```bash
./tutorial.sh --gpu L4            # ≈ 31.1 kg — a small inference GPU vs the H100's 103
```
Now edit a *segment-local* copy (`exercises/gpu_l4.json`) — the submodule stays untouched — change one
field, re-run:

| Knob | Edit | Effect |
|---|---|---|
| memory tech | `memory_type: GDDR6 → HBM3e` | total **31.1 → 22.9 kg** — per-GB 0.36→0.24 *and* the cooling model flips to the HBM/liquid branch (an honest nuance worth naming) |
| memory size | `memory_size: 24 → 48` | total **31.1 → 40.2 kg** — memory carbon is linear in GB |
| lifetime | `lifetime_years: 4 → 6` | embodied total **unchanged** (it's the manufactured carbon) — but it stretches amortization, lowering the embodied *rate* you'll meet in Stage 4 |

```bash
./tutorial.sh --gpu-file exercises/gpu_l4.json     # re-run after each edit
```
(Solved memory-tech variant: `solutions/gpu_l4_hbm3e.json`.) **Takeaway:** a GPU's embodied number is a
handful of explicit, editable inputs — just like an ACT BOM.

---

## Stage 3 — The host reveal (≈4 min)

```bash
./tutorial.sh --gpu H100HGX --host
```
| Component | kgCO2e |
|---|---|
| GPU (1 accelerator) | 103 |
| Host SSD (22.7 TB) | 227 |
| Host DRAM (2 TB) | 580 |
| **Host total** | **1,084** |

The host is **≈91%** of one accelerator's embodied carbon; its storage + DRAM alone is **≈8× the GPU**.
The accelerator you obsessed over is still the small half. Storage is priced on `act_core`'s shared
**bare-die NAND** (nand_10nm = 10 g/GB, the same source ACT/MicroGreen use), so the host is **DRAM-led**:
its 2 TB of DDR4 (580 kg) outweighs even 22.7 TB of SSD (227 kg). **Back-link:** that host *is* the kind
of server you learned to model in **ACT (segment 1)** — here it dominates the GPU box.
*(For a host-less GPU like L4, `--host` borrows the H100 HGX reference host and says so — the host is the
box you rack GPUs into, not a property of the chip.)*

---

## Stage 4 — The grid crossover, swept for your region (≈4 min)

```bash
./tutorial.sh --gpu H100HGX --host --grid-ci 17 261 501
```
The 8-GPU node (5.95 kW, 80% util, 4-yr life) has a flat **embodied rate ≈ 54 g/hr** and an operational
rate that rises with the grid: **81 / 1,242 / 2,385 g/hr** at 17 / 261 / 501 gCO2e/kWh. They cross at
**≈ 11.4 gCO2e/kWh** — *below* all three, so operational wins at every one (yes, even Sweden's 17). Find
the regime where building outweighs running:

```bash
./tutorial.sh --gpu H100HGX --host --grid-ci 8       # below crossover: embodied wins
./tutorial.sh --gpu H100HGX --host --grid-ci 30 --util 0.5
```
**Takeaway:** for this big-host H100 node the crossover (~11 g/kWh) sits *below* essentially every real
grid's annual average, so **operational dominates almost everywhere** — by ~1.5× on a clean grid (Sweden
17) up to ~44× on a dirty one (California 501). *Building* outweighs *running* only in the very cleanest
pockets (<~11 g/kWh). What dominates — and by how much — is still the grid's call, not the GPU's. Sample
grids: Sweden 17 · Ontario ~30 · France ~56 · world avg 261 · California 501 · India 725.

---

## Stage 5 — Capstone: provision for your deployment (≈4 min)

Fill `exercises/my_gpu_starter.json` with your accelerator's datasheet fields, then provision it in your
region:
```bash
./tutorial.sh --gpu-file exercises/my_gpu_starter.json --host --n-gpus 8 --util 0.7 --grid-ci <your_region>
```
The helper prints the GPU breakdown, the host-inclusive node footprint, and the crossover — i.e. whether
your deployment is **embodied- or operational-dominated**. A complete example is `solutions/my_gpu.json`
(an A100 SXM + its own host):
```bash
./tutorial.sh --gpu-file solutions/my_gpu.json --host     # GPU 99 / host 892 / crossover 18.2
```
Note this lighter node's crossover (~18 g/kWh) sits *above* Sweden's 17 — so on the A100 box a clean grid
**does** flip to embodied-dominated, where the bigger, higher-power H100 node (crossover ~11) stays
operational-dominated. The crossover is a property of the *node* (power + host size), not just the grid.
Compare to `solutions/EXPECTED.md`.

**Optional extend (≈2 min)** — add a GPU EServe doesn't ship. Add an entry to
`EServe/config/gpuconfigs.json` (on your checkout), run `./tutorial.sh --gpu MyNewGPU`, then revert with
`git -C EServe checkout config/gpuconfigs.json`. (The core exercises use segment-local `exercises/*.json`
precisely so you never have to touch the submodule.)

---

## Honesty (say it aloud)

The GPU and host embodied numbers are EServe's **own calculators**. The grid crossover is a thin analysis
layer on top (`operational = node power × utilization × grid CI`). The full EcoServe serving optimizer
(Reduce / Reuse / Rightsize / Recycle + ILP, the paper's ~47% headline) has **no code in this repo** — so
we demonstrate the *observations*, not the optimization. **Don't claim 47%.**

## Where this goes next

This node's embodied carbon (the `gpu_embodied 103` it commits) flows to **segment 6 (Fair-CO2)**, which
time-allocates it fairly across the co-located queries that share the box.
