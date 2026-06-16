# Segment 3 — CarbonClarity: how trustworthy is that number?

**Story beat.** Segment 1 gave ACT's *single* embodied-carbon number for the CPU die.
But fab energy, gas, yield, and grid carbon-intensity are all uncertain. CarbonClarity
propagates those uncertainties into a *distribution*.

**Run it:** `make demo-carbonclarity`  (or `walkthrough/03_carbonclarity/run.sh`)

**Headline — R740 CPU die (28 nm, 6.98 cm²):**

| | kgCO2e |
|---|---|
| Median | 7.31 |
| P10–P90 band | 5.15 – 9.62 |
| Mean ± σ | 7.36 ± 1.70 |
| ACT point estimate (seg 1) | 5.78 |

**Figure:** `figures/carbonclarity_cpu_distribution.png` — the distribution with ACT's
point estimate marked.

**What to say (slide bullets):**
- A single embodied-carbon number hides real manufacturing variance; the true value is
  a distribution that can span ~2× from P10 to P90.
- CarbonClarity reuses ACT's EPA/GPA tables (segment 1's primitives) but *samples* them
  as distributions instead of point values.
- ACT's deterministic estimate is plausible but optimistic here — it lands below the
  median, a useful caution when reporting any single figure.

**Inputs.** Committed 28 nm EPA/GPA/CI distributions in `inputs/all_distribution/`
(generated once by CarbonClarity's `distribution_gen/`, then frozen — the
artifact-evaluation pattern).

**Relationship.** Quantifies the uncertainty in segment 1's (and segment 2's CMOS
baseline) numbers; the same machinery bounds advanced-node dies like the H100's 5 nm
SoC in segment 5.
