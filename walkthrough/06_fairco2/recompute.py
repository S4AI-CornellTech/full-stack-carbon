#!/usr/bin/env python3
"""Segment 6 - Fair-CO2: fairly attributing shared cloud carbon (the accounting CLIMAX).

The data center is built (ACT, segment 1) and running (EServe, segment 5). Now
its embodied + operational carbon has to be *charged back* to the software that
shares the machine. The industry default is to split it in proportion to
resource use -- Resource-Utilization-Proportional (RUP), which is exactly what
Google's operational carbon accounting and the Green Software Foundation's SCI
prescribe. Fair-CO2's thesis: RUP is *unfair*. Measured against a game-theoretic
Shapley-value ground truth (the provably fair way to divide a shared cost), RUP
misattributes each job by ~80% on average. Fair-CO2 approximates the fair Shapley
share and cuts that error ~4-6x, at ~600,000x less compute than computing Shapley
exactly.

This segment reproduces the paper's Figures 7-9 by a direct pandas reduction over
Fair-CO2's committed Monte-Carlo results (ref-sim-results/, READ-ONLY): the mean
per-simulation deviation-from-Shapley of each attribution method. The hook is the
embodied-carbon colocation matrix -- the SAME job's attributed embodied carbon
swings ~2x purely depending on which neighbor it shares the node with ("your
carbon bill depends on your neighbor").

The Fair-CO2 submodule is only ever READ; nothing is written into it.

With --golden we restore the committed golden/ outputs instead of recomputing.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import walk  # noqa: E402

import pandas as pd  # noqa: E402

FAIRCO2 = walk.SUITE_ROOT / "Fair-CO2"
MC = FAIRCO2 / "monte-carlo-simulations"
DEMAND_CSV = MC / "dynamic-demand" / "ref-sim-results" / "synthetic_schedule.csv"
INTERF_CSV = MC / "colocation" / "ref-sim-results" / "interference_adjustment_results.csv"
EMB_MATRIX = FAIRCO2 / "colocation" / "ref-results" / "embodied_cf_colocation_matrix.csv"

# Fair-CO2 approximates the exponential exact-Shapley computation at ~600,000x
# less compute (paper; the headline scalability result that makes live, per-job
# fair attribution -- and hence carbon optimisation, Section 8 -- tractable).
SHAPLEY_SPEEDUP_X = 600_000


def grouped_bars(out_png, groups, series, *, title, subtitle, ylabel, colors,
                 figsize=(7.8, 4.8), unit="%", ann_fmt="{:.1f}", legend_loc="upper left"):
    """Annotated grouped bar chart (headless / Agg). One bold headline (suptitle),
    one gray sub-line (axes title), value labels on each bar."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    names = list(series.keys())
    x = np.arange(len(groups))
    n = len(names)
    w = 0.8 / n
    fig, ax = plt.subplots(figsize=figsize, layout="constrained")
    ymax = 0.0
    for i, name in enumerate(names):
        vals = series[name]
        ymax = max(ymax, max(vals))
        bars = ax.bar(x + (i - (n - 1) / 2) * w, vals, w, label=name,
                      color=colors[i % len(colors)])
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, ann_fmt.format(v) + unit,
                    ha="center", va="bottom", fontsize=8.5)
    ax.set_xticks(x)
    ax.set_xticklabels([str(g) for g in groups])
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, ymax * 1.18)
    ax.set_title(subtitle, fontsize=9.5, color="#555555")
    fig.suptitle(title, fontsize=13, fontweight="bold")
    ax.legend(frameon=False, fontsize=9, loc=legend_loc)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def mean_pct(df, col):
    """Mean per-simulation deviation-from-Shapley for one method (the reduction the
    paper's own figure generators print; see gen_colocation_sim_figures.py)."""
    return round(float(df[col].mean()), 1)


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
        dd = h["dynamic_demand_deviation_pct"]
        red = h["error_reduction_x"]
        print(f"[06_fairco2] (golden) RUP misattributes shared carbon "
              f"{dd['RUP']['avg']}% avg / {dd['RUP']['worst']}% worst vs fair Shapley; "
              f"Fair-CO2 -> {dd['fair_co2']['avg']}% / {dd['fair_co2']['worst']}% "
              f"(~{red['dynamic_demand_avg_x']}x), at ~{h['shapley_speedup_x']:,}x less compute")
        return

    # --- SETUP / hook: "your carbon bill depends on your neighbor" ---------------
    # embodied_cf_colocation_matrix[row=job, col=partner] = embodied carbon (gCO2e)
    # attributed to `job` when it shares the node with `partner`; col "nothing" =
    # the job running alone. The SAME job's attribution swings ~2x across partners.
    emb = pd.read_csv(EMB_MATRIX).set_index("workload")

    def swing(wl):
        row = emb.loc[wl]
        lo, hi = float(row.min()), float(row.max())
        return {
            "isolated_gco2e": round(float(row["nothing"]), 4),
            "with_spark_gco2e": round(float(row["spark"]), 4),
            "min_gco2e": round(lo, 4), "min_partner": str(row.idxmin()),
            "max_gco2e": round(hi, 4), "max_partner": str(row.idxmax()),
            "swing_x": round(hi / lo, 2),
        }

    neighbor = {"llama": swing("llama"), "spark": swing("spark")}

    # --- REVEAL / climax: deviation from the fair (Shapley) ground truth ---------
    # Dynamic demand (Fig 7): RUP vs Demand-Proportional vs Fair-CO2.
    dd = pd.read_csv(DEMAND_CSV)
    demand = {
        "RUP": {"avg": mean_pct(dd, "baseline_avg_deviation (%)"),
                "worst": mean_pct(dd, "baseline_worst_case_deviation (%)")},
        "demand_proportional": {"avg": mean_pct(dd, "demand_proportional_avg_deviation (%)"),
                                "worst": mean_pct(dd, "demand_proportional_worst_case_deviation (%)")},
        "fair_co2": {"avg": mean_pct(dd, "temporal_shapley_avg_deviation (%)"),
                     "worst": mean_pct(dd, "temporal_shapley_worst_case_deviation (%)")},
        "n_simulations": int(len(dd)),
    }
    # Co-location interference (Figs 8-9): RUP vs Fair-CO2's interference adjustment.
    co = pd.read_csv(INTERF_CSV)
    interf = {
        "RUP": {"avg": mean_pct(co, "baseline_deviation_from_shapley (%)"),
                "worst": mean_pct(co, "worst_case_baseline_deviation (%)")},
        "fair_co2": {"avg": mean_pct(co, "adjusted_deviation_from_shapley (%)"),
                     "worst": mean_pct(co, "worst_case_adjusted_deviation (%)")},
        "n_simulations": int(len(co)),
    }

    def ratio(a, b):
        return round(a / b, 1)

    red = {
        "dynamic_demand_avg_x": ratio(demand["RUP"]["avg"], demand["fair_co2"]["avg"]),
        "dynamic_demand_worst_x": ratio(demand["RUP"]["worst"], demand["fair_co2"]["worst"]),
        "interference_avg_x": ratio(interf["RUP"]["avg"], interf["fair_co2"]["avg"]),
        "interference_worst_x": ratio(interf["RUP"]["worst"], interf["fair_co2"]["worst"]),
    }

    # --- figures -----------------------------------------------------------------
    grouped_bars(
        fig / "fairco2_neighbor_swing.png",
        groups=["Llama-3-8B", "Spark"],
        series={
            "running alone": [neighbor["llama"]["isolated_gco2e"], neighbor["spark"]["isolated_gco2e"]],
            "sharing the node w/ Spark": [neighbor["llama"]["with_spark_gco2e"], neighbor["spark"]["with_spark_gco2e"]],
        },
        title="Your carbon bill depends on your neighbor",
        subtitle=(f"same job, ~2x swing in attributed embodied carbon just from co-location "
                  f"(Llama {neighbor['llama']['swing_x']}x, Spark {neighbor['spark']['swing_x']}x)"),
        ylabel="attributed embodied carbon (gCO₂e)",
        colors=["#bb5566", "#3b7a57"],
        unit="", ann_fmt="{:.3f}", figsize=(7.4, 4.6),
    )
    grouped_bars(
        fig / "fairco2_deviation.png",
        groups=["Average case", "Worst case"],
        series={
            "RUP — industry default": [demand["RUP"]["avg"], demand["RUP"]["worst"]],
            "Demand-Proportional": [demand["demand_proportional"]["avg"], demand["demand_proportional"]["worst"]],
            "Fair-CO₂ (ours)": [demand["fair_co2"]["avg"], demand["fair_co2"]["worst"]],
        },
        title="The industry-default split misattributes each job by ~80%",
        subtitle=(f"deviation from a fair (Shapley) ground truth\nFair-CO₂ cuts the error "
                  f"{red['dynamic_demand_avg_x']}-{red['dynamic_demand_worst_x']}x, at "
                  f"~{SHAPLEY_SPEEDUP_X:,}x less compute"),
        ylabel="deviation from fair share (%)",
        colors=["#bb5566", "#ddaa33", "#3b7a57"],
    )
    grouped_bars(
        fig / "fairco2_interference.png",
        groups=["Average case", "Worst case"],
        series={
            "RUP — industry default": [interf["RUP"]["avg"], interf["RUP"]["worst"]],
            "Fair-CO₂ (ours)": [interf["fair_co2"]["avg"], interf["fair_co2"]["worst"]],
        },
        title="Co-location interference: Fair-CO₂ vs proportional",
        subtitle=(f"deviation from fair share — Fair-CO₂ cuts the error "
                  f"{red['interference_avg_x']}-{red['interference_worst_x']}x"),
        ylabel="deviation from fair share (%)",
        colors=["#bb5566", "#3b7a57"], figsize=(7.4, 4.6),
    )

    # --- cross-segment handoffs (frame WHAT hardware's carbon is being split) ----
    def maybe(name):
        p = HERE / "inputs" / name
        return json.loads(p.read_text()) if p.exists() else None

    seg1, seg5 = maybe("from_01_act.json"), maybe("from_05_eserve.json")

    result = {
        "segment": "06_fairco2",
        "tool": "Fair-CO2",
        "anchor": "Shared server carbon attributed across co-located cloud jobs",
        "headline": {
            "claim": (
                "Splitting shared cloud carbon proportionally (RUP, the industry default = "
                "Google operational accounting + Green Software Foundation SCI) misattributes "
                "each job by ~80% on average and up to ~279% vs a fair, game-theoretic "
                "(Shapley) ground truth. Fair-CO2 approximates the fair share and cuts that "
                "error ~4-6x, at ~600,000x less compute than exact Shapley."
            ),
            "dynamic_demand_deviation_pct": demand,
            "interference_deviation_pct": interf,
            "error_reduction_x": red,
            "shapley_speedup_x": SHAPLEY_SPEEDUP_X,
            "neighbor_swing": neighbor,
        },
        "fairness_note": (
            f"RUP (resource-utilization-proportional) deviates from the fair Shapley share "
            f"by {demand['RUP']['avg']}% on average ({demand['RUP']['worst']}% worst case) "
            f"under dynamic demand; demand-proportional improves to "
            f"{demand['demand_proportional']['avg']}%/{demand['demand_proportional']['worst']}%; "
            f"Fair-CO2 reaches {demand['fair_co2']['avg']}%/{demand['fair_co2']['worst']}%. "
            f"Under co-location interference RUP deviates {interf['RUP']['avg']}%/"
            f"{interf['RUP']['worst']}%, Fair-CO2 {interf['fair_co2']['avg']}%/"
            f"{interf['fair_co2']['worst']}%. The hook: the same job's attributed embodied "
            f"carbon already swings ~2x just from its neighbor (Llama "
            f"{neighbor['llama']['swing_x']}x, Spark {neighbor['spark']['swing_x']}x)."
        ),
        "method": {
            "baseline_RUP": "Resource-Utilization-Proportional (Google operational accounting + GSF SCI)",
            "ground_truth": "Shapley value -- the provably fair division of a shared cost",
            "fair_co2": "Fair-CO2's temporal- and interference-aware Shapley approximation",
            "reduction": ("mean per-simulation deviation-from-Shapley over Fair-CO2's committed "
                          "Monte-Carlo ref-sim-results (reproduces paper Figs 7-9)"),
            "sources": [
                str(DEMAND_CSV.relative_to(walk.SUITE_ROOT)),
                str(INTERF_CSV.relative_to(walk.SUITE_ROOT)),
                str(EMB_MATRIX.relative_to(walk.SUITE_ROOT)),
            ],
        },
        # PRESERVED for lib/verify_chain.py: it reads these three keys from this
        # segment's golden to confirm the cross-tool carbon handoffs line up.
        "server_embodied_budget": {
            "source": "Fair-CO2 colocation/process_colocation_sweep.py (ACT-derived)",
            "ACT_cpu_chip_cf_gco2e": 18530,
            "from_segment1_R740_kgco2e": (seg1 or {}).get("server_embodied_kgco2e"),
            "from_segment5_H100_kgco2e": (seg5 or {}).get("gpu_embodied_kgco2e"),
            "note": ("The embodied carbon being divided fairly here is exactly the hardware "
                     "quantified upstream: ACT's R740 server (segment 1) and EServe's H100 "
                     "node (segment 5)."),
        },
        "figures": [
            "fairco2_deviation.png",
            "fairco2_interference.png",
            "fairco2_neighbor_swing.png",
        ],
    }
    walk.save_result(HERE, result)
    print(f"[06_fairco2] deviation from fair Shapley share (dynamic demand): "
          f"RUP {demand['RUP']['avg']}%/{demand['RUP']['worst']}% (avg/worst), "
          f"Demand-Prop {demand['demand_proportional']['avg']}%/{demand['demand_proportional']['worst']}%, "
          f"Fair-CO2 {demand['fair_co2']['avg']}%/{demand['fair_co2']['worst']}% "
          f"-> ~{red['dynamic_demand_avg_x']}-{red['dynamic_demand_worst_x']}x less error at "
          f"~{SHAPLEY_SPEEDUP_X:,}x less compute")


if __name__ == "__main__":
    main()
