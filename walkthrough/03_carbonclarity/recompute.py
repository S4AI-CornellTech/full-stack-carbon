#!/usr/bin/env python3
"""Segment 3 - CarbonClarity: how trustworthy is segment 1's CPU number?

CarbonClarity propagates fab uncertainty (EPA / GPA / carbon-intensity / yield
distributions) into a *distribution* of embodied carbon-per-area instead of a
single point. We feed it committed 28 nm input distributions (in inputs/, the
artifact-evaluation data) and the R740 CPU die area, and show ACT's deterministic
estimate sitting inside the resulting band.

With --golden we restore the committed golden/ outputs instead of recomputing.
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import walk  # noqa: E402

CC = walk.SUITE_ROOT / "CarbonClarity"
sys.path.insert(0, str(CC / "examples"))
from Fab_Logic_Risk import Fab_Logic_Risk  # noqa: E402

AREA_CM2 = 6.98   # R740 CPU die area (segment 1 / dellr740 BOM)
NODE = "28nm"
FAB_YIELD = 0.875


def _load(name):
    return np.array(json.loads((HERE / "inputs" / "all_distribution" / name).read_text()))


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
        print(f"[03_carbonclarity] (golden) R740 CPU die embodied carbon: "
              f"{h['p50_kgco2e']} kgCO2e (P10-P90 {h['p10_kgco2e']}-{h['p90_kgco2e']})")
        return

    epa, gpa, ci = _load("epa_28nm.json"), _load("gpa_28nm.json"), _load("CI_fab_taiwan.json")

    os.chdir(CC)  # Fab_Logic_Risk reads materials.json relative to CWD
    model = Fab_Logic_Risk(process_node=NODE, gpa=gpa, carbon_intensity=ci, epa=epa, fab_yield=FAB_YIELD)
    cpa = model.get_cpa() / 1e3 * AREA_CM2   # gCO2e/cm2 distribution -> kgCO2e for the die

    mean, std = float(cpa.mean()), float(cpa.std())
    p10, p50, p90 = (round(float(np.percentile(cpa, q)), 3) for q in (10, 50, 90))

    # ACT's deterministic per-die estimate from segment 1 (committed golden).
    act_per_die = None
    seg1 = walk.WALK_ROOT / "01_act" / "golden" / "result.json"
    if seg1.exists():
        ps = json.loads(seg1.read_text())["handoff"].get("cpu_per_socket_kgco2e")
        if ps:
            act_per_die = round(ps / 2.0, 2)  # 2 dies per socket in the BOM

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(6.2, 3.8))
    plt.hist(cpa, bins=60, density=True, alpha=0.6, color="#3b7a57",
             label=f"{NODE} CPU die, {AREA_CM2} cm2")
    if act_per_die is not None:
        plt.axvline(act_per_die, color="#bb3344", ls="--", lw=1.4,
                    label=f"ACT point estimate ({act_per_die} kg)")
    plt.xlabel("Embodied carbon (kgCO2e)")
    plt.ylabel("probability density")
    plt.title("CarbonClarity: fab-uncertainty band for the R740 CPU die")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(fig / "carbonclarity_cpu_distribution.png", dpi=150)
    plt.close()

    result = {
        "segment": "03_carbonclarity",
        "tool": "CarbonClarity",
        "anchor": f"R740 CPU die, {NODE}, {AREA_CM2} cm2",
        "headline": {
            "mean_kgco2e": round(mean, 3),
            "std_kgco2e": round(std, 3),
            "p10_kgco2e": p10,
            "p50_kgco2e": p50,
            "p90_kgco2e": p90,
            "act_point_estimate_kgco2e": act_per_die,
        },
        "note": "Propagates EPA/GPA/carbon-intensity/yield uncertainty into a "
                "distribution of embodied carbon. ACT's single-point estimate (segment 1) "
                "is shown as the dashed line for comparison.",
    }
    walk.save_result(HERE, result)
    band = f"P10-P90 {p10}-{p90}"
    ref = f" vs ACT point {act_per_die}" if act_per_die is not None else ""
    print(f"[03_carbonclarity] R740 CPU die embodied carbon: median {p50} kgCO2e "
          f"({band}, mean {round(mean,3)} +/- {round(std,3)}){ref}")


if __name__ == "__main__":
    main()
