# Workstream C — act-core unification (working area)

Goal: carve a shared **`act_core`** package out of ACT and converge the three
ACT-derived codebases — ACT, MicroGreen's `EmbodiedCarbonModeling`, and EServe —
onto it. Full design: `/home/leo/.claude/plans/our-lab-has-a-wobbly-simon.md`
(Workstream C). This directory holds the regression safety net + notes. All C work
is on the **`act-core`** branch; `suite-assembly` / tag `v0.1.0` stay as the stable
reframed walkthrough.

## Baselines (captured BEFORE any refactor — the regression net)
- `baselines/act/<bom>/act_report.yaml` — ACT report for each BOM (dellr740,
  fairphone3, test, imported). `ACT/ci_script.sh` passes at capture time.
- `baselines/eserve/gpu_components_baseline.json` — per-GPU full-embodied component
  breakdown (memory / PCB / PDN / cooling / SoC / connection + sum) for all 11 GPUs
  in `gpuconfigs.json`. EServe `pytest tests` (6 tests incl `test_h100_validation`)
  passes at capture time (pytest installed ad-hoc into `.envs/eserve`).

## Regression check (run after each refactor step — nothing may drift)
- **ACT:** `cd ACT && PYTHONPATH=. ../.envs/act/bin/python -m act.act_model -m act/boms/<bom>.yaml -o /tmp/chk`, then diff `/tmp/chk/act_report.yaml` vs `baselines/act/<bom>/act_report.yaml`; and `bash ACT/ci_script.sh`.
- **EServe:** re-capture the component JSON and diff vs `baselines/eserve/...`; and `pytest tests` (lock `test_h100_validation`).
- **Walkthrough:** `make all-demos` must stay green (the ACT CLI surface is preserved throughout).

## Status
- **C0 baselines:** ACT + EServe captured. MicroGreen / `EmbodiedCarbonModeling`
  baselines deferred to C2 (captured when that nested submodule is initialized).
- **C1 (carve act_core):** DONE — ACT submodule branch `act-core`, commit `96292d8`
  (local, not yet pushed to ACTv2). `act/core`→`act_core`, `act/models`→`act_core/models`;
  ACT frontend + tests import `act_core`; `ACT_ROOT` now = the `act_core` dir. Verified:
  `ci_script.sh` passes, report carbon numbers byte-identical to baselines,
  `from act_core... import` works, `make demo-act` green. The suite gitlink is **not**
  bumped yet (deferred to C4, together with pushing the ACTv2 `act-core` branch).
- **C2** (superset enums/data + passives registry; port MicroGreen, repoint
  EmbodiedCarbonModeling), **C3** (EServe convergence + vendor re-validation — needs the
  HBM-basis decision / domain sign-off), **C4** (wire suite to `act_core`): pending.
