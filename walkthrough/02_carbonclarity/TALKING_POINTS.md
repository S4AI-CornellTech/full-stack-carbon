# Segment 2 — CarbonClarity: that single number is the *mean* of a distribution

**Story beat.** Segment 1 (ACT) handed us *one* embodied-carbon number per chip. But
the fab inputs ACT plugs in — energy-per-area (EPA), gas-per-area (GPA), grid
carbon-intensity (CI) and yield — are all uncertain. CarbonClarity samples them
instead of fixing them, turning ACT's point into a **distribution** of carbon-per-area.
The punchline isn't "ACT is wrong"; it's *which* number you should report, and how
that choice gets riskier at advanced nodes.

**Run it:** `make demo-carbonclarity`  (or `walkthrough/02_carbonclarity/run.sh`)

**Headline — logic carbon-per-area, per cm² (so nodes compare directly):**

| Node | mean = ACT plug-in | 95th pct = report this | p95/mean | P(actual > mean) |
|---|---|---|---|---|
| 28 nm\* | 1.06 | 1.46 | 1.39×\* | 49% |
| 10 nm | 1.66 | 2.11 | 1.27× | 51% |
| 7 nm | 2.09 | 2.70 | 1.29× | 47% |

*(kgCO2e/cm²; \*28 nm has no committed yield distribution — see caveat.)*

**One line:** ACT gives the **mean** — real embodied carbon exceeds it **~half the
time**; the number you should **report** (95th percentile) is **~1.3× higher**, and
**both the carbon and its uncertainty grow toward advanced nodes**.

**Figure:** `figures/carbonclarity_node_risk.png` — per-node violins of the CPA
distribution with the ACT-mean (solid) and reportable p95 (dashed) marked, p95/mean
annotated, ordered mature → advanced.

**What to say (slide bullets):**
- Embodied carbon is a **distribution, not a point.** CarbonClarity reuses ACT's
  EPA/GPA/CI/yield primitives but *samples* them, producing a band of carbon-per-area
  rather than a single value.
- ACT's deterministic number lands at **~the mean** of that band — so the true value
  **exceeds it roughly half the time** (P>mean ≈ 47–51%). It is a coin-flip, **not a
  lowball**.
- **Report the 95th percentile, not the mean.** The conservative figure runs **~1.3×**
  the mean (1.27–1.39× here) — that's the number that belongs in a disclosure.
- **Advanced silicon is dirtier *and* less certain.** Per cm², the mean climbs
  1.06 → 2.09 kg and the spread (σ) widens 0.24 → 0.33 kg from 28 nm to 7 nm; the
  mean→p95 gap grows 0.41 → 0.61 kg. The clean 10 nm→7 nm pair shows the p95/mean
  inflation ticking up too (1.27× → 1.29×).

**Honesty caveat.**
- The committed input JSONs are **100-sample KDE resamples**, narrower than the paper's
  figures — so **do not quote the paper's "1.6×"** off this recompute. The fully clean
  comparison (committed EPA+GPA+CI+yield) is the **10 nm vs 7 nm** pair.
- **28 nm has no committed yield distribution**, so we plug a deterministic yield. That
  omits yield variance and **understates** 28 nm's uncertainty — its 1.39× is inflated
  by a near-zero EPA sample, not directly comparable, hence the asterisk.
- We deliberately **dropped** the old "ACT is optimistic / below the median" framing: it
  was factually fragile. ACT ≈ the mean, full stop.

**Inputs.** Committed 28/10/7 nm EPA/GPA/CI/yield distributions in
`inputs/all_distribution/` (CarbonClarity's `distribution_gen/` output, frozen for
offline reproducibility — the artifact-evaluation pattern). Per cm², **no die-area
multiply**, for cross-node comparability.

**Relationship.**
- ← **prev, Segment 1 (ACT):** ACT produced the single embodied number; here we show it
  is the *mean* of a band and hand back the figure you should actually report (p95).
- → **next, Segment 3 (COFFEE):** branches to emerging FeFET memory, layering on ACT's
  *same* 28 nm CMOS EPA table — the very baseline whose uncertainty this segment just
  quantified. The same machinery bounds any advanced-node die downstream (e.g. the
  H100's SoC in Segment 5).
