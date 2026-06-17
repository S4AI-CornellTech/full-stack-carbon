#!/usr/bin/env python3
"""Segment 3 - COFFEE: the memory-technology trade-off (a side-branch).

COFFEE is a life-cycle carbon model for emerging FeFET (HZO) on-chip memory. The
interesting result is NOT an "overhead" -- it is a *density inversion* that comes
out in FeFET's favour at the system level:

  Panel A (per cm2):  the ferroelectric ALD layer makes the FeFET die cost
                      ~+9% carbon-per-area (CPA) vs a CMOS-28nm die.  FeFET
                      *loses* on area.
  Panel B (per MB):   but the FeFET cell is ~5x denser, so per stored megabyte
                      the embodied carbon is ~4.3x *lower* than SRAM.  FeFET
                      *wins* on density.

So the right memory-tech choice is a life-cycle trade-off (a one-time fab cost
amortised over operation via leakage/energy savings, gated by write-endurance),
not a flat penalty.

Panel A runs COFFEE's own Fab_Logic on the committed HZO_5 device and CMOS_logic
archs. Panel B reads the committed inputs/nvm_areas.csv (SRAM vs FeFET array
areas per capacity) and converts each tool's CPA into carbon-per-MB.

With --golden we restore the committed golden/ outputs instead of recomputing.

Two honesty caveats are encoded below:
  * get_cpa() is in GRAMS CO2e / cm2 (some Fab_Logic debug prints mislabel it
    "kgCO2e/cm2"); every axis/number here stays in grams.
  * the committed fefet_ald.json uses fefet_area_efficiency = 0.8 -> +9.0%; the
    paper's Figure_coffee/coffee.ipynb hardcodes ~0.96 -> +10.9%. We compute and
    report both so the "+9-11%" range is explicit.
"""
import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import walk  # noqa: E402

COFFEE = walk.SUITE_ROOT / "COFFEE"
sys.path.insert(0, str(COFFEE))
from src.logic_model_HZO import Fab_Logic  # noqa: E402

ARCHS = COFFEE / "archs"
DEVICE = "HZO_5"
NODE_NM = 28
LOCATION = "loc_taiwan"
FAB_YIELD = 0.875            # Fab_Logic default; passed explicitly so we can invert it
PAPER_AREA_EFF = 0.96079     # area-efficiency hardcoded in Figure_coffee/coffee.ipynb

# COFFEE's purple identity, plus a neutral green for the CMOS/SRAM baseline.
C_CMOS = "#3b7a57"
C_FEFET = "#a06cd5"
C_FEFET_PAPER = "#cdb4f0"


def _fefet_cpa_for_efficiency(thick_hzo, thick_al2o3, area_efficiency):
    """COFFEE Fab_Logic CPA (gCO2e/cm2) for the HZO stack at a given FEL area
    efficiency. We write the efficiency into a throwaway ALD config so the value
    comes straight out of COFFEE's own model rather than being re-derived."""
    import tempfile, os
    cfg = json.loads((ARCHS / "fefet_extensions" / "fefet_ald.json").read_text())
    cfg["fefet_area_efficiency"] = area_efficiency
    tf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(cfg, tf)
    tf.close()
    try:
        fab = Fab_Logic(process_node=NODE_NM, carbon_intensity=LOCATION, fab_yield=FAB_YIELD,
                        fefet_config_path=tf.name,
                        override_thickness_hzo=thick_hzo, override_thickness_al2o3=thick_al2o3)
        return float(fab.get_cpa()), float(fab.get_fefet_epa()), float(fab.get_fel_energy())
    finally:
        os.unlink(tf.name)


def _per_mb_table(cmos_cpa, fefet_cpa):
    """Read committed nvm_areas.csv and turn each array area into carbon-per-MB.

    per-MB embodied carbon (gCO2e/MB) = CPA(gCO2e/cm2) * area(cm2) / capacity(MB).
    SRAM is CMOS, so it carries the CMOS CPA; the FeFET array carries the FeFET CPA.
    """
    cpa = {"SRAM": cmos_cpa, "HZO5_FeFET": fefet_cpa}
    rows = []
    with open(HERE / "inputs" / "nvm_areas.csv", newline="") as f:
        for r in csv.DictReader(f):
            cap = float(r["capacity_MB"])
            area_cm2 = float(r["area_mm2"]) / 100.0
            g_per_mb = cpa[r["tech"]] * area_cm2 / cap
            rows.append({"tech": r["tech"], "capacity_MB": int(cap),
                         "area_mm2": float(r["area_mm2"]), "cell_F2": int(r["cell_F2"]),
                         "g_per_mb": g_per_mb, "g_total": cpa[r["tech"]] * area_cm2})
    return rows


