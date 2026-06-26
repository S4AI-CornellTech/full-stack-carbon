# Contributing & Handoff Guide

One-page orientation for collaborators **reviewing** this suite and **continuing** to work on it.
Read this first — it links to the deeper docs instead of duplicating them.

---

## What this is

`full-stack-carbon` bundles six lab tools for carbon modeling of computer hardware and systems —
device manufacturing → server provisioning → software carbon attribution — as git submodules, with
a single guided **walkthrough** ("the life of a data center") built for an academic workshop. The
tools: **ACT, COFFEE, CarbonClarity, MicroGreen, EServe (a.k.a. EcoServe), Fair-CO2**.

Two things were built on top of bundling them:
1. A reframed **walkthrough** that runs each tool from committed data (artifact-evaluation style) and
   ties them into one story.
2. An **`act_core` unification** that de-duplicates the three ACT-derived codebases (ACT, MicroGreen's
   `EmbodiedCarbonModeling`, EServe) onto one shared package.

## Status at a glance

| Workstream | What | State |
|---|---|---|
| A — plumbing & envs | six submodules, per-tool venvs, `Makefile`, CI | ✅ done |
| B — the walkthrough | six reframed segments, golden fallbacks, chain verify | ✅ done (tag `v0.1.0`) |
| C — `act_core` unification | ACT + MicroGreen + EServe share one core | ✅ done (on `act-core` branches) |

A from-scratch clone → `make setup` → `make all-demos` is **verified to run end-to-end**.
**Nothing is merged to `main` on any pre-existing repo.**

---

## ⚠️ Branch model — read before pushing

| Branch | What's on it |
|---|---|
| `main` (suite) | initial commit only — untouched |
| `suite-assembly` + tag **`v0.1.0`** | the stable reframed walkthrough (pre-unification; e.g. EServe H100 ≈ 154 kg) |
| **`act-core`** (suite + the unified tool repos) | the full unified suite (`act_core`; EServe H100 ≈ 103 kg) — **the review branch** |

**Constraint (from the repo owner):** the `act_core` unification work in the pre-existing public tool
repos — **ACTv2, MicroGreen, EmbodiedCarbonModeling** (and EServe) — must stay on the **`act-core`
review branch, never `main`**. **Do not merge `act-core` to `main` or open PRs** until the team has
reviewed. (EServe and the suite repo are new, so their branches are fine. COFFEE's one-line
`NVMExplorer`-submodule fix was a separate, owner-approved hygiene change and is already on `main`;
CarbonClarity and Fair-CO2 are untouched.)

Pinned commits (for review / verification):

| repo | review branch | tip | original default |
|---|---|---|---|
| full-stack-carbon (suite) | `act-core` | _this branch (see `git log`)_ | main `6de3e0c` |
| ACTv2 | `act-core` | `8764d6a` | main `abc9fbb` |
| EServe | `act-core` | `d38bf93` | main `a1b33a5` |
| MicroGreen | `act-core` | `7f03583` | main `384d8b7` |
| EmbodiedCarbonModeling | `act-core` | `d9fd240` | `microgreen` `365589b` |
| COFFEE | _(fix merged to `main`)_ | `257f4d5` | was main `8e019a6` |
| CarbonClarity | _(untouched)_ | — | main `ae209c9` |
| Fair-CO2 | _(untouched)_ | — | main `a1142d6` |

> **COFFEE** carries a one-line repo-hygiene fix (unrelated to `act_core`), now on `main`: it adds the
> missing `.gitmodules` mapping for COFFEE's `NVMExplorer` submodule (the gitlink existed but had no
> URL, so `git submodule update --init --recursive` failed). The suite's `act-core` pins COFFEE at this
> commit (= COFFEE `main` HEAD), so a suite clone gets the working mapping.

- Stable demo: `git checkout suite-assembly && git submodule update --init`
- Unified version: `git checkout act-core && git submodule update --init`

---

## Get it running

**Prerequisite:** install [`uv`](https://docs.astral.sh/uv/) (`brew install uv`, or the install
script). It auto-provisions each tool's pinned Python (3.11 / 3.12); without it, `make setup` falls
back to `python -m venv` and requires **both** `python3.11` and `python3.12` already on your PATH.

```bash
make submodules     # init the six tools + MicroGreen's EmbodiedCarbonModeling
make setup          # build the six isolated per-tool venvs (uv-first); ~a few min
make all-demos      # run all six walkthrough segments, then verify the chain
make golden         # OR: show the committed backup figures with zero compute
make help           # every target
```

