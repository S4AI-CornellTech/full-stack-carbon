#!/usr/bin/env python3
"""Segment 4 - MicroGreen: the edge tier (a side-branch).

MicroGreen applies the same ACT-based embodied-carbon methodology to edge/IoT
microcontroller boards. We run MicroGreen's own component-composition plotter on
its committed board_carbon.csv (no hardware, no nested submodule) and summarize
the per-board embodied carbon. This is a parallel branch (grams, not server kg),
not a step in the provisioning chain.

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

MG = walk.SUITE_ROOT / "MicroGreen"
PLOTTER = MG / "scripts" / "carbon_component_composition_plotter.py"
CSV = MG / "database" / "board_carbon.csv"


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
        print(f"[04_microgreen] (golden) {h['n_boards']} edge boards, embodied carbon "
              f"{h['min_board']} ({h['min_kgco2e']}) .. {h['max_board']} ({h['max_kgco2e']}) kgCO2e")
        return

    # Run MicroGreen's own Figure-3 plotter (writes into MicroGreen/figures, which is gitignored).
    import os
    import subprocess
    (MG / "figures").mkdir(exist_ok=True)
    print("[04_microgreen] running MicroGreen board-composition plotter ...")
    subprocess.run([sys.executable, str(PLOTTER)], check=True, cwd=str(MG),
                   env={**os.environ, "MPLBACKEND": "Agg"},
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for pdf in (MG / "figures").glob("figure3_*"):
        shutil.copy2(pdf, fig / pdf.name)

    df = pd.read_csv(CSV, index_col=0)
    totals = df["Total"].sort_values()
    lo_board, hi_board = totals.index[0], totals.index[-1]
    lo, hi = round(float(totals.iloc[0]), 3), round(float(totals.iloc[-1]), 3)
    ic_share = round(100.0 * float(df.loc[hi_board, "IC"]) / float(df.loc[hi_board, "Total"]), 0)

    walk.bar_chart(
        fig / "microgreen_board_carbon.png",
        labels=list(totals.index),
        values=[round(float(v), 3) for v in totals.values],
        title="Edge MCU board embodied carbon (MicroGreen)",
        ylabel="kgCO2e",
        color="#d08c34",
        figsize=(8.5, 4.2),
    )

    result = {
        "segment": "04_microgreen",
        "tool": "MicroGreen",
        "anchor": "Edge/IoT MCU boards",
        "branch": "parallel edge tier (grams, not server kg) - not a provisioning-chain step",
        "headline": {
            "n_boards": int(len(totals)),
            "min_board": lo_board, "min_kgco2e": lo,
            "max_board": hi_board, "max_kgco2e": hi,
            "max_board_ic_share_pct": ic_share,
        },
        "note": "Per-board embodied carbon from MicroGreen's committed board_carbon.csv "
                "(itself ACT-derived). The IC dominates the heaviest board, echoing the "
                "silicon-centric view ACT gives for servers.",
    }
    walk.save_result(HERE, result)
    print(f"[04_microgreen] {len(totals)} edge boards: {lo_board} {lo} .. {hi_board} {hi} kgCO2e "
          f"(IC = {ic_share:.0f}% of the heaviest)")


if __name__ == "__main__":
    main()
