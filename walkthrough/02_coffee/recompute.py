#!/usr/bin/env python3
"""Segment 2 - COFFEE: embodied carbon of emerging FeFET (HZO) on-chip memory.

A labelled side-branch off segment 1's silicon: COFFEE extends ACT's CMOS
energy-per-area table with the ferroelectric layer (FEL) that HZO FeFET adds via
Atomic Layer Deposition. We evaluate COFFEE's own Fab_Logic model on the committed
HZO_5 device and read ACT/COFFEE's shared 28 nm CMOS EPA as the baseline, so the
figure shows the FEL fabrication-energy overhead in unit-safe kWh/cm2.

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

COFFEE = walk.SUITE_ROOT / "COFFEE"
sys.path.insert(0, str(COFFEE))
from src.logic_model_HZO import Fab_Logic  # noqa: E402

DEVICE = "HZO_5"


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
        print(f"[02_coffee] (golden) FeFET {DEVICE}: total EPA {h['fefet_epa_kwh_cm2']} kWh/cm2 "
              f"(CMOS baseline {h['cmos_epa_kwh_cm2']})")
        return

    devices = json.loads((COFFEE / "archs" / "fefet_extensions" / "fefet_devices.json").read_text())
    p = devices[DEVICE]
    fab = Fab_Logic(
        process_node=28,
        carbon_intensity="loc_taiwan",
        debug=False,
        override_thickness_hzo=p["Thickness_HZO"],
        override_thickness_al2o3=p["Thickness_AI2O3"],
    )
    fel_kwh = round(float(fab.get_fel_energy()), 4)
    fefet_epa = round(float(fab.get_fefet_epa()), 4)
    cpa = round(float(fab.get_cpa()), 4)

    epa_tbl = json.loads((COFFEE / "archs" / "CMOS_logic" / "epa.json").read_text())
    cmos_epa = round(float(epa_tbl["28nm"]), 4)
    fel_overhead_pct = round(100.0 * (fefet_epa - cmos_epa) / cmos_epa, 1)

    walk.bar_chart(
        fig / "coffee_epa_overhead.png",
        labels=["CMOS 28 nm", f"FeFET {DEVICE}\n(CMOS+FEL)"],
        values=[cmos_epa, fefet_epa],
        title="Energy-per-area: CMOS baseline vs HZO FeFET (COFFEE)",
        ylabel="EPA (kWh/cm2)",
        color="#a06cd5",
    )

    result = {
        "segment": "02_coffee",
        "tool": "COFFEE",
        "anchor": f"HZO FeFET eNVM ({DEVICE}), 28 nm",
        "branch": "side-branch off segment 1 silicon (emerging-memory what-if)",
        "headline": {
            "cmos_epa_kwh_cm2": cmos_epa,
            "fefet_epa_kwh_cm2": fefet_epa,
            "fel_process_energy_kwh": fel_kwh,
            "fel_epa_overhead_pct": fel_overhead_pct,
            "fefet_cpa": cpa,
        },
        "note": "EPA values (kWh/cm2) are the unit-safe comparison; the ferroelectric "
                "layer adds ALD fabrication energy on top of the shared ACT/COFFEE 28 nm "
                "CMOS baseline. CPA is COFFEE's carbon-per-area output for the FeFET stack.",
    }
    walk.save_result(HERE, result)
    print(f"[02_coffee] FeFET {DEVICE}: CMOS EPA {cmos_epa} -> FeFET EPA {fefet_epa} kWh/cm2 "
          f"(+{fel_overhead_pct}% from {fel_kwh} kWh FEL/ALD)")


if __name__ == "__main__":
    main()
