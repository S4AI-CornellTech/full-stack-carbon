# Segment 5 — EServe / EcoServe: provisioning is a carbon decision

**Story beat.** The old version of this slide showed only the H100 GPU's ~154 kg
embodied breakdown — the *small* half, and it missed the point. **EcoServe** is a
carbon-aware LLM-serving **provisioning** framework, and its real lesson is about
what you rack and where: the **host**, not the GPU, dominates embodied carbon, and
on a **clean grid** the carbon spent *building* the box outweighs everything you
ever spend *running* it. We drive EServe's own GPU **and** CPU carbon calculators
on the committed H100 HGX config to show both.

(Mirror of segment 4 — MicroGreen — at the other end of the stack: tiny edge
devices are embodied-dominated; the data center is *usually* operational-dominated
— **unless the grid is clean**, which is exactly the regime this segment pins down.)

**Run it:** `make demo-eserve`  (or `walkthrough/05_eserve/run.sh`)

**Headline.** *The **host** dominates embodied carbon (~3,355 kg, storage+DRAM-heavy,
vs the GPU's 154); and below ~27 gCO2e/kWh a clean grid makes embodied outweigh ALL
operational — so what to optimize, and what to provision, depends on the grid, not
just the GPU.*

**Obs 2 — embodied is a *host* problem** (per accelerator, EServe's own calculators):

| Component | kgCO2e |
|---|---|
| GPU (full H100, GPUCarbonCalculator) | 154 |
| Host DRAM (2 TB) | 580 |
| Host SSD (22.7 TB) | 2,499 |
| **Host total** (CPU board + DRAM + SSD, CPUCarbonCalculator) | **3,355** |

→ host ≈ **95.6%** of one accelerator's embodied; storage+DRAM alone (~3,079) ≈ **20×** the GPU's 154.

**Obs 3 — the grid decides** (8-GPU node, ~6 kW, 80% util, 4-yr life):

| Carbon rate | gCO2e/hr |
|---|---|
| **Embodied** (manufacturing, amortized) | **131** |
| Operational @ CI 17 (clean — Sweden) | 81 |
| Operational @ CI 261 (world avg) | 1,242 |
| Operational @ CI 501 (high — California) | 2,385 |

→ crossover at **~27 gCO2e/kWh** (27.5 computed): below it, manufactured carbon outweighs ALL operational.

**Figures:**
- `figures/eserve_host_vs_gpu.png` — the GPU bar (154) dwarfed by host SSD (2,499)
  and DRAM (580) (Obs 2).
- `figures/eserve_embodied_vs_operational.png` — flat amortized-embodied line vs the
  rising operational line across grid carbon intensity, with the ~27.5 g/kWh crossover
  and the three grids (Sweden / world-avg / California) marked (Obs 3).

**What to say (slide bullets):**
- **(Obs 2) The accelerator is the small half.** An LLM-serving host carries 2 TB of
  DRAM and 22.7 TB of SSD; that storage+memory alone is ~20× the GPU's embodied carbon.
  Provisioning carbon is a **host** problem, not a GPU problem.
- **(Obs 3) Embodied is fixed the day the node ships** (~131 g/hr amortized). On a clean
  grid (Sweden, 17 g/kWh) operational is only ~81 g/hr — and below ~27 g/kWh the
  *manufacturing* outweighs everything you ever spend running it. On a dirty grid
  (California, 501 g/kWh) operational dominates embodied ~18×.
- **So what to optimize — and what to provision — depends on the grid, not just the GPU.**
  Clean grid → minimize embodied (right-size the host, extend lifetime, reuse). Dirty grid
  → operational dominates and energy efficiency wins.
- **Lifecycle hinge.** This is the server-provisioning joint of the stack: it turns
  manufactured-component carbon (ACT/iMeC feed the GPU SoC and the host die) into a
  *provisioning* decision, and its time-allocated per-node carbon is exactly what
  Fair-CO2 attributes to individual queries next.

**Honesty note (read before you cite a number).**
- Only EcoServe's **Section-3 carbon model** is committed here; the Section-4 "4R" ILP
  optimizer — the paper's **47%** headline — is **not**. So we demo the *Observations*,
  not the optimization: **do not claim 47%.**
- **Lead with ratios/directions** — host ≈ 95%, storage+DRAM ≈ 20× the GPU, crossover
  ≈ 27 g/kWh. The artifact's absolute per-part numbers don't match the paper to the digit
  (host SSD/DRAM coefficients, and a placeholder ACT-Table-12 constant for the CPU die),
  but the directional findings are robust.

**Hands off to:**
- ← **Segment 4 (MicroGreen):** the embodied-vs-operational balance, now flipped from the
  edge tier to the data center.
- → **Segment 6 (Fair-CO2):** the server's embodied carbon
  (`inputs/from_05_eserve.json`: GPU 154 + host 3,355 → node **4,589** kgCO2e), to be
  time-allocated and fairly split across co-located Llama + Spark jobs.
