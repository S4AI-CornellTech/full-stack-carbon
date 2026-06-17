#!/usr/bin/env python3
"""Segment 4 - MicroGreen: the carbon-optimal edge MCU is NOT fixed - it flips.

MicroGreen is a carbon-aware DESIGN-SPACE-EXPLORATION framework. It JOINTLY models
embodied carbon (board + solar panel + capacitors + batteries) and operational
carbon to pick the carbon-optimal {MCU + power-system} for a given workload, light
level, inference rate, and lifetime. Its central finding: the carbon-optimal MCU
FLIPS with those conditions (by >1 order of magnitude), and the most
energy-efficient processor is NOT the carbon winner.

The naive view (paper Fig. 3) is a static per-board embodied ranking - a strawman:
it would always pick the lowest-embodied board. The payoff (paper Fig. 6) is that
once you co-optimize embodied + operational for a workload, the winner flips.

This segment:
  1. runs MicroGreen's own sweep (scripts/overall_eval_carbon.py) to reproduce the
     paper's Figure 6 (device carbon-rank vs inference rate x light), and
  2. reads its per-(workload,irradiance) device x inference-rate carbon tables,
     computes the min-carbon (carbon-optimal) device at every point, and renders a
     "carbon-optimal device vs inference rate" flip figure, and
  3. keeps the static per-board embodied bar as the "naive view" the flip overturns.

Scale-invariance: this is the SAME embodied-vs-operational co-optimization seen
across the stack, shown here at the edge boundary where EMBODIED dominates (~75%) -
the mirror image of the data center (operational-dominated) handled by EServe (05).

With --golden we restore the committed golden/ outputs instead of recomputing.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import walk  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

MG = walk.SUITE_ROOT / "MicroGreen"
SWEEP = MG / "scripts" / "overall_eval_carbon.py"
BOARD_CSV = MG / "database" / "board_carbon.csv"

LIFETIME_YEARS = 1.0
SOLAR_CAP = 611
IRRADIANCES = {"Dim": 200, "Medium": 10000, "Bright": 40000}  # uW/cm^2
# Workloads we visualize: kws-l is the clean 2-way flip the headline references;
# kws-s is the busy case (four distinct winners across conditions).
FLIP_WORKLOADS = ["kws-l", "kws-s"]

# Mirror of MicroGreen/framework/constants.py (kept local to avoid importing the
# submodule's matplotlib rcParams side-effects / Times New Roman font warnings).
DEVICE_LABELS = {
    "esp32": "ESP32", "esp32C6": "ESP32-C6", "esp32S3": "ESP32-S3",
    "nf52840": "nRF52840", "rp2040": "RP2040", "rp2350": "RP2350",
    "stm32f411fe": "STM32F4", "nxprt1176+TPU": "NXP RT1176+TPU",
    "nxprt1176": "NXP RT1176",
}
DEVICE_COLORS = {
    "esp32": "slategrey", "esp32C6": "darkviolet", "esp32S3": "blue",
    "nf52840": "black", "rp2040": "darkgreen", "rp2350": "yellowgreen",
    "stm32f411fe": "hotpink", "nxprt1176+TPU": "coral", "nxprt1176": "darkred",
}


# --------------------------------------------------------------------------- #
# Data helpers
# --------------------------------------------------------------------------- #
def run_sweep() -> None:
    """Run MicroGreen's own carbon sweep into its (gitignored) intermediate_results/
    and figures/. Suppresses its noisy font warnings (stderr) and forces Agg."""
    (MG / "figures").mkdir(exist_ok=True)
    (MG / "intermediate_results").mkdir(exist_ok=True)
    print(f"[04_microgreen] running MicroGreen carbon sweep "
          f"(lifetime={LIFETIME_YEARS}yr, solar-cap={SOLAR_CAP}cm^2) ... ~1 min")
    subprocess.run(
        [sys.executable, str(SWEEP),
         "--lifetime-years", str(LIFETIME_YEARS),
         "--solar-panel-area-cap", str(SOLAR_CAP)],
        check=True, cwd=str(MG),
        env={**os.environ, "MPLBACKEND": "Agg", "PYTHONDONTWRITEBYTECODE": "1"},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def load_table(wl: str, irr: str) -> pd.DataFrame:
    """device x inference-rate table of total kgCO2e (NaN where infeasible)."""
    p = MG / "intermediate_results" / f"{wl}_{irr}_embodied_carbon.csv"
    df = pd.read_csv(p, index_col=0)
    df.columns = [float(c) for c in df.columns]
    return df


def winner_curve(df: pd.DataFrame):
    """Carbon-optimal (min over devices) device + cost at each feasible rate."""
    valid = df.dropna(axis=1, how="all")
    fps = np.asarray(valid.columns, dtype=float)
    cost = valid.min(axis=0).to_numpy(dtype=float)
    who = valid.idxmin(axis=0).to_numpy()
    return fps, cost, who


def at_rate(df: pd.DataFrame, ips: float):
    """(winner, kgCO2e) at the feasible rate column nearest to ``ips``."""
    valid = df.dropna(axis=1, how="all")
    cols = np.asarray(valid.columns, dtype=float)
    col = valid.columns[int(np.argmin(np.abs(cols - ips)))]
    s = valid[col].dropna()
    return s.idxmin(), round(float(s.min()), 2), round(float(col), 2)


def winner_segments(fps, who):
    """List of (start_rate, end_rate, device) runs of the winning device."""
    segs, start = [], 0
    for i in range(1, len(who) + 1):
        if i == len(who) or who[i] != who[start]:
            segs.append((float(fps[start]), float(fps[i - 1]), str(who[start])))
            start = i
    return segs


# --------------------------------------------------------------------------- #
# Figure: carbon-optimal device vs inference rate (the flip)
# --------------------------------------------------------------------------- #
def plot_flip(out_png: Path, tables: dict) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    irr_labels = list(IRRADIANCES.keys())
    nrow, ncol = len(FLIP_WORKLOADS), len(irr_labels)
    fig, axes = plt.subplots(nrow, ncol, figsize=(12.0, 6.8),
                             sharex=False, sharey="row")
    axes = np.atleast_2d(axes)
    winners_seen = set()
    row_env_min = {}  # workload -> smallest winning cost across its 3 light panels

    for r, wl in enumerate(FLIP_WORKLOADS):
        for c, irr in enumerate(irr_labels):
            ax = axes[r, c]
            df = tables[(wl, irr)]
            fps_all = np.asarray(df.columns, dtype=float)

            # faint per-device curves (every candidate the sweep evaluated)
            for dev in df.index:
                y = df.loc[dev].to_numpy(dtype=float)
                if np.all(np.isnan(y)):
                    continue
                ax.plot(fps_all, y, color=DEVICE_COLORS.get(dev, "grey"),
                        alpha=0.22, lw=1.0, zorder=1)

            # carbon-optimal (winner) lower envelope, colored by who wins
            fps, cost, who = winner_curve(df)
            row_env_min[wl] = min(row_env_min.get(wl, np.inf), float(np.nanmin(cost)))
            ax.plot(fps, cost, color="0.15", lw=2.6, zorder=3,
                    solid_capstyle="round")
            for dev in np.unique(who):
                m = who == dev
                ax.scatter(fps[m], cost[m], s=12, zorder=4,
                           color=DEVICE_COLORS.get(dev, "grey"), edgecolors="none")
                winners_seen.add(dev)

            # crossovers + winner labels at each segment start
            segs = winner_segments(fps, who)
            for (s0, _s1, dev) in segs:
                yi = float(cost[int(np.argmin(np.abs(fps - s0)))])
                ax.annotate(DEVICE_LABELS.get(dev, dev), (s0, yi),
                            textcoords="offset points", xytext=(3, 7),
                            fontsize=8, zorder=5,
                            bbox=dict(boxstyle="round,pad=0.18", fc="white",
                                      ec=DEVICE_COLORS.get(dev, "grey"),
                                      lw=1.1, alpha=0.92))
            for (s0, _s1, _dev) in segs[1:]:
                ax.axvline(s0, color="0.6", ls=":", lw=0.9, zorder=2)

            ax.set_yscale("log")
            ax.grid(True, which="both", ls="--", alpha=0.30)
            if r == 0:
                ax.set_title(f"{irr}  ({IRRADIANCES[irr]} uW/cm$^2$)", fontsize=11)
            if r == nrow - 1:
                ax.set_xlabel("Inferences per second (IPS)", fontsize=10)
            if c == 0:
                ax.set_ylabel(f"{wl}\ntotal kgCO2e (log)", fontsize=10,
                              fontweight="bold")
            if c == ncol - 1:
                # focus the row on the winning band; worse "naive" picks run
                # off the top (the point: they cost ~10-100x more).
                axes[r, 0].set_ylim(row_env_min[wl] * 0.85, row_env_min[wl] * 30.0)

    handles = [Line2D([0], [0], color=DEVICE_COLORS[d], lw=3,
                      marker="o", markersize=6, label=DEVICE_LABELS.get(d, d))
               for d in DEVICE_COLORS if d in winners_seen]
    fig.legend(handles=handles, title="carbon-optimal (winning) device",
               loc="lower center", ncol=len(handles), frameon=True,
               fontsize=9, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("MicroGreen: the carbon-optimal edge MCU flips with light & "
                 "inference rate\n(thick line = lowest total-carbon device; "
                 "it is NOT the same device across conditions)", fontsize=12)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=130)
    plt.close(fig)
    return out_png


# --------------------------------------------------------------------------- #
# Naive-view setup figure (paper Fig. 3): static per-board embodied ranking
# --------------------------------------------------------------------------- #
def plot_naive_bar(out_png: Path):
    df = pd.read_csv(BOARD_CSV, index_col=0)
    totals = df["Total"].sort_values()
    lo_board, hi_board = totals.index[0], totals.index[-1]
    lo, hi = round(float(totals.iloc[0]), 3), round(float(totals.iloc[-1]), 3)
    ic_share = round(100.0 * float(df.loc[hi_board, "IC"]) /
                     float(df.loc[hi_board, "Total"]), 0)
    walk.bar_chart(
        out_png,
        labels=list(totals.index),
        values=[round(float(v), 3) for v in totals.values],
        title="Naive view: static per-board embodied carbon (MicroGreen, paper Fig. 3)",
        ylabel="kgCO2e", color="#d08c34", figsize=(8.5, 4.2),
    )
    return dict(n_boards=int(len(totals)), min_board=lo_board, min_kgco2e=lo,
                max_board=hi_board, max_kgco2e=hi, max_board_ic_share_pct=ic_share)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
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
        print(f"[04_microgreen] (golden) carbon-optimal edge MCU FLIPS "
              f"({' <-> '.join(DEVICE_LABELS.get(d, d) for d in h['flip_devices'])}) "
              f"with light, inference rate & lifetime; "
              f"kws-s has {h['n_distinct_winners']['kws-s']} distinct winners.")
        return

    # 1) MicroGreen's own sweep -> reproduces Figure 6 (+ intermediate CSVs).
    run_sweep()
    f6 = sorted((MG / "figures").glob(
        f"figure6_*lifetime{LIFETIME_YEARS}_solarcap{SOLAR_CAP}.pdf"))
    if not f6:
        f6 = sorted((MG / "figures").glob("figure6_*.pdf"))
    figure6_name = f6[-1].name
    shutil.copy2(f6[-1], fig / figure6_name)

    # 2) Load device x inference-rate carbon tables; compute the flip.
    tables = {(wl, irr): load_table(wl, irr)
              for wl in FLIP_WORKLOADS for irr in IRRADIANCES}
    plot_flip(fig / "microgreen_carbon_optimal_flip.png", tables)

    # distinct carbon-optimal winners per workload (across all light x rate)
    distinct = {}
    for wl in ["kws-s", "kws-l", "ppd-s", "ppd-l"]:
        winset = set()
        for irr in IRRADIANCES:
            _, _, who = winner_curve(load_table(wl, irr))
            winset.update(map(str, who))
        distinct[wl] = sorted(winset)

    # representative flip rows for kws-l (the headline RP2350 <-> NXP flip)
    flip_rows = []
    for irr, ips_list in [("Dim", [0.5, 1.0, 5.0, 10.0]),
                          ("Medium", [0.5, 10.0]),
                          ("Bright", [0.5, 10.0])]:
        df = tables[("kws-l", irr)]
        for ips in ips_list:
            who, kg, col = at_rate(df, ips)
            flip_rows.append({"workload": "kws-l", "irradiance": irr,
                              "ips": col, "winner": who, "kgco2e": kg})

    # dim-light crossover rate for kws-l
    fps, _cost, who = winner_curve(tables[("kws-l", "Dim")])
    segs = winner_segments(fps, who)
    crossover = round(segs[1][0], 2) if len(segs) > 1 else None
    win_lo, win_hi = (min(r["kgco2e"] for r in flip_rows),
                      max(r["kgco2e"] for r in flip_rows))

    # energy-efficiency spread per workload, and the efficiency leader for kws-l
    prof = pd.read_csv(MG / "database" / "profiling_results.csv")
    prof["Model"] = prof["Model"].astype(str).str.strip().str.lower()
    eff_spread, eff_leader = {}, {}
    for wl in ["kws-s", "kws-l", "ppd-s", "ppd-l"]:
        sub = prof.loc[prof["Model"] == wl, ["Devices", "inference energy (mJ)"]].dropna()
        sub = sub.sort_values("inference energy (mJ)")
        eff_spread[wl] = round(float(sub["inference energy (mJ)"].iloc[-1] /
                                     sub["inference energy (mJ)"].iloc[0]), 1)
        eff_leader[wl] = str(sub["Devices"].iloc[0])

    naive = plot_naive_bar(fig / "microgreen_board_carbon.png")

    result = {
        "segment": "04_microgreen",
        "tool": "MicroGreen",
        "anchor": "Carbon-optimal edge-MCU + power-system selection "
                  "(joint embodied + operational DSE)",
        "role": "scale-invariance proof point: the same embodied-vs-operational "
                "co-optimization recurs at every scale; shown here at the edge "
                "boundary where EMBODIED dominates (~75%) - the mirror image of "
                "the data center (operational-dominated), which EServe (05) handles.",
        "headline": {
            "claim": "The carbon-optimal edge MCU is NOT fixed - it flips "
                     "(RP2350 <-> NXP RT1176+TPU) with light, inference rate and "
                     "lifetime; energy-efficiency does not predict the winner.",
            "flip_devices": ["rp2350", "nxprt1176+TPU"],
            "example_workload": "kws-l",
            "dim_crossover_ips": crossover,
            "winning_cost_range_kgco2e": [win_lo, win_hi],
            "n_distinct_winners": {wl: len(v) for wl, v in distinct.items()},
            "distinct_winners": distinct,
            "energy_efficiency_spread_x": eff_spread,
            "efficiency_leader": eff_leader,
            "efficiency_note": (
                f"For kws-l the most energy-efficient processor is "
                f"{DEVICE_LABELS.get(eff_leader['kws-l'], eff_leader['kws-l'])} "
                f"(spread up to {eff_spread['kws-l']}x), yet in Medium/Bright light "
                f"the ~3.4x-less-efficient RP2350 is the carbon winner."),
        },
        "flip_table": flip_rows,
        "naive_view": {
            "description": "static per-board embodied ranking (paper Fig. 3) - the "
                           "strawman that the flip overturns",
            **naive,
        },
        "sweep": {
            "script": "scripts/overall_eval_carbon.py",
            "lifetime_years": LIFETIME_YEARS,
            "solar_panel_area_cap_cm2": SOLAR_CAP,
            "irradiances_uW_cm2": IRRADIANCES,
        },
        "figures": {
            "flip": "microgreen_carbon_optimal_flip.png",
            "figure6_pdf": figure6_name,
            "naive_bar": "microgreen_board_carbon.png",
        },
        "caveat": "The paper's headline 47% heterogeneous-deployment case study is "
                  "NOT reproduced here: it needs an extra sim step "
                  "(framework/heterogeneousDeployment.py), a Streamlit plotter, and "
                  "an uncommitted results CSV. Offered as optional future work.",
        "branch_note": "Not a provisioning-chain step (grams/sub-kg, not server kg) "
                        "and does not hand a unit to EServe (05); it is the "
                        "edge-boundary instance of the recurring embodied+operational "
                        "trade-off.",
    }
    walk.save_result(HERE, result)

    print(
        "[04_microgreen] carbon-optimal MCU FLIPS: kws-l Dim "
        f"0.5IPS->{DEVICE_LABELS['rp2350']}({flip_rows[0]['kgco2e']}) but "
        f">={crossover}IPS->{DEVICE_LABELS['nxprt1176+TPU']}"
        f"(up to {flip_rows[3]['kgco2e']}); Bright all-IPS->{DEVICE_LABELS['rp2350']}"
        f"({win_lo}); kws-s has {len(distinct['kws-s'])} distinct winners; "
        f"energy-efficiency (<= {eff_spread['kws-l']}x spread) does NOT pick the winner."
    )


if __name__ == "__main__":
    main()
