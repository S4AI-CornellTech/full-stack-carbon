#!/usr/bin/env python3
"""Segment 5 - EServe: embodied carbon of provisioning an NVIDIA H100 HGX node.

Imports EServe's own GPUCarbonCalculator (installed editable in the eserve env)
and evaluates it on the committed H100HGX config. EServe scales every component
by execution_time / lifetime, so we pass the full lifetime (ratio = 1) to get
the full embodied "provisioning" cost using EServe's own code.

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

from server_carbon import GPUCarbonCalculator, json_to_gpuspecs  # noqa: E402

GPU = "H100HGX"
CONFIG = walk.SUITE_ROOT / "EServe" / "config" / "gpuconfigs.json"


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
        print(f"[05_eserve] (golden) {GPU} embodied carbon: "
              f"{res['headline']['gpu_embodied_kgco2e']:,.1f} kgCO2e")
        return

    cfg = json.loads(CONFIG.read_text())[GPU]
    specs = json_to_gpuspecs(cfg)
    calc = GPUCarbonCalculator(specs)

    lifetime_hours = specs.lifetime_years * 365 * 24
    full = calc.calculate_total_cf(execution_time_hours=lifetime_hours)  # ratio=1 -> full embodied
    comp = {k: round(v, 2) for k, v in full.items() if k != "total"}
    total = round(full["total"], 1)

    walk.bar_chart(
        fig / "eserve_h100_breakdown.png",
        labels=list(comp.keys()),
        values=[comp[k] for k in comp],
        title=f"NVIDIA {GPU} embodied carbon by component (EServe)",
        color="#5566bb",
    )

    # Optional context: compare against the R740 server from segment 1 (if committed).
    context = {}
    r740 = HERE / "inputs" / "from_01_act.json"
    if r740.exists():
        context["r740_server_embodied_kgco2e"] = json.loads(r740.read_text()).get("server_embodied_kgco2e")

    result = {
        "segment": "05_eserve",
        "tool": "EServe",
        "anchor": f"NVIDIA {GPU}",
        "headline": {"gpu_embodied_kgco2e": total},
        "breakdown_kgco2e": comp,
        "context": context,
        "handoff": {
            "gpu": GPU,
            "gpu_embodied_kgco2e": total,
            "soc_kgco2e": comp.get("SoC"),
            "memory_kgco2e": comp.get("memory"),
            "memory_type": cfg.get("memory_type"),
            "soc_node_nm": cfg.get("process_node"),
            "note": "Full embodied carbon of one accelerator (time_ratio=1). EServe "
                    "allocates a slice of this to a workload via execution_time/lifetime; "
                    "segment 6 does that allocation across co-located jobs.",
        },
    }
    walk.save_result(HERE, result)
    extra = ""
    if context:
        extra = f"  [R740 server was {context['r740_server_embodied_kgco2e']:,.0f} kgCO2e]"
    print(f"[05_eserve] {GPU} embodied carbon: {total:,.1f} kgCO2e  "
          f"(memory {comp.get('memory')} / SoC {comp.get('SoC')} / PDN {comp.get('PDN')}){extra}")

    dst = HERE.parent / "06_fairco2" / "inputs"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "from_05_eserve.json").write_text(json.dumps(result["handoff"], indent=2) + "\n")


if __name__ == "__main__":
    main()
