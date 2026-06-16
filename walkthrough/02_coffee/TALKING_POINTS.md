# Segment 2 — COFFEE: the cost of emerging memory (a side-branch)

**Story beat.** A what-if branching off segment 1's silicon: what if the chip used
emerging **HZO FeFET** non-volatile memory instead of conventional CMOS? COFFEE
extends ACT's *same* CMOS energy-per-area table with the ferroelectric layer (FEL)
that FeFET adds via Atomic Layer Deposition (ALD).

**Run it:** `make demo-coffee`  (or `walkthrough/02_coffee/run.sh`)

**Headline.** For the HZO_5 device at 28 nm, the ferroelectric layer adds **+20%**
energy-per-area over the CMOS baseline:

| | EPA (kWh/cm²) |
|---|---|
| CMOS 28 nm (ACT baseline) | 0.90 |
| FeFET HZO_5 (CMOS + FEL) | 1.08 |
| FEL / ALD process energy | 18.26 kWh |

**Figure:** `figures/coffee_epa_overhead.png`.

**What to say (slide bullets):**
- COFFEE reuses ACT's CMOS process-node table — the 28 nm EPA here is the *same*
  number ACT used in segment 1 — and layers the FeFET ALD process on top: one tool
  literally extending another's primitives.
- Emerging memory isn't carbon-free: the ALD ferroelectric stack carries a real
  fabrication-energy overhead, to be weighed against its endurance/efficiency wins.
- This is a *branch*, not a step in the provisioning chain — it explores a silicon
  design alternative, then we return to the main story.

**Relationship.** Shares ACT's 28 nm CMOS baseline (segment 1); the *uncertainty* in
that baseline is exactly what segment 3 (CarbonClarity) quantifies.
