# Segment 4 — MicroGreen: the edge tier (a side-branch)

**Story beat.** Data centers don't exist in isolation — data is collected by edge/IoT
devices first. MicroGreen applies the *same* ACT-based embodied-carbon method to
microcontroller boards. (A parallel branch: grams, not server kilograms.)

**Run it:** `make demo-microgreen`  (or `walkthrough/04_microgreen/run.sh`)

**Headline.** Across 8 edge MCU boards, embodied carbon spans **0.175 → 1.141 kgCO2e**:
- Lowest: **nRF52840** (0.175 kgCO2e)
- Highest: **Coral Dev Micro** (1.141 kgCO2e), of which the **IC is ~78%**

**Figures:** `figures/microgreen_board_carbon.png` (per-board totals) and
`figure3_board_carbon_composition_stacked_bar.pdf` (MicroGreen's own component breakdown).

**What to say (slide bullets):**
- The same bottom-up, BoM-based embodied-carbon method scales from data-center servers
  (kg, segment 1) down to coin-cell-class edge devices (sub-kg).
- Just as SSDs dominated the server, the **IC dominates** the heaviest edge board —
  silicon is the recurring carbon hotspot across the whole stack.
- MicroGreen runs on a heavily-extended ACT fork (EmbodiedCarbonModeling) — one of the
  three ACT lineages the act-core unification (workstream C) consolidates.

**Branch note.** This is the upstream edge tier, shown for contrast; it doesn't feed a
unit into the server provisioning chain.
