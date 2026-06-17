#!/usr/bin/env python3
"""Segment 2 - CarbonClarity: embodied carbon is a DISTRIBUTION, not a point.

ACT (segment 1) reports a single embodied-carbon number. But the fab inputs it
plugs in -- energy-per-area (EPA), gas-per-area (GPA), grid carbon-intensity
(CI) and yield -- are all uncertain. CarbonClarity propagates those uncertainties
into a *distribution* of carbon-per-area (CPA). The key, decision-relevant facts:

  * ACT's deterministic value is ~the MEAN of that distribution. The real value
    therefore exceeds ACT's number roughly half the time -- it is NOT a lowball.
  * The number you should actually REPORT is the conservative 95th percentile,
    which runs ~1.3x the mean here.
  * Both the carbon and its (absolute) uncertainty grow toward advanced nodes.

We sweep three logic nodes that have committed input distributions and, per cm2
(no die-area multiply, for cross-node comparability), report each node's mean
(= the ACT plug-in point), 95th percentile, p95/mean, and P(actual > mean).

7nm and 10nm are the fully clean pair (committed EPA+GPA+CI+yield). 28nm has no
committed yield distribution, so we plug a deterministic yield -- which omits
yield variance and therefore UNDERSTATES 28nm's uncertainty (flagged below).

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

# Per-node fab inputs. CI: the mature 28nm node is plugged with a Taiwan grid;
# the sub-10nm advanced nodes use CarbonClarity's dedicated advanced-fab grid
# (matches its own 7nm&10nm example). yield: committed per-cm2 distribution where
# one exists; 28nm has none committed, so we plug a deterministic 0.875 -- this
# omits yield variance and so UNDERSTATES 28nm uncertainty (see caveat).
NODES = [
    {"node": "28nm", "ci": "CI_fab_taiwan.json",  "yield": 0.875,
     "yield_source": "deterministic 0.875 (no committed distribution)", "clean": False},
    {"node": "10nm", "ci": "CI_fab_sub10nm.json", "yield": "Yield_10nm_per_cm2.json",
     "yield_source": "Yield_10nm_per_cm2.json", "clean": True},
    {"node": "7nm",  "ci": "CI_fab_sub10nm.json", "yield": "Yield_7nm_per_cm2.json",
     "yield_source": "Yield_7nm_per_cm2.json", "clean": True},
]

GREEN, ORANGE = "#3b7a57", "#cc6b2c"


def _load(name):
    return np.array(json.loads((HERE / "inputs" / "all_distribution" / name).read_text()))


def _cpa_kg(spec):
    """kgCO2e/cm2 distribution for one node via CarbonClarity's own model.

    get_cpa() returns gCO2e/cm2; we divide by 1e3 and do NOT multiply by any die
    area, so nodes are directly comparable. CWD must already be CC (materials.json)."""
    node = spec["node"]
    epa, gpa, ci = _load(f"epa_{node}.json"), _load(f"gpa_{node}.json"), _load(spec["ci"])
    fy = spec["yield"]
    fab_yield = float(fy) if isinstance(fy, (int, float)) else _load(fy)
    model = Fab_Logic_Risk(process_node=node, gpa=gpa, carbon_intensity=ci,
                           epa=epa, fab_yield=fab_yield)
    return model.get_cpa() / 1e3


def _figure(out_png, nodes, stats, samples):
    """Violins of the per-node CPA distribution with the ACT-mean and reportable
    p95 marked, p95/mean annotated, ordered mature -> advanced."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    x = np.arange(len(nodes))
    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    parts = ax.violinplot(samples, positions=x, widths=0.8,
                          showmeans=False, showextrema=False)
    for pc in parts["bodies"]:
        pc.set_facecolor(GREEN)
        pc.set_alpha(0.35)
        pc.set_edgecolor("#2a5a40")
        pc.set_linewidth(1.0)

    hw = 0.34
    top = max(s["p95"] for s in stats)
    for xi, node, s in zip(x, nodes, stats):
        ax.hlines(s["mean"], xi - hw, xi + hw, color=GREEN, lw=2.4, zorder=5)
        ax.hlines(s["p95"], xi - hw, xi + hw, color=ORANGE, lw=2.4, ls="--", zorder=5)
        star = "*" if not node["clean"] else ""
        ax.annotate(f"p95/mean\n{s['p95']/s['mean']:.2f}x{star}",
                    (xi, s["p95"]), xytext=(0, 8), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, color=ORANGE, fontweight="bold")
        ax.annotate(f"P(>mean)\n{s['p_exceed_mean']*100:.0f}%",
                    (xi, s["mean"]), xytext=(0, -2), textcoords="offset points",
                    ha="center", va="top", fontsize=8, color=GREEN)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{n['node']}{'*' if not n['clean'] else ''}" for n in nodes])
    ax.set_xlabel("logic node  (mature  ->  advanced)")
    ax.set_ylabel("embodied carbon per area  (kgCO2e / cm2)")
    ax.set_ylim(0, top * 1.30)
    fig.suptitle("Embodied carbon is a distribution, not a point (CarbonClarity)",
                 fontsize=13, fontweight="bold", y=0.98)
    ax.set_title("ACT's number = the mean; report the 95th pct (~1.3x). "
                 "Carbon & its spread grow toward advanced nodes.",
                 fontsize=8.5, color="#555", pad=10)
    handles = [
        Line2D([0], [0], color=GREEN, lw=2.4, label="mean  = ACT plug-in point"),
        Line2D([0], [0], color=ORANGE, lw=2.4, ls="--", label="95th pct = report this"),
    ]
    ax.legend(handles=handles, frameon=False, loc="upper left", fontsize=9)
    fig.text(0.5, 0.015,
             "* 28nm has no committed yield distribution -> yield variance omitted "
             "-> its uncertainty is understated. Fully clean pair: 10nm vs 7nm.",
             ha="center", va="bottom", fontsize=7.5, color="#888")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
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
        print(f"[02_carbonclarity] (golden) embodied carbon is a distribution: "
              f"report p95 ~{h['p95_over_mean_x']}x the ACT-mean "
              f"(P(actual>mean) ~{h['p_exceed_mean_pct']}%); {h['units']}")
        return

    os.chdir(CC)  # Fab_Logic_Risk opens materials.json relative to CWD
    rng = np.random.default_rng(0)
    stats, samples = [], []
    for spec in NODES:
        cpa = _cpa_kg(spec)
        mean = float(cpa.mean())
        stats.append({
            "mean": mean,
            "std": float(cpa.std()),
            "p50": float(np.percentile(cpa, 50)),
            "p95": float(np.percentile(cpa, 95)),
            "p_exceed_mean": float(np.mean(cpa > mean)),
        })
        # Subsample (with replacement) only for the violin KDE; stats use the full array.
        samples.append(cpa[rng.integers(0, cpa.size, 60000)])
        del cpa

    _figure(fig / "carbonclarity_node_risk.png", NODES, stats, samples)

    per_node = {}
    for spec, s in zip(NODES, stats):
        per_node[spec["node"]] = {
            "mean_kgco2e_cm2": round(s["mean"], 3),
            "p95_kgco2e_cm2": round(s["p95"], 3),
            "p95_over_mean": round(s["p95"] / s["mean"], 3),
            "p_exceed_mean": round(s["p_exceed_mean"], 3),
            "std_kgco2e_cm2": round(s["std"], 3),
            "ci_source": spec["ci"],
            "yield_source": spec["yield_source"],
            "clean": spec["clean"],
        }

    ratios = [s["p95"] / s["mean"] for s in stats]
    pexc = [s["p_exceed_mean"] for s in stats]
    result = {
        "segment": "02_carbonclarity",
        "tool": "CarbonClarity",
        "anchor": "logic fab carbon-per-area (per cm2), nodes 28/10/7 nm",
        "units": "kgCO2e/cm2",
        "headline": {
            "units": "kgCO2e/cm2",
            "nodes_mature_to_advanced": [n["node"] for n in NODES],
            "p95_over_mean_x": round(float(np.mean(ratios)), 2),
            "p95_over_mean_range": [round(min(ratios), 2), round(max(ratios), 2)],
            "p_exceed_mean_pct": round(float(np.mean(pexc)) * 100),
            "mean_growth_28nm_to_7nm": [per_node["28nm"]["mean_kgco2e_cm2"],
                                        per_node["7nm"]["mean_kgco2e_cm2"]],
            "std_growth_28nm_to_7nm": [per_node["28nm"]["std_kgco2e_cm2"],
                                       per_node["7nm"]["std_kgco2e_cm2"]],
            "statement": "ACT gives the mean; report the 95th pct (~1.3x); carbon and "
                         "its absolute uncertainty grow toward advanced nodes.",
        },
        "per_node": per_node,
        "clean_pair": ["10nm", "7nm"],
        "note": "CarbonClarity propagates EPA/GPA/carbon-intensity/yield uncertainty into a "
                "distribution of carbon-per-area. The mean equals ACT's deterministic "
                "plug-in point, so the true value exceeds it ~half the time; the reportable "
                "figure is the 95th percentile.",
        "caveat": "Committed JSONs are 100-sample KDE resamples, narrower than the paper's "
                  "figures -- do NOT quote the paper's 1.6x off this recompute. 28nm has no "
                  "committed yield distribution (deterministic yield plugged), so its "
                  "uncertainty is understated; the fully clean pair is 10nm vs 7nm.",
    }
    walk.save_result(HERE, result)

    p = per_node
    print(f"[02_carbonclarity] embodied carbon is a distribution: report p95 "
          f"~{result['headline']['p95_over_mean_x']}x the ACT-mean "
          f"(P(actual>mean) ~{result['headline']['p_exceed_mean_pct']}%); per cm2 mean/p95 "
          f"28nm {p['28nm']['mean_kgco2e_cm2']}/{p['28nm']['p95_kgco2e_cm2']}, "
          f"10nm {p['10nm']['mean_kgco2e_cm2']}/{p['10nm']['p95_kgco2e_cm2']}, "
          f"7nm {p['7nm']['mean_kgco2e_cm2']}/{p['7nm']['p95_kgco2e_cm2']} kgCO2e/cm2")


if __name__ == "__main__":
    main()
