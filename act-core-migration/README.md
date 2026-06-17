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
- **C2 (superset act_core + port MicroGreen): IN PROGRESS.**
  - DONE: `EmbodiedCarbonModeling` initialized; its broken `location.yaml` symlink fixed
    (relative) — commit `42cfed5` on its `act-core` branch (pushed) — so it runs again; 14
    IoT/device BOM baselines captured in `baselines/microgreen/`.
  - VERIFIED DELTAS (ECM vs act_core, all confirmed by diff): **enums are pure additions** —
    `SourceType` +6 (DIODE/RESISTOR/CAPACITOR/SWITCH/INDUCTOR/ACTIVE), `LogicProcess` +3
    (180/130/90nm), `ComponentCategory` +8. **Data are additive supersets** — logic epa/gpa
    add legacy nodes (overlapping rows identical), materials adds tin/bronze/aluminum/
    pb_free_solder, capacitors adds package factors 0201–0805 (energy values preserved).
    Plus **7 new component models** (active/connector/diode/inductor/other/resistor/switch).
    The ONLY behavioral delta: capacitor→`CAPACITOR` & PCB→`PCB` (vs ACT's `PASSIVES` &
    `FABRICATION`); `bom.py` differs by 74 additive lines (extra ComponentSpecs + dispatch).
  - REMAINING PORT (next increment): (1) adopt superset enums + data + 7 models into act_core;
    (2) add a SourceType **policy** to capacitor_model/pcb_model — default PASSIVES/FABRICATION
    (keeps ACT green), ECM sets CAPACITOR/PCB; (3) superset `bom.py`; (4) port ECM's frontend to
    import act_core (delete its `act/core`+`act/models`), policy=CAPACITOR/PCB, keep IoT BOMs;
    (5) verify ACT ci_script + baselines byte-identical AND ECM's 14 baselines reproduce;
    (6) commit+push act_core (ACTv2) + ECM, repoint the EmbodiedCarbonModeling pin.
- **C3** (EServe convergence + vendor re-validation — needs the HBM-basis decision / domain
  sign-off), **C4** (wire suite to `act_core`): pending.
