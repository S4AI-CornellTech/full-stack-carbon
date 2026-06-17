# Segment 3 — COFFEE: the memory-technology trade-off (density inversion)

**Story beat.** A what-if branching off the silicon story: what if the chip used
emerging **HZO FeFET** non-volatile memory instead of conventional CMOS SRAM?
COFFEE is a *life-cycle* carbon model for FeFET — it extends ACT's CMOS per-area
model with the ferroelectric layer (FEL) that FeFET adds via Atomic Layer
Deposition (ALD). The result is **not an "overhead." It's a trade-off**, and at the
system level it comes out in FeFET's favour.

**Run it:** `make demo-coffee`  (or `walkthrough/03_coffee/run.sh`)

**Headline — a density inversion.** FeFET costs a little more carbon per unit
*area*, but far less carbon per stored *megabyte*, because its cell is ~5x denser:

| Metric | CMOS / SRAM | FeFET HZO_5 | FeFET vs baseline |
|---|---|---|---|
| Carbon **per cm²** (CPA) | 1328 gCO₂e/cm² | 1448 gCO₂e/cm² | **+9.0%** — FeFET *loses* on area |
| Carbon **per MB** (2–32 MB) | 12.9 gCO₂e/MB | 3.0 gCO₂e/MB | **~4.3× lower** — FeFET *wins* on density |

So the headline is: **+9–11% embodied carbon per cm², but ~4.3× LOWER carbon per
MB — and lower operational (leakage) energy — so the right memory-tech choice is a
life-cycle trade-off, not an "overhead."**

**Figure:** `figures/coffee_density_inversion.png` (two panels — left: per cm²,
CMOS vs FeFET, +9–11%; right: per MB, SRAM vs FeFET, ~4.3× lower across 2–32 MB).

**What to say (slide bullets):**
- COFFEE reuses ACT's CMOS process-node model and layers the FeFET ALD ferroelectric
  stack on top — one tool literally extending another's primitives. The number that
  matters for embodied carbon is **carbon-per-area (CPA)**, and COFFEE computes it
  from its own `Fab_Logic` (CMOS-28 nm 1328 g/cm² matches the paper's Fig. 6 ~1327).
- **Per cm², FeFET loses by ~+9%** (the ALD ferroelectric layer is extra fab energy).
- **Per MB, FeFET wins by ~4.3×**: the FeFET cell is ~5× denser (30 F² vs 146 F²),
  so it needs ~4.7× less array area per megabyte — which more than cancels the +9%
  per-area penalty. The advantage is essentially **flat from 2 MB to 32 MB**.
- This is the **memory-technology decision inside the embodied-vs-operational
  trade-off** (`CF = OCF + (T/LT)·ECF`): a one-time fabrication cost amortised over
  the device's operating life via lower leakage/energy, gated by write-endurance.
- **Endurance ↔ CPA co-optimisation** (qualitative): a thicker HZO layer raises CPA
  but buys higher write-endurance / lifetime — so the "best" device is a life-cycle
  optimum, not simply the lowest-CPA one.

**Two honesty caveats (say them out loud):**
1. **The "+20%" you may have heard is an *energy* number, not a carbon number.**
   The ferroelectric layer adds ~20% to the CMOS *energy-per-area* (EPA: 0.90 → 1.08
   kWh/cm²). But EPA is only the *energy* term of CPA; the gas + materials terms are
   unchanged, so once you carry it through to **carbon-per-area the penalty dilutes
   to +9–11%**. The "+9 vs +11" spread is purely the FEL **area-efficiency**
   assumption: the committed `fefet_ald.json` uses 0.80 → **+9.0%**; the paper's
   `Figure_coffee/coffee.ipynb` hardcodes ~0.96 → **+10.9%**. We show both bars.
2. **Units are grams, not kilograms.** COFFEE's `get_cpa()` returns **gCO₂e/cm²**
   (some `Fab_Logic` debug prints mislabel it "kgCO2e/cm²"). 1328 g/cm² is right and
   matches ACT's Fig. 6; a "kg/cm²" slide would be ~1000× wrong. Every axis and
   number here stays in grams.

**Relationship.**
- *Prev — CarbonClarity (segment 2)* put an **uncertainty band** on exactly this
  CMOS-28 nm per-area carbon (~1328 g/cm²). COFFEE takes the *same* per-area model
  and asks a **design** question on top of it: swap CMOS memory for denser FeFET.
- *Next — MicroGreen (segment 4)* carries the same ACT-based embodied-carbon lens
  down to the **edge/IoT tier** (grams, whole MCU boards). Both COFFEE and MicroGreen
  are **side-branches** off the main provisioning chain — they explore silicon/design
  alternatives, then we return to the server story.
