# Workstream C — act-core unification (working area)

Goal: carve a shared **`act_core`** package out of ACT and converge the three
ACT-derived codebases — ACT, MicroGreen's `EmbodiedCarbonModeling`, and EServe —
onto it. Full design: `/home/leo/.claude/plans/our-lab-has-a-wobbly-simon.md`
(Workstream C). This directory holds the regression safety net + notes. All C work
is on the **`act-core`** branch; `suite-assembly` / tag `v0.1.0` stay as the stable
reframed walkthrough.

> **Note (later):** the cross-tool `walkthrough/` was since **removed** from the suite once the hands-on
> tutorials moved into the tool repos (ACT/EServe/Fair-CO2 `tutorial/`). The `make all-demos` /
> `make demo-*` / "walkthrough segment" references below are historical (they were the regression check
> at migration time); the live regression net is now `make tutorial-act/eserve/fairco2` + the baselines
> here. The walkthrough is preserved at tag `v0.1.0`.

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
  - **act_core SUPERSET DONE** (ACTv2 `act-core`, commit `5d07fe7`, pushed): adopted the superset
    enums + data + 7 component models + bom/materials/utils; added the capacitor/pcb `source_type`
    policy (default ACT `PASSIVES`/`FABRICATION`; ECM will set `CAPACITOR`/`PCB`). ACT verified
    **byte-identical** (ci_script + all 4 BOM totals; the report merely lists the 6 new SourceTypes
    as 0). logic_model/storage_model kept as ACT's (IC packaging in-model, no yield division).
  - **ECM PORT DONE** (EmbodiedCarbonModeling `act-core`, commit `d9fd240`, pushed):
    made act_core **pip-installable** (pyproject + `__init__.py`; ACTv2 `3046ecf`); added an
    `add_ic_packaging` flag + re-adopted ECM's `world_cpa` lookup in logic_model (both inert for
    ACT — verified byte-identical, all 4 ACT totals + ci_script). Rewired ECM's frontend to import
    act_core, **deleted its `act/core`+`act/models` fork**, set capacitor/pcb policy=CAPACITOR/PCB
    and silicon `add_ic_packaging=False` (frontend supplies MANUAL packaging /fab_yield).
    **All 14 ECM BOMs reproduce their baselines byte-for-byte.** ACT + MicroGreen now share one core.
  - These folded into C4 (done): ECM pin repointed (MicroGreen `act-core` `7f03583`), suite gitlinks
    bumped, `bootstrap.sh` installs act-core editable into the eserve + microgreen envs.
- **C3 (EServe convergence): DONE** (EServe `act-core`: memory `d38bf93`, SSD `94d2a9a`).
  - **Memory** converged onto `act_core.MemoryModel` using the **paper-backed HBM3e = 0.24**
    (EcoServe Table 1; the GPU's 0.85 was unsourced and absent from the paper). GPU + CPU now
    self-consistent. Only HBM3/HBM3E GPUs change (H100 full embodied 154 → ~103).
  - **SSD (2026-06-27)** converged onto `act_core.SSDModel` at **nand_10nm = 10 g/GB** (the bare-die
    NAND source ACT/MicroGreen use), replacing the whole-device 0.10999. H100 HGX host SSD 2,499 → 227 kg
    (host now DRAM-led; total 3,355 → 1,084 kg); embodied↔operational crossover 25.1 → 11.4 gCO2e/kWh
    (Obs 3 reframed — below real grids). Fair-CO2 was aligned to the same coefficient on its `act-core`
    branch (`f4e2f53`; its deviation/2× swing headline is scale-invariant, unchanged).
  - EServe tests pass; deltas in `baselines/eserve/c3_convergence_deltas.md`; walkthrough segment 5
    refreshed. **SoC/PDN/cooling** kept EServe-specific (documented follow-ups).
- **C4 (wire suite): DONE** (suite `act-core` `cc465ce`). `bootstrap.sh` installs act-core editable;
  `.gitmodules` tracks the act-core branch; gitlinks bumped (ACT `8764d6a`, EServe `d38bf93`,
  MicroGreen `7f03583`). `make all-demos` is green on the unified suite; submodules clean.

## Workstream C COMPLETE (+ SSD convergence)
All three ACT lineages — ACT, MicroGreen/EmbodiedCarbonModeling, and EServe — now share the single
`act_core` package (pip-installable; ACT also uses it via PYTHONPATH). ACT is byte-identical, ECM's 14
BOMs reproduce, and EServe's **memory + SSD** carbon are converged onto act_core (Fair-CO2's SSD too).
The tool repos stay on their **`act-core`** branches (pushed to origin for review) — **nothing is merged
to any tool repo's `main` / no PRs**, per the collaborator-review constraint. The suite
(full-stack-carbon), a new repo, has been promoted (`main` fast-forwarded to `act-core`) and pushed to
origin. The stable `suite-assembly` / `v0.1.0` walkthrough snapshot is untouched.
