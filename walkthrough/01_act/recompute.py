#!/usr/bin/env python3
"""Segment 1 - ACT: recompute the Dell R740 embodied-carbon breakdown.

run.sh invokes ACT's CLI on act/boms/dellr740.yaml and drops the report in
figures/act_report.yaml. Here we aggregate that report by component class,
render a bar chart, write result.json (headline + handoff), and commit the
server budget into the downstream segments' inputs/ so they run standalone.

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

import yaml  # provided by the act env  # noqa: E402

# The dellr740 BOM models 2 CPU sockets (cpu.main0/1), each n_ics=2.
N_CPU_SOCKETS = 2


def _kg(value) -> float:
    """ACT writes pint quantities as strings like '11.27 kilogram'."""
    return float(str(value).split()[0])


def aggregate(report: dict) -> dict:
    by_dev = report["result_by_device"]["silicon_results"]
    classes = {"CPU": 0.0, "DRAM": 0.0, "SSD": 0.0}
    for name, vals in by_dev.items():
        kg = sum(_kg(v) for v in vals.values())
        if name.startswith("cpu"):
            classes["CPU"] += kg
        elif "dram" in name:          # incl. ssd.secondary.dram (a DRAM part)
            classes["DRAM"] += kg
        elif "ssd" in name:
            classes["SSD"] += kg
    return {k: round(v, 1) for k, v in classes.items()}


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
        res = walk.load_result(HERE, golden=True)
        print(f"[01_act] (golden) Dell R740 embodied carbon: "
              f"{res['headline']['server_embodied_kgco2e']:,.1f} kgCO2e")
        return

    report = yaml.safe_load((fig / "act_report.yaml").read_text())
    total = round(_kg(report["total_carbon"]), 1)
    classes = aggregate(report)

    walk.bar_chart(
        fig / "act_r740_breakdown.png",
        labels=list(classes.keys()),
        values=[classes[k] for k in classes],
        title="Dell PowerEdge R740 embodied carbon by component class (ACT)",
    )

    result = {
        "segment": "01_act",
        "tool": "ACT",
        "anchor": "Dell PowerEdge R740",
        "headline": {"server_embodied_kgco2e": total},
        "breakdown_kgco2e": classes,
        "handoff": {
            "server_embodied_kgco2e": total,
            "cpu_total_kgco2e": classes["CPU"],
            "cpu_per_socket_kgco2e": round(classes["CPU"] / N_CPU_SOCKETS, 2),
            "dram_total_kgco2e": classes["DRAM"],
            "ssd_total_kgco2e": classes["SSD"],
            "cpu_die_node": "28nm",
            "cpu_die_area_cm2": 6.98,
            "fab_ci": "coal",
            "note": (
                "Per-socket figure is from the illustrative dellr740 BOM "
                "(28nm / 6.98 cm2 / coal grid). Fair-CO2 (segment 6) uses an "
                "ACT-derived per-CPU constant of 18530 gCO2e computed for its "
                "actual Xeon Gold 6240R node; the two are related by method, "
                "not identical, because the BOM parameters differ."
            ),
        },
    }
    walk.save_result(HERE, result)
    print(f"[01_act] Dell R740 embodied carbon: {total:,.1f} kgCO2e  "
          f"(SSD {classes['SSD']:,.0f} / DRAM {classes['DRAM']:,.0f} / CPU {classes['CPU']:,.1f})")

    # Hand the server budget forward so segments 5 & 6 run standalone.
    for nxt in ("05_eserve", "06_fairco2"):
        dst = HERE.parent / nxt / "inputs"
        dst.mkdir(parents=True, exist_ok=True)
        (dst / "from_01_act.json").write_text(json.dumps(result["handoff"], indent=2) + "\n")


if __name__ == "__main__":
    main()
