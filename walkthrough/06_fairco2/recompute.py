#!/usr/bin/env python3
"""Segment 6 - Fair-CO2: fairly attribute the server's embodied carbon to co-located jobs.

Artifact-evaluation style: copy Fair-CO2's committed colocation matrices into a
throwaway FAIR_CO2 workdir, run Fair-CO2's *own* figure generator against them
(reproducing the paper's colocation heatmaps), then read the embodied-carbon
attribution matrix to show how co-locating Llama + Spark splits the shared
hardware's embodied carbon. The Fair-CO2 submodule is never modified.

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

import pandas as pd  # noqa: E402

FAIRCO2 = walk.SUITE_ROOT / "Fair-CO2"
REF = FAIRCO2 / "colocation" / "ref-results"
GEN = FAIRCO2 / "colocation" / "gen_colocation_sweep_figures.py"


def cell(df, row, col) -> float:
    return round(float(df.loc[row, col]), 4)


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
        print(f"[06_fairco2] (golden) Llama embodied attribution {h['llama_isolated']} "
              f"-> {h['llama_with_spark']} when co-located with Spark")
        return

    # --- AE recompute: run Fair-CO2's own figure generator on committed matrices ---
    work = fig / "work"
    (work / "colocation" / "results").mkdir(parents=True, exist_ok=True)
    (work / "figures").mkdir(parents=True, exist_ok=True)
    for csv in REF.glob("*.csv"):
        shutil.copy2(csv, work / "colocation" / "results" / csv.name)

    env = {**os.environ, "FAIR_CO2": str(work)}
    print("[06_fairco2] running Fair-CO2 colocation figure generator (AE) ...")
    subprocess.run([sys.executable, str(GEN)], check=True, env=env)
    for pdf in (work / "figures").glob("*.pdf"):
        shutil.copy2(pdf, fig / pdf.name)

    # --- embodied-carbon attribution: Llama & Spark, isolated vs co-located ---
    emb = pd.read_csv(work / "colocation" / "results" / "embodied_cf_colocation_matrix.csv")
    emb = emb.set_index("workload")
    vals = {
        "llama_isolated": cell(emb, "llama", "nothing"),
        "llama_with_spark": cell(emb, "llama", "spark"),
        "spark_isolated": cell(emb, "spark", "nothing"),
        "spark_with_llama": cell(emb, "spark", "llama"),
    }
    walk.grouped_bar(
        fig / "fairco2_attribution.png",
        groups=["Llama", "Spark"],
        series={
            "run alone": [vals["llama_isolated"], vals["spark_isolated"]],
            "co-located (Llama+Spark)": [vals["llama_with_spark"], vals["spark_with_llama"]],
        },
        title="Fair-CO2: embodied carbon attributed per workload",
        ylabel="attributed embodied carbon (gCO2e)",
        colors={"run alone": "#bb5566", "co-located (Llama+Spark)": "#3b7a57"},
    )

    def maybe(name):
        p = HERE / "inputs" / name
        return json.loads(p.read_text()) if p.exists() else None

    seg1, seg5 = maybe("from_01_act.json"), maybe("from_05_eserve.json")

    result = {
        "segment": "06_fairco2",
        "tool": "Fair-CO2",
        "anchor": "Dell R740 node, Llama-3-8B + Spark co-located",
        "headline": vals,
        "fairness_note": (
            "Run alone, each job carries the full shared-hardware embodied carbon for "
            f"its runtime. Co-located, Fair-CO2 splits it: Llama {vals['llama_isolated']} "
            f"-> {vals['llama_with_spark']}, Spark {vals['spark_isolated']} "
            f"-> {vals['spark_with_llama']} (gCO2e)."
        ),
        "server_embodied_budget": {
            "source": "Fair-CO2 colocation/process_colocation_sweep.py (ACT-derived)",
            "ACT_cpu_chip_cf_gco2e": 18530,
            "from_segment1_R740_kgco2e": (seg1 or {}).get("server_embodied_kgco2e"),
            "from_segment5_H100_kgco2e": (seg5 or {}).get("gpu_embodied_kgco2e"),
        },
        "figures": [
            "fairco2_attribution.png",
            "2a_runtime_relative_change_matrix_new.pdf",
            "2b_proportional_energy_relative_change_matrix_new.pdf",
        ],
    }
    walk.save_result(HERE, result)
    print(f"[06_fairco2] embodied attribution (gCO2e): Llama "
          f"{vals['llama_isolated']}->{vals['llama_with_spark']}, Spark "
          f"{vals['spark_isolated']}->{vals['spark_with_llama']}")

    shutil.rmtree(work, ignore_errors=True)  # tidy the bulky workdir


if __name__ == "__main__":
    main()