def _figure(out_png, cmos_cpa, fefet_cpa, fefet_cpa_paper, pen_pct, pen_pct_paper, rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    caps = sorted({r["capacity_MB"] for r in rows})
    sram = [next(r["g_per_mb"] for r in rows if r["tech"] == "SRAM" and r["capacity_MB"] == c) for c in caps]
    fefet = [next(r["g_per_mb"] for r in rows if r["tech"] == "HZO5_FeFET" and r["capacity_MB"] == c) for c in caps]
    ratio = sram[0] / fefet[0]

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.4, 4.8))

    # Panel A: carbon-per-AREA (FeFET loses) -------------------------------------
    labelsA = ["CMOS\n28 nm", "FeFET HZO_5\n(eff 0.8)", "FeFET HZO_5\n(eff 0.96, paper)"]
    valsA = [cmos_cpa, fefet_cpa, fefet_cpa_paper]
    barsA = axA.bar(labelsA, valsA, color=[C_CMOS, C_FEFET, C_FEFET_PAPER])
    axA.set_ylabel("embodied carbon (gCO2e / cm2)")
    axA.set_title("Per cm2: FeFET loses on area  (+9-11%)")
    axA.set_ylim(0, max(valsA) * 1.18)
    for b, v, tag in zip(barsA, valsA, ["", f"+{pen_pct:.1f}%", f"+{pen_pct_paper:.1f}%"]):
        axA.text(b.get_x() + b.get_width() / 2, v, f"{v:,.0f}\n{tag}",
                 ha="center", va="bottom", fontsize=9)
    for s in ("top", "right"):
        axA.spines[s].set_visible(False)

    # Panel B: carbon-per-MB (FeFET wins) ----------------------------------------
    x = np.arange(len(caps))
    w = 0.38
    axB.bar(x - w / 2, sram, w, label="SRAM (CMOS)", color=C_CMOS)
    axB.bar(x + w / 2, fefet, w, label="HZO5 FeFET", color=C_FEFET)
    axB.set_xticks(x)
    axB.set_xticklabels([f"{c} MB" for c in caps])
    axB.set_ylabel("embodied carbon (gCO2e / MB)")
    axB.set_title(f"Per MB: FeFET wins on density  (~{ratio:.1f}x lower, flat)")
    axB.set_ylim(0, max(sram) * 1.28)
    axB.text(0.5, 0.93, f"~{ratio:.1f}x lower per MB at every capacity",
             ha="center", va="center", fontsize=9, color=C_FEFET, transform=axB.transAxes)
    axB.legend(frameon=False, loc="upper right")
    for s in ("top", "right"):
        axB.spines[s].set_visible(False)

    fig.suptitle("COFFEE: FeFET density inversion -- +9-11% carbon per cm2, "
                 "but ~4.3x LOWER carbon per MB", fontsize=12, y=1.00)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = Path(out_png)
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", action="store_true")
    args = ap.parse_args()
    fig = HERE / "figures"
    fig.mkdir(parents=True, exist_ok=True)

    if args.golden:
        for f in (HERE / "golden").iterdir():
            if f.is_file():
                shutil.copy2(f, fig / f.name)
        h = walk.load_result(HERE, golden=True)["headline"]
        print(f"[03_coffee] (golden) FeFET {DEVICE}: +{h['per_cm2_penalty_pct']}% carbon/cm2 "
              f"({h['cmos_cpa_g_cm2']} -> {h['fefet_cpa_g_cm2']} gCO2e/cm2) but "
              f"~{h['per_mb_advantage_x']}x LOWER per MB")
        return

    # --- Panel A: COFFEE's Fab_Logic, carbon-per-area (gCO2e/cm2) ---------------
    dev = json.loads((ARCHS / "fefet_extensions" / "fefet_devices.json").read_text())[DEVICE]
    thick_hzo, thick_al2o3 = dev["Thickness_HZO"], dev["Thickness_AI2O3"]
    committed_eff = float(json.loads(
        (ARCHS / "fefet_extensions" / "fefet_ald.json").read_text())["fefet_area_efficiency"])

    # FeFET die at the committed area efficiency (0.8) -> COFFEE's real output.
    fefet_cpa, fefet_epa, fel_kwh = _fefet_cpa_for_efficiency(thick_hzo, thick_al2o3, committed_eff)

    # CMOS-28nm baseline = the same fab model with the ferroelectric layer removed.
    # carbon_per_area = (fab_ci*EPA + GPA + MPA)/yield and only the EPA term carries
    # the FEL, so subtracting fab_ci*(fefet_epa - cmos_epa)/yield recovers the pure
    # CMOS die. (Verified identical to running Fab_Logic with fefet_area_efficiency=0.)
    cmos_epa = float(json.loads((ARCHS / "CMOS_logic" / "epa.json").read_text())[f"{NODE_NM}nm"])
    fab_ci = float(json.loads((ARCHS / "carbon_intensity" / "location.json").read_text())["taiwan"])
    fel_cpa_delta = fab_ci * (fefet_epa - cmos_epa) / FAB_YIELD
    cmos_cpa = fefet_cpa - fel_cpa_delta

    # Paper variant (area efficiency ~0.96) -> the "+11%" end of the range.
    fefet_cpa_paper, _, _ = _fefet_cpa_for_efficiency(thick_hzo, thick_al2o3, PAPER_AREA_EFF)

    pen_pct = 100.0 * (fefet_cpa - cmos_cpa) / cmos_cpa
    pen_pct_paper = 100.0 * (fefet_cpa_paper - cmos_cpa) / cmos_cpa

    # --- Panel B: carbon-per-MB from committed nvm_areas.csv --------------------
    rows = _per_mb_table(cmos_cpa, fefet_cpa)
    sram2 = next(r for r in rows if r["tech"] == "SRAM" and r["capacity_MB"] == 2)
    fefet2 = next(r for r in rows if r["tech"] == "HZO5_FeFET" and r["capacity_MB"] == 2)
    per_mb_x = sram2["g_per_mb"] / fefet2["g_per_mb"]

    png = _figure(fig / "coffee_density_inversion.png", cmos_cpa, fefet_cpa, fefet_cpa_paper,
                  pen_pct, pen_pct_paper, rows)

    result = {
        "segment": "03_coffee",
        "tool": "COFFEE",
        "anchor": f"HZO FeFET eNVM ({DEVICE}) vs SRAM, {NODE_NM} nm",
        "branch": "side-branch off the silicon story: the memory-technology choice "
                  "in the embodied-vs-operational trade-off (CF = OCF + (T/LT)*ECF)",
        "headline": {
            "cmos_cpa_g_cm2": round(cmos_cpa, 1),
            "fefet_cpa_g_cm2": round(fefet_cpa, 1),
            "per_cm2_penalty_pct": round(pen_pct, 1),
            "per_cm2_penalty_pct_paper_eff096": round(pen_pct_paper, 1),
            "sram_g_per_mb": round(sram2["g_per_mb"], 2),
            "fefet_g_per_mb": round(fefet2["g_per_mb"], 2),
            "per_mb_advantage_x": round(per_mb_x, 2),
        },
        "panelA_per_cm2": {
            "units": "gCO2e/cm2 (grams; COFFEE get_cpa() is grams despite some debug prints saying kg)",
            "cmos_28nm": round(cmos_cpa, 2),
            "fefet_hzo5_eff0_8_committed": round(fefet_cpa, 2),
            "fefet_hzo5_eff0_96_paper": round(fefet_cpa_paper, 2),
            "fel_process_energy_kwh": round(fel_kwh, 3),
            "fefet_epa_kwh_cm2": round(fefet_epa, 4),
            "cmos_epa_kwh_cm2": round(cmos_epa, 4),
            "fel_carbon_delta_g_cm2": round(fel_cpa_delta, 1),
        },
        "panelB_per_mb": {
            "units": "gCO2e/MB",
            "sram_cell_F2": 146, "fefet_cell_F2": 30,
            "per_capacity": [{"capacity_MB": r["capacity_MB"], "tech": r["tech"],
                              "g_per_mb": round(r["g_per_mb"], 3)} for r in rows],
        },
        "note": "Density inversion: FeFET costs +9.0% carbon/cm2 (committed fefet_ald.json "
                "area-efficiency 0.8; ~+10.9% at the paper's ~0.96) but ~4.3x LOWER carbon "
                "per MB because the FeFET cell is ~5x denser (30 vs 146 F2). Net memory-tech "
                "choice is a life-cycle trade-off: a one-time fab cost amortised over operation "
                "via leakage/energy savings, and co-optimised with write-endurance (thicker HZO "
                "-> higher CPA but higher endurance/lifetime).",
    }
    walk.save_result(HERE, result)
    print(f"[03_coffee] FeFET {DEVICE}: +{pen_pct:.1f}% carbon/cm2 "
          f"({cmos_cpa:,.0f} -> {fefet_cpa:,.0f} gCO2e/cm2; +{pen_pct_paper:.1f}% at paper eff 0.96) "
          f"BUT ~{per_mb_x:.1f}x LOWER per MB "
          f"(SRAM {sram2['g_per_mb']:.1f} -> FeFET {fefet2['g_per_mb']:.1f} gCO2e/MB) "
          f"-> {png.name}")


if __name__ == "__main__":
    main()
