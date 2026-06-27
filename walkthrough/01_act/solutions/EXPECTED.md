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
`solutions/poweredge2.yaml` → **total ≈ 95.94 kg**  ⚠️ **PLACEHOLDER** — an illustrative stand-in
server, **not real**. Placeholder breakdown: CPU 2 × 12.17 · DRAM 4 × 6.25 · SSD 2 × 23.14 · PCB 0.30 kg.

**TODO (maintainer):** replace `solutions/poweredge2.yaml`'s `__TODO__` values with the real
second-PowerEdge config and put the real reference total here; then add `--expect <total>` to the CI
smoke check in `.github/workflows/ci.yaml`.

## Stage 4 — extend data (add the `france` location)
After adding `france` (56 g/kWh) to the `EnergyLocation` enum + `location_2022.yaml`, the 7 cm² / 7nm
die on `fab_ci: france` → soc FAB **≈ 7.76 kg** — between wind (6.99) and the dirtier grids (taiwan
16.8, coal 20.9), since France's grid is near the clean end.