The tools carry incompatible pins (numpy 2.3.4/2.3.5/2.4.3; Python 3.11 vs 3.12), so each gets its
**own venv** under `.envs/<tool>/` (gitignored). EServe and MicroGreen also get `act_core` installed
editable. See `README.md` for the quickstart and `scripts/bootstrap.sh` for the env matrix.

---

## How the walkthrough works (Workstream B)

The story, order, and headline numbers live in **`walkthrough/README.md`**. The model:

- Each `walkthrough/NN_<tool>/` **recomputes from committed data** (no live workloads), writes a
  figure + `result.json`, and falls back to a committed `golden/` via `run.sh --golden`.
- Segments run **standalone** — the value one hands the next is committed into the next's `inputs/`.
- `make verify` (`walkthrough/lib/verify_chain.py`) asserts those handoffs line up.
- Each segment's **`TALKING_POINTS.md`** is the slide content for that tool's presentation (owners
  build the actual decks from it; honesty caveats are baked in).

**To edit/add a segment:** copy the shape of `walkthrough/05_eserve/` (`run.sh` + `recompute.py` +
`TALKING_POINTS.md` + `inputs/` + `golden/`), use the `walkthrough/lib/walk.py` helpers, and after a
real run snapshot the backup: `rm -f golden/* && cp figures/* golden/`.

---

## The `act_core` unification (Workstream C) — and how not to break it

Full log, every commit, and the regression procedure: **`act-core-migration/README.md`**.

In short: `act/core` + `act/models` were carved out of ACT into a pip-installable **`act_core`**
package (hosted in the ACTv2 repo). MicroGreen's `EmbodiedCarbonModeling` fork was **deleted** and
re-pointed at `act_core`; EServe's memory model was **converged** onto `act_core.MemoryModel`. ACT
stays byte-identical, ECM's 14 BOMs reproduce, and EServe's memory was corrected to the paper-backed
**HBM3e = 0.24** (the old 0.85 was unsourced — see `baselines/eserve/c3_convergence_deltas.md`).

- **ACT** consumes `act_core` via `PYTHONPATH`; **EServe** and **MicroGreen/ECM** consume it as the
  pip-installed package (`scripts/bootstrap.sh` installs it editable into their venvs).

**If you change `act_core`, run the regression checks** against the committed safety net in
`act-core-migration/baselines/`:
- **ACT:** `cd ACT && bash ci_script.sh`; and diff a BOM report vs `baselines/act/<bom>/`.
- **EServe:** `cd EServe && ../.envs/eserve/bin/python -m pytest tests` (incl. `test_h100_validation`).
- **MicroGreen/ECM:** re-run its 14 BOMs and diff `total_carbon` vs `baselines/microgreen/<bom>/`.
- **Walkthrough:** `make all-demos` must stay green.

---

## What's left / how to continue

- **Review → merge (owner's call):** the `act-core` branches are the review vehicle — green and
  reproducible. When the team signs off, merge `act-core` → `suite-assembly`/`main` (or open PRs).
- **Make the tool repos public** if you want anonymous artifact-evaluation clones (the suite uses
  HTTPS submodule URLs; currently access is required).
- **Slide decks:** build from the six `TALKING_POINTS.md`.
- **Deferred technical follow-ups** (detailed in `act-core-migration/README.md`):
  - EServe's **SoC / SSD / PDN** are still EServe-specific (only the memory model converged onto `act_core`).
  - The HBM coefficient (0.24) is paper-backed; pulling the real figure from NVIDIA's H100 PCF PDF
    would settle the HBM-stacking-overhead question.
  - COFFEE's **lifetime/endurance** branch (only the embodied/density path is demoed).

---

## Doc map

| For… | Read |
|---|---|
| quickstart + suite overview | `README.md` |
| the walkthrough story + how to run it | `walkthrough/README.md` |
| a tool's slide content (per segment) | `walkthrough/<segment>/TALKING_POINTS.md` |
| the `act_core` refactor: status, commits, regression | `act-core-migration/README.md` |
| the EServe memory-convergence deltas | `act-core-migration/baselines/eserve/c3_convergence_deltas.md` |
| every Make target | `make help` |
| a tool's own documentation | that submodule's own `README` |
| the source papers | `papers/` (kept local; gitignored) |

The reasoning behind specific choices (why HBM3e = 0.24, why the segment order, the "naive number →
real point" reframe) lives in the relevant `TALKING_POINTS.md` and `act-core-migration/README.md`.
