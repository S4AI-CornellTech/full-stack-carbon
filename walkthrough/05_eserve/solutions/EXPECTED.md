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
Host **1,083.7 kg** = SSD 227.2 + DRAM 580 + other 276.5. Host ≈ **91.3%** of one accelerator;
storage+DRAM ≈ **7.8×** the GPU. (SSD on `act_core`'s bare-die NAND nand_10nm = 10 g/GB → the host is
DRAM-led: DRAM 580 > SSD 227.)

## Stage 4 — the crossover (`--gpu H100HGX --host --grid-ci 17 261 501`)
Node (8 GPU + host) embodied **1,907.7 kg** → **54.4 g/hr** amortized; **5.95 kW** @ 80% util.
Operational: 80.9 / 1,242.4 / 2,384.8 g/hr at CI 17 / 261 / 501. **Crossover ≈ 11.4 gCO2e/kWh** — below
all three, so operational wins at every one (even Sweden 17); embodied wins only below ~11.

## Stage 5 — capstone (`--gpu-file solutions/my_gpu.json --host`)
A100 SXM: GPU **99.0** · host **891.5** (host ≈ 90.0%, storage+DRAM ≈ 6.2×) · node **1,683.5** ·
crossover **≈ 18.2 gCO2e/kWh** — note this lighter node's crossover sits *above* Sweden's 17, so its
clean-grid case flips to embodied (unlike the bigger H100 node at ~11).

> The GPU/host embodied are EServe's own calculators; the crossover is a thin analysis layer
> (`operational = power × util × CI`). The EcoServe 4R/ILP optimizer (~47%) is the paper, not run.
