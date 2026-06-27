# Expected results — segment-6 Fair-CO2 tutorial

Reference numbers. The attribution reuses Fair-CO2's real `peak_shapley`
(`Fair-CO2/forecast/emb_shapley_lib.py`); recompute with `./tutorial.sh …` from `walkthrough/06_fairco2/`.

## Stage 1 — the verdict (`make demo-fairco2`)
RUP deviates from the fair Shapley share by **80.3% avg / 279% worst**; Fair-CO2 → **19.1% / 54.8%**
(≈4.2–5.1×), at **~600,000×** less compute. (Fair-CO2's committed 10k-sim Monte-Carlo result.)

## Stage 2 — neighbor swing (`--swing <workload>`)
`llama`: isolated **0.161** vs with-spark **0.080** gCO2e → **2.02×** swing. `spark`: **2.06×**.

## Stage 3 — attribute a shared node (`--workloads exercises/workloads.json`, budget = R740 1523.1 kg)
| job | RUP (proportional) | fair (Shapley) | RUP error |
|---|---|---|---|
| llama (LLM serving) | **507.7** | **957.4** | 47% under |
| spark (batch ETL) | **761.5** | **261.1** | **192% over** |
| faiss (index build) | **253.8** | **304.6** | 17% under |

The batch job (high resource-time, low peak) is over-charged ~3× by RUP; the spiky serving job that
drives the peak is under-charged. Editing `peak`/`resource_time` moves the over/under-charging.

> The fair split is Fair-CO2's `peak_shapley`; the Stage-1 headline is its committed Monte-Carlo output.
> The heavy simulation and any downstream optimizer are not run here.
