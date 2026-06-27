# Fair-CO2 — hands-on: split shared carbon fairly (≈20 min)

The data center is built (**ACT**, segment 1) and provisioned (**EServe**, segment 5). Now its embodied
carbon has to be **charged back** to the software that shares the machine. You'll see why the industry's
proportional split is unfair, then attribute a shared server's carbon yourself — the fair way — using
Fair-CO2's own Shapley code. This follows the 5-minute Fair-CO2 intro (`TALKING_POINTS.md`).

The helper:
```bash
cd walkthrough/06_fairco2
./tutorial.sh --workloads exercises/workloads.json   # proportional (RUP) vs fair (Shapley) split
./tutorial.sh --swing llama                          # "your bill depends on your neighbor"
```
Prereq: `make setup` built the `fair-co2` env.

**Two ways to bill shared carbon.** **RUP** (Resource-Utilization-Proportional — the industry default,
= Google's operational accounting + the Green Software Foundation SCI) charges each job in proportion to
its **resource-time** (CPU × runtime). **Shapley** — the provably fair division of a shared cost —
charges each job by its **marginal contribution to the peak** the hardware was built (and embodied) to
serve. They disagree, a lot.

---

## Stage 1 — Read the verdict (≈3 min)

```bash
make demo-fairco2
```
Over Fair-CO2's committed 10,000-simulation results: **RUP misattributes each job by ~80% on average
(up to 279%)** vs the fair Shapley ground truth; **Fair-CO2 cuts that to ~19% (≈4.2×)** — at **~600,000×
less compute** than computing Shapley exactly, which is what makes fair, per-job attribution tractable
at all. The industry-default split isn't slightly off; it's badly unfair.

---

## Stage 2 — The hook: your bill depends on your neighbor (≈4 min)

```bash
./tutorial.sh --swing llama
```
The same Llama-3-8B serving job's attributed embodied carbon **swings ~2× (2.02×)** just from *who it
shares the node with* — **0.161 gCO2e alone** vs **0.080 gCO2e next to Spark** (it splits the shared box
with a neighbor). Try `--swing spark` (2.06×). **Lesson:** a fixed "your share" number can't be right if
it changes depending on your neighbors — attribution has to be *relational*, which proportional billing
can't capture.

---

## Stage 3 — Attribute a shared node yourself (≈8 min)

Three jobs co-locate on one server and share its embodied carbon — ACT's **R740 = 1,523 kg** from
segment 1. Open `exercises/workloads.json`: each job has a `peak` (the demand it drives) and a
`resource_time` (CPU × runtime, what RUP bills by). Run it:

```bash
./tutorial.sh --workloads exercises/workloads.json
```
| job | RUP (proportional) | fair (Shapley) | RUP error |
|---|---|---|---|
| llama (LLM serving) | 507.7 kg | 957.4 kg | **47% under-charged** |
| spark (batch ETL) | 761.5 kg | 261.1 kg | **192% over-charged** |
| faiss (index build) | 253.8 kg | 304.6 kg | 17% under-charged |

**The unfairness, concrete:** Spark is a batch job with the *most* resource-time (so RUP bills it the
most — 50% of the budget) but the *lowest* peak — it never drives the peak the hardware was sized for,
so its fair share is the *smallest* (261 kg). RUP over-charges it ~3×. Meanwhile the spiky Llama serving
job *drives* the peak and is under-charged by RUP. Now **edit the jobs** — bump Spark's `peak`, or drop
Llama's `resource_time` — re-run, and watch the over/under-charging move. (This calls Fair-CO2's real
`peak_shapley`.)

---

## Stage 4 — Capstone: fairly bill your tenants (≈4 min)

Copy `exercises/workloads.json`, put in **your own** co-located tenants (their peak demand + resource
use) and the shared budget (`--budget <kg>`, or keep the upstream R740/H100 embodied carbon), and run:

```bash
./tutorial.sh --workloads exercises/workloads.json --budget 1626   # e.g. R740 1523 + one H100 103
```
The helper reports each tenant's **fair share** and exactly how much RUP over- or under-charges them.
That's the whole suite closing the loop: the carbon **ACT quantified**, **EServe provisioned**, finally
**split fairly** across the jobs that share the machine.

---

## Honesty (say it aloud)

The fair split uses Fair-CO2's **real `peak_shapley`** (`Fair-CO2/forecast/emb_shapley_lib.py`). The
Stage-1 headline (RUP 80% vs Fair-CO2 19%) is Fair-CO2's committed **10,000-sim Monte-Carlo** result —
the heavy simulation is not re-run here, and neither is any downstream carbon optimizer. The point this
hands-on makes is the core one: **proportional billing of shared carbon is unfair, and a Shapley share
fixes it.**
