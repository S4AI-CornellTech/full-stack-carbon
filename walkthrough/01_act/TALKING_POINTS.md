# Segment 1 — ACT: one number to start (and to question)

**Story beat.** Where the story begins: a single, deterministic embodied-carbon
number for a server, computed bottom-up from its bill-of-materials. It's the
foundation every other tool builds on — and the number the rest of the walkthrough
will complicate, because *one number is never the whole answer*.

**Run it:** `make demo-act`  (or `walkthrough/01_act/run.sh`)

**Headline: ~1,523 kgCO2e** embodied in one Dell R740 — storage-dominated:

| Component class | Embodied carbon |
|---|---|
| SSD (8× high-capacity) | ~1,120 kgCO2e |
| DRAM | ~380 kgCO2e |
| CPU (2× 28 nm dies) | ~23 kgCO2e |

This is **embodied (manufacturing) carbon only** — fixed the day the hardware ships.
Operational carbon (running it) is separate and depends on *how* and *where* it's
used. That split — **embodied vs operational** — is the thread through the whole
walkthrough.

**Figure:** `figures/act_r740_breakdown.png`.

**What to say (slide bullets):**
- ACT is the **foundation**: bottom-up BoM carbon (die area × process-node
  carbon-per-area for logic, per-GB for memory/storage, plus packaging/PCB/materials).
  COFFEE, CarbonClarity, MicroGreen and EServe all reuse or extend these primitives.
- It returns **one deterministic number** — and the rest of the suite exists because
  that number is, by turns: actually a **distribution** (CarbonClarity), the wrong
  axis for a **memory-tech trade-off** (COFFEE), not **fixed across deployments**
  (MicroGreen), the **small half** of the real total (EServe), and hard to **attribute
  fairly** (Fair-CO2).
- Even here the naive intuition is wrong: **storage, not the CPU, dominates** this
  server's embodied footprint.

**Hands off to:**
- → **Segment 2 (CarbonClarity):** is 1,523 kg *the* number, or the middle of a wide
  distribution? (It's the latter.)
- → **Segments 5 (EServe) & 6 (Fair-CO2):** the per-component server budget, committed
  to their `inputs/`.
