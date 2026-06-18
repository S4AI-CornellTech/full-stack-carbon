# C3 — EServe memory-model convergence: validation deltas

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

## Scope / not yet converged (kept as EServe-specific, documented follow-ups)
- **SoC**: still EServe's precomputed `soc_cf` constant in `gpuconfigs.json`
  (e.g. H100 = 41.5). Converging to `act_core.LogicModel` (die area × node CPA)
  would re-derive it and needs the original area/CI/yield assumptions to match —
  left as a follow-up.
- **SSD** (CPU `CF_SSD_PER_GB = 0.10999`) and the **TDP→PDN/cooling/chassis/PSU**
  heuristics have no `act_core` analog and remain in EServe.

## Verification
- `pytest tests/` (gpu + cpu calculators) passes; `test_gpu_memory_cf` updated to
  0.24×80 = 19.2. `test_h100_validation` placeholders updated to the converged model.
- Walkthrough segment 5 (`05_eserve`) refreshed to the new H100 numbers.
