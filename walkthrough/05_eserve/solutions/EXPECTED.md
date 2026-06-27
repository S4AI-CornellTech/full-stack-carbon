# Expected results — segment-5 EServe tutorial

Reference numbers (all reproduced live by EServe's calculators). Recompute with
`./tutorial.sh …` from `walkthrough/05_eserve/`.

## Stage 1 — read the H100 (`--gpu H100HGX`)
GPU embodied **103.0 kg**: SoC 41.5 · PDN 28.75 · memory 19.2 (HBM3) · cooling 6.5 · PCB 1.19 · conn 0.93.

## Stage 2 — compare + edit (`exercises/gpu_l4.json`)
| Config | total |
|---|---|
| L4 baseline (GDDR6, 24 GB) | **31.1** |
| `memory_type → HBM3e` (`solutions/gpu_l4_hbm3e.json`) | **22.9** (memory 8.64→5.76; cooling flips to the HBM/liquid branch) |
| `memory_size 24 → 48` | **40.2** (memory linear in GB) |
| `lifetime_years 4 → 6` | embodied unchanged (lowers the amortized rate in Stage 4) |

## Stage 3 — the host reveal (`--gpu H100HGX --host`)
Host **3,355.4 kg** = SSD 2,499 + DRAM 580 + other 276.4. Host ≈ **97.0%** of one accelerator;
storage+DRAM ≈ **29.9×** the GPU.

## Stage 4 — the crossover (`--gpu H100HGX --host --grid-ci 17 261 501`)
Node (8 GPU + host) embodied **4,179.4 kg** → **119.3 g/hr** amortized; **5.95 kW** @ 80% util.
Operational: 80.9 / 1,242.4 / 2,384.8 g/hr at CI 17 / 261 / 501. **Crossover ≈ 25.1 gCO2e/kWh.**

## Stage 5 — capstone (`--gpu-file solutions/my_gpu.json --host`)
A100 SXM: GPU **99.0** · host **1,531.4** (host ≈ 93.9%, storage+DRAM ≈ 12.7×) · node **2,323.4** ·
crossover **≈ 25.1 gCO2e/kWh**.

> The GPU/host embodied are EServe's own calculators; the crossover is a thin analysis layer
> (`operational = power × util × CI`). The EcoServe 4R/ILP optimizer (~47%) is the paper, not run.
