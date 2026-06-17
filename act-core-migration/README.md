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
  baselines are deferred to C2 (captured when that nested submodule is initialized).
- C1–C4: pending (see plan).
