# Segment 4 — MicroGreen: the carbon-optimal edge MCU is NOT fixed — it flips

**Story beat.** The old slide showed a static per-board embodied bar and stopped there —
but that bar is the paper's *motivation* (Fig. 3), the **strawman**, not the
contribution. MicroGreen is a carbon-aware **design-space-exploration** framework: it
**jointly** models embodied carbon (board + solar panel + super-caps + batteries) **and**
operational carbon to pick the carbon-optimal **{MCU + power-system}** for a given
*workload × light × inference-rate × lifetime*. Its real finding (Fig. 6): the
carbon-optimal MCU **flips** as those conditions change — by **>1 order of magnitude** —
and the **most energy-efficient processor is not the carbon winner**.

**Run it:** `make demo-microgreen`  (or `walkthrough/04_microgreen/run.sh`) — runs
MicroGreen's *own* sweep `scripts/overall_eval_carbon.py` (~1 min, lifetime 1 yr, solar
cap 611 cm²), then computes the min-carbon device at every operating point.

**Headline.** *The carbon-optimal edge MCU is not fixed — it flips
(**RP2350 ⇄ NXP RT1176+TPU**) with light, inference rate, and lifetime; energy-efficiency
does **not** predict the carbon winner.*

**The flip** (workload `kws-l`, *total* kgCO2e, winner in **bold**):

| `kws-l` | ~0.5 IPS | ~1 IPS | ~10 IPS |
|---|---|---|---|
| **Dim** (200 µW/cm²) | **RP2350 — 1.37** | **NXP RT1176+TPU — 1.78** | **NXP RT1176+TPU — 6.04** |
| **Medium** (10 000) | **RP2350 — 0.59** | **RP2350 — 0.61** | **RP2350 — 0.94** |
| **Bright** (40 000) | **RP2350 — 0.58** | **RP2350 — 0.59** | **RP2350 — 0.70** |

→ In **Dim** light the winner flips RP2350 → NXP RT1176+TPU at just **~0.66 IPS**; in
brighter light RP2350 wins everywhere. The winner moves with **both** light **and** rate.
The fussier `kws-s` workload has **four** different winners across conditions
(nRF52840 / RP2040 / RP2350 / NXP RT1176+TPU).

**Naive view it overturns** (the strawman, paper Fig. 3): a static per-board embodied
ranking — 8 boards, **nRF52840 (0.175 kg)** … **Coral/NXP-class (1.14 kg, IC ≈ 78%)** —
that says "just pick the lightest board, avoid the heavy ML one." Yet the **heaviest**
processor (NXP RT1176+TPU) becomes the *carbon-optimal* choice in dim light at ≥~1 IPS,
because it finishes inferences fast enough to slash solar-panel + battery embodiment.

**Figures:**
- `figures/microgreen_carbon_optimal_flip.png` — **the payoff:** carbon-optimal device vs
  inference rate for `kws-l` and `kws-s` across Dim/Medium/Bright. The thick line is the
  winner (lowest total carbon); it changes colour/device across panels and within Dim.
- `figures/figure6_overall_device_carbon_rank_lifetime1.0_solarcap611.pdf` — MicroGreen's
  own Fig. 6 (device carbon-rank vs IPS × light), reproduced by the sweep.
- `figures/microgreen_board_carbon.png` — the **naive** static per-board embodied bar
  (the setup the flip overturns).

**What to say (slide bullets):**
- **The winner flips.** Same workload, change only the light or the inference rate and the
  carbon-optimal MCU changes — by >10×. There is no single "greenest edge chip."
- **Energy-efficiency ≠ carbon winner.** The efficiency spread across MCUs is huge
  (**3.4×–186×**), yet it doesn't pick the winner: NXP RT1176+TPU is the *most*
  energy-efficient for `kws-l` (1.13 mJ/inf), but the **3.4× less-efficient RP2350** wins
  on total carbon in Medium/Bright light. Optimising J/inference optimises the wrong thing.
- **Embodied vs operational is the real knob.** Solar + super-caps + batteries (operational
  harvesting/storage) trade against board silicon (embodied); the optimum depends on how
  much energy the environment hands you, which is *why* it flips.
- **Scale-invariance proof point.** This is the **same** embodied-vs-operational
  co-optimization seen everywhere in the stack — shown here at the edge boundary where
  **embodied dominates (~75%)**. It is the **mirror image** of the data center
  (operational-dominated) that EServe pins down next: identical method, opposite balance.

**Scale-invariance framing.** Don't read MicroGreen as a disconnected edge side-branch
(grams, not server kg, so it hands no unit to the provisioning chain). Read it as the
**embodied-dominated extreme** of one recurring trade-off. ACT/iMeC give you the embodied
numbers; MicroGreen and EServe show that *which* term dominates — and therefore what you
should optimise — depends on scale and operating regime, not on the chip alone.

**Honesty caveat (read before you cite).** This segment reproduces MicroGreen's carbon
**model and sweep** (the flip). It does **not** reproduce the paper's headline **47%**
heterogeneous-deployment case study — that needs an extra simulation step
(`framework/heterogeneousDeployment.py`), a Streamlit plotter, and an uncommitted results
CSV. Offered as optional future work; **do not claim 47%** from this artifact.

**Linkage.**
- ← **Segment 3 (COFFEE):** explored a *silicon* design alternative (FeFET memory). Here we
  zoom out from the chip to the **whole device + power system** and let carbon pick it.
- → **Segment 5 (EServe):** the *same* embodied-vs-operational balance, **flipped** from the
  embodied-dominated edge to the (usually) operational-dominated data center — unless the
  grid is clean, which is exactly the regime EServe corners.
