# C3 — EServe memory + SSD convergence: validation deltas

EServe's GPU and CPU calculators now share `act_core.MemoryModel`, whose per-GB
coefficients come from the **EcoServe paper, Table 1** (TechInsights "Micron 1α
DRAM," Nov 2024 + SK hynix HBM3e, 2024): HBM3e/HBM3/HBM2e = **0.24**, HBM2/HBM1 =
0.28, DDR4/LPDDR5 = 0.29, GDDR6 = 0.36 kgCO2e/GB.

This corrects the GPU calculator's previous **0.85** for HBM3e/HBM3/HBM2e, which
was unsourced (absent from the paper; the `# Constants from the paper` comment was
wrong) and higher than ACT's oldest DDR3-50nm DRAM node (0.6 kg/GB). The CPU
calculator already used 0.24 — so this also makes GPU and CPU self-consistent.

## Per-GPU change (full-embodied component values, vs C0 baseline)
Only HBM3/HBM3E parts change; HBM2/GDDR6 parts were already at 0.28/0.36.

| GPU | memory (old → new) | component-sum (old → new) |
|---|---|---|
| A100SXM   | 68.0 → **19.2**  | 143.06 → **94.26** |
| H100PCIE  | 68.0 → **19.2**  | 158.79 → **109.99** |
| H100HGX   | 68.0 → **19.2**  | 146.86 → **98.06** |
| GH200SXM  | 81.6 → **23.04** | 160.46 → **101.9** |
| A100PCIE, A40, V100PCIE, L4, T4, A5500, A6000 | unchanged | unchanged |

H100HGX full embodied (×1.05 margin): **154.2 → ~102.96 kgCO2e**.

## SSD convergence (storage)
The CPU calculator's SSD coefficient now comes from `act_core.SSDModel` — the same
bare-die NAND tables (`models/ssd/ssd_hynix.yaml`) ACT and MicroGreen use. Storage is
priced at **nand_10nm = 10 g/GB = 0.010 kgCO2e/GB** (delivered per-GB, fab_yield 1.0; the
node the ACT PowerEdge capstone uses), replacing the former whole-device **0.10999** —
~11× higher and the last coefficient EServe didn't share with `act_core`.

Impact on the H100 HGX host (22.7 TB SSD): **2,499 → 227 kg**, dropping the host total
**3,355 → 1,084 kg** (now DRAM-led: DRAM 580 > SSD 227). Per-accelerator host share
97% → 91%; storage+DRAM ratio 30× → 8× the GPU. The whole-node embodied↔operational
crossover falls **25.1 → 11.4 gCO2e/kWh** (below essentially every real grid — see the
segment-5 talking points). The GPU side is SSD-free and unchanged (103 kg); `verify_chain`'s
handoff (the GPU number) stays green.

## Scope / not yet converged (kept as EServe-specific, documented follow-ups)
- **SoC**: still EServe's precomputed `soc_cf` constant in `gpuconfigs.json`
  (e.g. H100 = 41.5). Converging to `act_core.LogicModel` (die area × node CPA)
  would re-derive it and needs the original area/CI/yield assumptions to match —
  left as a follow-up.
- The **TDP→PDN/cooling/chassis/PSU** heuristics have no `act_core` analog and remain
  in EServe.

## Verification
- `pytest tests/` (gpu + cpu calculators) passes; `test_gpu_memory_cf` updated to
  0.24×80 = 19.2; `test_cpu_ssd_cf` updated to 0.010×120 = 1.2 (act_core nand_10nm).
  `test_h100_validation` (GPU, SSD-free) unchanged at the converged model.
- Walkthrough segment 5 (`05_eserve`) refreshed to the new host/crossover numbers
  (host 1,084, crossover 11.4); `make verify` still ALL CONSISTENT (GPU handoff = 103).
