# Expected results — segment-1 ACT tutorial

Reference numbers for the hands-on. Recompute any BOM with `./tutorial.sh <bom>` from
`walkthrough/01_act/`. (FAB = FABRICATION; each component also carries 150 g/IC PACKAGING.)

## Stage 1 — Dell R740 (read example)
`../../ACT/act/boms/dellr740.yaml` → **total_carbon ≈ 1,523.1 kg** (FABRICATION ~1,468, PACKAGING ~55).
By class: **SSD ~1,120 · DRAM ~380 · CPU ~23 kg**. (This is the canonical `make demo-act`.)

## Stage 2 — sensitivity (`exercises/sensitivity.yaml`)
Baseline — soc 7 cm² / 28nm / coal + mem 64 GB / ddr3_50nm → **total ≈ 55.49 kg**
(soc FAB 11.30, mem FAB 43.89).

| Knob | change | result |
|---|---|---|
| **A** node | `soc.process` 28nm → 7nm (coal) | soc FAB 11.30 → **20.90** |
| **B** grid | `soc.fab_ci` coal → wind (7nm) | soc FAB 20.90 → **6.99** |
| **C** memory | `mem.process` ddr3_50nm → ddr4_10nm | mem FAB 43.89 → **4.75** |

All three applied → `solutions/sensitivity_solved.yaml` → **total ≈ 12.04 kg** (soc 6.99, mem 4.75).

## Stage 3 — second PowerEdge (capstone)
`solutions/poweredge2.yaml` — the **Fair-CO2 test node** (2× Xeon Gold 6240R 14 nm · 192 GB DDR4 ·
480 GB SSD) → **total ≈ 72.55 kg**:

| class | kgCO2e |
|---|---|
| DRAM (12× 16 GB ECC) | 47.34 |
| CPU (2× 698 mm² 14 nm) | 18.23 |
| SSD (480 GB) | 6.69 |
| PCB | 0.30 |

Contrast with the R740 read example (1,523 kg, SSD-dominated): this compute-focused server is
**DRAM-dominated** (65%) — 192 GB of ECC DDR4 with heavy per-module IC packaging (19 ICs × 12), little
storage. The CPU (18.2 kg) ≈ the Fair-CO2 paper's ACT-derived `ACT_cpu_chip_cf` (18.53 kg for both
dies). Carbon is what ACT computes from the config; we don't align to the doc's per-component numbers
(different DRAM/SSD coefficients; chassis/PSU/cooling are out of BOM scope).

## Stage 4 — extend data (add the `france` location)
After adding `france` (56 g/kWh) to the `EnergyLocation` enum + `location_2022.yaml`, the 7 cm² / 7nm
die on `fab_ci: france` → soc FAB **≈ 7.76 kg** — between wind (6.99) and the dirtier grids (taiwan
16.8, coal 20.9), since France's grid is near the clean end.
