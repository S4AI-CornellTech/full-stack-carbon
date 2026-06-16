# Segment 5 — EServe: provisioning the accelerator

**Story beat.** The data center grows. To serve modern AI workloads we rack an
NVIDIA **H100 HGX** node. EServe gives its embodied carbon, component by component.

**Run it:** `make demo-eserve`  (or `walkthrough/05_eserve/run.sh`)

**Headline number: ~154 kgCO2e** embodied per H100HGX accelerator:

| Component | kgCO2e |
|---|---|
| memory (80 GB HBM3) | 68.0 |
| SoC (814 mm², 5 nm) | 41.5 |
| PDN | 28.75 |
| cooling | 6.5 |
| PCB | 1.2 |
| connection (NVLink) | 0.9 |
| **total** (+5% margin) | **154.2** |

For context, the R740 from segment 1 was ~1,523 kgCO2e — but *that* footprint was
storage; here it's **HBM memory and the large 5 nm SoC** that dominate.

**Figure:** `figures/eserve_h100_breakdown.png`.

**What to say (slide bullets):**
- Accelerators shift the embodied-carbon balance: HBM + a big advanced-node die
  dominate, unlike the storage-heavy general-purpose server.
- EServe reuses ACT's core idea (SoC carbon from die area × process node) but adds
  a per-GB memory-by-type model (HBM3) and TDP-scaled power-delivery/cooling —
  exactly the pieces the act-core unification (workstream C) folds into one model.
- This is *full* embodied carbon; only a slice is charged to any one job, in
  proportion to how long it runs — which is segment 6's problem.

**Hands off to:**
- → **Segment 6 (Fair-CO2):** the accelerator's embodied carbon
  (`inputs/from_05_eserve.json`), to be fairly split across co-located workloads.

**Note.** SoC carbon (41.5) is a precomputed ACT/iMEC-derived constant in EServe's
config; segment 3 (CarbonClarity) shows the fab-uncertainty band such 5 nm figures
carry — EServe wires that in as the SoC error bar when segment 3 has been run.
