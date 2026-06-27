# Segment 5 — EServe / EcoServe: provisioning is a carbon decision

**Story beat.** The naive slide shows only the H100 GPU's embodied breakdown — the
*small* half, and it misses the point. **EcoServe** is a carbon-aware LLM-serving
**provisioning** framework, and its real lesson is about what you rack and where: the
**host**, not the GPU, dominates embodied carbon, and on a **clean grid** the carbon
spent *building* the box outweighs everything you ever spend *running* it. We drive
EServe's own GPU **and** CPU carbon calculators on the committed H100 HGX config.

(Mirror of segment 4 — MicroGreen — at the other end of the stack: tiny edge devices are
embodied-dominated; the data center is operational-dominated on essentially every real
grid — **flipping to embodied only on the very cleanest grids (<~11 g/kWh, below even
Sweden)**, the narrow regime this segment pins down.)

**Run it:** `make demo-eserve`

**Headline.** *The **host** dominates embodied carbon (~1,084 kg, DRAM-led, vs the GPU's
~103) — Obs 2 is rock-solid. The grid then sets the embodied-vs-operational balance: this
big-host node's crossover is only ~11 gCO2e/kWh, so operational dominates on essentially
every real grid (~1.5× on clean Sweden up to ~44× on dirty California); building outweighs
running only in the cleanest pockets (<~11) or on a lighter node (crossover ~18, above
Sweden). So what to optimize, and what to provision, depends on the grid and the node — not
just the GPU.*

**Obs 2 — embodied is a *host* problem** (per accelerator, EServe's own calculators):

| Component | kgCO2e |
|---|---|
| GPU (full H100, GPUCarbonCalculator) | 103 |
| Host SSD (22.7 TB) | 227 |
| Host DRAM (2 TB) | 580 |
| **Host total** (CPU board + DRAM + SSD) | **1,084** |

→ host ≈ **91%** of one accelerator's embodied; storage+DRAM alone (~807) ≈ **8×** the GPU's ~103.
SSD is priced on `act_core`'s shared bare-die NAND (nand_10nm, as ACT/MicroGreen), so the host is
**DRAM-led** (DRAM 580 > SSD 227).

**Obs 3 — the grid (and the node) decide** (8-GPU node, ~6 kW, 80% util, 4-yr life):

| Carbon rate | gCO2e/hr |
|---|---|
| **Embodied** (manufacturing, amortized) | **54** |
| Operational @ CI 17 (clean — Sweden) | 81 |
| Operational @ CI 261 (world avg) | 1,242 |
| Operational @ CI 501 (high — California) | 2,385 |

→ crossover at **~11 gCO2e/kWh** — *below* every real grid here (even Sweden's 17), so operational
dominates ~1.5×–44× across them; manufactured carbon outweighs all operational only below ~11.

**Figures:** `figures/eserve_host_vs_gpu.png` (the GPU bar dwarfed by host DRAM+SSD) and
`figures/eserve_embodied_vs_operational.png` (the ~11 g/kWh crossover, three grids marked).

**What to say (slide bullets):**
- **(Obs 2) The accelerator is the small half.** An LLM-serving host carries 2 TB of DRAM
  and 22.7 TB of SSD; that storage+memory alone is ~8× the GPU's embodied carbon — and is now
  DRAM-led, since SSD is priced on act_core's bare-die NAND. Provisioning carbon is a **host**
  problem, not a GPU problem.
- **(Obs 3) Embodied is fixed the day the node ships** (~54 g/hr amortized). The crossover is
  ~11 g/kWh — *below* every real grid, so operational dominates everywhere this node runs: ~1.5×
  on a clean grid (Sweden 17, ~81 g/hr) up to ~44× on a dirty one (California 501). Building
  outweighs running only in the very cleanest pockets (<~11) — or on a lighter, lower-power node,
  whose crossover rises back above clean grids (the A100 capstone lands at ~18, above Sweden).
- **So what to optimize — and what to provision — depends on the grid, not just the GPU.**
- **Lifecycle hinge.** This is the server-provisioning joint: it turns manufactured-component
  carbon (ACT/iMeC feed the SoC and the host die) into a *provisioning* decision, and its
  time-allocated per-node carbon is exactly what Fair-CO2 attributes to queries next.

**Honesty note (read before you cite a number).**
- Only EcoServe's **Section-3 carbon model** is committed here; the Section-4 "4R" ILP optimizer
  — the paper's **47%** headline — is **not**. We demo the *Observations*, not the optimization:
  **do not claim 47%.**
- **GPU memory now uses the paper-backed HBM3e = 0.24 kgCO2e/GB** (EcoServe Table 1, via the
  shared `act_core` memory model), so the H100 GPU embodied is **~103 kg** (memory ~19.2).
  The earlier 154 kg used an *unsourced* 0.85; see `act-core-migration/baselines/eserve/`.
- **Lead with ratios/directions** — host ≈ 91%, storage+DRAM ≈ 8× the GPU, crossover ≈ 11 g/kWh.

**Then: hands-on (≈20 min, see `TUTORIAL.md`).** Participants drive EServe's own calculators: read the
H100's embodied breakdown → compare/edit a GPU config (memory tech, lifetime) → add the **host** and see
it dominate (~8×, DRAM-led) → sweep the **grid** to the ~11 g/kWh crossover → provision a node for their
own deployment. The point to convey: the host is the **server you modeled in ACT (segment 1)** — and what
you provision, and where, is a carbon decision the grid (and the node) settle.

**Hands off to:**
- ← **Segment 4 (MicroGreen):** the embodied-vs-operational balance, now flipped to the data center.
- → **Segment 6 (Fair-CO2):** the server's embodied carbon (`inputs/from_05_eserve.json`:
  GPU 103 + host 1,084 → node **~1,908** kgCO2e), to be fairly split across co-located jobs.
