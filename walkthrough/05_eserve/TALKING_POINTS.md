# Segment 5 — EServe / EcoServe: provisioning is a carbon decision

**Story beat.** The naive slide shows only the H100 GPU's embodied breakdown — the
*small* half, and it misses the point. **EcoServe** is a carbon-aware LLM-serving
**provisioning** framework, and its real lesson is about what you rack and where: the
**host**, not the GPU, dominates embodied carbon, and on a **clean grid** the carbon
spent *building* the box outweighs everything you ever spend *running* it. We drive
EServe's own GPU **and** CPU carbon calculators on the committed H100 HGX config.

(Mirror of segment 4 — MicroGreen — at the other end of the stack: tiny edge devices are
embodied-dominated; the data center is *usually* operational-dominated — **unless the
grid is clean**, which is exactly the regime this segment pins down.)

**Run it:** `make demo-eserve`

**Headline.** *The **host** dominates embodied carbon (~3,355 kg, storage+DRAM-heavy, vs
the GPU's ~103); and below ~25 gCO2e/kWh a clean grid makes embodied outweigh ALL
operational — so what to optimize, and what to provision, depends on the grid, not just
the GPU.*

**Obs 2 — embodied is a *host* problem** (per accelerator, EServe's own calculators):

| Component | kgCO2e |
|---|---|
| GPU (full H100, GPUCarbonCalculator) | 103 |
| Host DRAM (2 TB) | 580 |
| Host SSD (22.7 TB) | 2,499 |
| **Host total** (CPU board + DRAM + SSD) | **3,355** |

→ host ≈ **97%** of one accelerator's embodied; storage+DRAM alone (~3,079) ≈ **30×** the GPU's ~103.

**Obs 3 — the grid decides** (8-GPU node, ~6 kW, 80% util, 4-yr life):

| Carbon rate | gCO2e/hr |
|---|---|
| **Embodied** (manufacturing, amortized) | **119** |
| Operational @ CI 17 (clean — Sweden) | 81 |
| Operational @ CI 261 (world avg) | 1,242 |
| Operational @ CI 501 (high — California) | 2,385 |

→ crossover at **~25 gCO2e/kWh**: below it, manufactured carbon outweighs ALL operational.

**Figures:** `figures/eserve_host_vs_gpu.png` (the GPU bar dwarfed by host SSD+DRAM) and
`figures/eserve_embodied_vs_operational.png` (the ~25 g/kWh crossover, three grids marked).

**What to say (slide bullets):**
- **(Obs 2) The accelerator is the small half.** An LLM-serving host carries 2 TB of DRAM
  and 22.7 TB of SSD; that storage+memory alone is ~30× the GPU's embodied carbon.
  Provisioning carbon is a **host** problem, not a GPU problem.
- **(Obs 3) Embodied is fixed the day the node ships** (~119 g/hr amortized). On a clean grid
  (Sweden, 17 g/kWh) operational is only ~81 g/hr — below ~25 g/kWh the *manufacturing*
  outweighs everything you ever spend running it. On a dirty grid (California, 501) operational
  dominates ~20×.
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
- **Lead with ratios/directions** — host ≈ 97%, storage+DRAM ≈ 30× the GPU, crossover ≈ 25 g/kWh.

**Then: hands-on (≈20 min, see `TUTORIAL.md`).** Participants drive EServe's own calculators: read the
H100's embodied breakdown → compare/edit a GPU config (memory tech, lifetime) → add the **host** and see
it dominate (~30×) → sweep the **grid** to the ~25 g/kWh crossover → provision a node for their own
deployment. The point to convey: the host is the **server you modeled in ACT (segment 1)** — and what
you provision, and where, is a carbon decision the grid settles.

**Hands off to:**
- ← **Segment 4 (MicroGreen):** the embodied-vs-operational balance, now flipped to the data center.
- → **Segment 6 (Fair-CO2):** the server's embodied carbon (`inputs/from_05_eserve.json`:
  GPU 103 + host 3,355 → node **~4,179** kgCO2e), to be fairly split across co-located jobs.
