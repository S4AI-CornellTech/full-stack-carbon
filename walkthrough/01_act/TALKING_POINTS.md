# Segment 1 — ACT: a server is designed

**Story beat.** Where the data center's carbon story begins — *before a single
watt is drawn*. We hand ACT a bill-of-materials for a Dell PowerEdge R740 and ask
how much carbon was emitted just to **manufacture** it.

**Run it:** `make demo-act`  (or `walkthrough/01_act/run.sh`)

**Headline number: ~1,523 kgCO2e** embodied in one R740 — dominated by storage:

| Component class | Embodied carbon |
|---|---|
| SSD (8× high-capacity) | ~1,120 kgCO2e |
| DRAM (12× + cache) | ~380 kgCO2e |
| CPU (2× 28 nm dies) | ~23 kgCO2e |

**Figure:** `figures/act_r740_breakdown.png` — embodied carbon by component class.

**What to say (slide bullets):**
- Embodied (manufacturing) carbon is fixed the day the hardware ships — paid up
  front, independent of how the server is later used.
- ACT computes it bottom-up from the BOM: die area × process-node carbon-per-area
  for logic, per-GB carbon for DRAM/SSD, plus packaging, PCB and materials.
- Counter-intuitive result: **storage, not the CPU, dominates** this server's
  embodied footprint — eight high-capacity SSDs swamp the 28 nm CPU dies.
- These same primitives are reused or refined by every other tool in the suite.

**Hands off to:**
- → **Segment 2 (COFFEE):** what if the chips used emerging FeFET memory instead?
- → **Segments 5 (EServe) & 6 (Fair-CO2):** the per-component server budget, in
  `figures/result.json` and committed to those segments' `inputs/from_01_act.json`.

**Honesty note.** The R740 BOM here is illustrative (28 nm / 6.98 cm² / coal grid).
The per-CPU figure Fair-CO2 uses downstream (18,530 gCO2e) was computed by ACT for
the node's *actual* Xeon Gold 6240R — same method, different inputs. See segment 6.
