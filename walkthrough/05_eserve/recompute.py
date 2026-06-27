#!/usr/bin/env python3
"""Segment 5 - EServe (EcoServe): the carbon hinge of server provisioning.

EcoServe is a carbon-aware LLM-serving *provisioning* framework. Its Section-3
carbon MODEL (the part committed here) makes two of the paper's findings concrete
on a single NVIDIA H100 HGX node:

  Obs 2  the HOST system -- not the GPU -- dominates embodied carbon.
  Obs 3  on a clean grid, embodied carbon OUTWEIGHS operational carbon.

A GPU-only breakdown (the previous version of this segment) shows neither. So we
drive EServe's OWN server_carbon calculators on the committed H100HGX config:

  * GPUCarbonCalculator           -> per-accelerator embodied (~103 kgCO2e).
  * CPUCarbonCalculator on the
    H100HGX ``cpu_configs``        -> the host embodied (~1,084 kgCO2e: a 2 TB
    (2 TB DRAM, 22.7 TB SSD)          DRAM + 22.7 TB SSD host that dwarfs the GPU).

Storage is priced on act_core's shared bare-die NAND model (nand_10nm), the same
source ACT/MicroGreen use -- so the host is DRAM-led (DRAM ~580 > SSD ~227 kg).

Then we amortise the whole 8-GPU node's embodied carbon over its 4-year life and
cross it against operational carbon at the paper's three grid intensities to find
the ~11 gCO2e/kWh crossover below which manufacturing outweighs everything you
will ever spend running it -- a clean-grid edge case, since real grids sit above it.

NB the Section-4 "4R" ILP optimizer (EcoServe's 47% headline) is NOT committed,
so this segment demonstrates the *Observations*, not the optimization, and leads
with ratios/directions -- the artifact's absolute per-part numbers do not match
the paper to the digit.

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

from server_carbon import (  # noqa: E402
    GPUCarbonCalculator, CPUCarbonCalculator,
    json_to_gpuspecs, json_to_cpuspecs, MemoryType,
)

GPU = "H100HGX"
CONFIG = walk.SUITE_ROOT / "EServe" / "config" / "gpuconfigs.json"

# An H100 HGX board carries 8 GPUs plus one host (CPU + DRAM + SSD).
N_GPUS = 8
UTILIZATION = 0.8
# Paper's three grid intensities (gCO2e/kWh): clean (Sweden) / world-avg / high (California).
GRID_CI = {"clean (Sweden)": 17, "world avg": 261, "high (California)": 501}


def crossover_figure(out_png, *, embodied_rate, power_kw, util, grid_ci, crossover_ci):
    """Operational carbon rate (rising with grid CI) vs the flat amortized embodied
    rate; mark the CI below which embodied wins."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    xmax = 560.0
    ci = np.linspace(0, xmax, 200)
    op = power_kw * util * ci
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    ax.axvspan(0, crossover_ci, color="#cfe8d6", alpha=0.7,
               label=f"embodied-dominated (CI < ~{crossover_ci:.1f})")
    ax.plot(ci, op, color="#bb5566", lw=2,
            label=f"operational  ({power_kw:.1f} kW node @ {int(util*100)}% util)")
    ax.axhline(embodied_rate, color="#3b7a57", lw=2, ls="--",
               label=f"embodied  ({embodied_rate:.0f} g/hr, 4-yr amortized)")
    ax.axvline(crossover_ci, color="#444", lw=1, ls=":")
    ax.annotate(f"crossover ~{crossover_ci:.1f} gCO2e/kWh",
                xy=(crossover_ci, embodied_rate),
                xytext=(crossover_ci + 70, embodied_rate * 3.0),
                arrowprops=dict(arrowstyle="->", color="#444"), fontsize=9)
    for name, c in grid_ci.items():
        y = power_kw * util * c
        ax.scatter([c], [y], color="#bb5566", zorder=5)
        left = c > 0.6 * xmax
        ax.annotate(f"{name}\n{c} -> {y:,.0f} g/hr", (c, y), textcoords="offset points",
                    xytext=(-8 if left else 8, 8), ha="right" if left else "left", fontsize=8)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, power_kw * util * xmax * 1.02)
    ax.set_xlabel("grid carbon intensity (gCO2e/kWh)")
    ax.set_ylabel("carbon rate (gCO2e per node-hour)")
    ax.set_title(f"Below ~{crossover_ci:.0f} gCO2e/kWh, embodied outweighs ALL operational (EcoServe Obs 3)")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper center")
    fig.tight_layout()
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
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
        print(f"[05_eserve] (golden) HOST {h['host_embodied_kgco2e']:,.0f} vs GPU "
              f"{h['gpu_embodied_kgco2e']:,.0f} kgCO2e (host = "
              f"{h['host_pct_of_per_accelerator']:.1f}% of per-accelerator embodied); "
              f"embodied > operational below ~{h['crossover_ci_gco2e_per_kwh']:.1f} gCO2e/kWh")
        return

    cfg = json.loads(CONFIG.read_text())[GPU]

    # --- (a) GPU: per-accelerator embodied via EServe's own GPUCarbonCalculator (ratio=1) ---
    gspecs = json_to_gpuspecs(cfg)
    lifetime_hours = gspecs.lifetime_years * 365 * 24
    gpu_full = GPUCarbonCalculator(gspecs).calculate_total_cf(execution_time_hours=lifetime_hours)
    gpu_total = round(gpu_full["total"], 1)                 # ~154.2

    # --- (b) HOST: CPUCarbonCalculator on the H100HGX cpu_configs (2 TB DRAM, 22.7 TB SSD) ---
    cpu_cfg = cfg["cpu_configs"]
    cspecs = json_to_cpuspecs(cpu_cfg)                      # CPUSpecs: mem 2000 GB, storage 22720 GB
    host_calc = CPUCarbonCalculator(
        lifetime_years=gspecs.lifetime_years,
        execution_time=lifetime_hours,                      # ratio=1 -> full embodied
        ssd_capacity_gb=cspecs.storage_size,                # 22720 GB SSD
        memory_capacity_gb=cspecs.cpu_memory,               # 2000 GB DRAM
        memory_type=MemoryType.DDR4,                        # host DRAM
        die_area_mm2=1600.0, process_node_nm=7,             # Xeon 8480C: enable the CPU-die term
    )                                                       #   (EServe returns ACT Table-12 const)
    host = host_calc.calculate_total_cf()
    host_total = round(host["total_cf"], 1)                 # ~1083.7
    host_ssd = round(host_calc.calculate_ssd_cf(), 1)       # ~227.2 (act_core nand_10nm)
    host_dram = round(host_calc.calculate_memory_cf(), 1)   # 580.0
    host_other = round(host_total - host_ssd - host_dram, 1)

    # --- Obs 2: host vs GPU (lead with ratios) ---
    per_accel = round(gpu_total + host_total, 1)            # one accelerator's share = 1 GPU + host
    host_pct = round(100 * host_total / per_accel, 1)       # ~91.3 %
    storage_dram_vs_gpu = round((host_ssd + host_dram) / gpu_total, 1)  # ~7.8x

    # --- Obs 3: whole-node embodied vs operational crossover ---
    node_embodied_kg = round(N_GPUS * gpu_total + host_total, 1)        # 8 GPU + host ~1908
    embodied_rate = round(node_embodied_kg * 1000 / lifetime_hours, 1)  # ~54 g/hr
    power_kw = round((N_GPUS * gspecs.tdp + cspecs.cpu_tdp) / 1000.0, 2)  # ~5.95 kW
    op_rates = {name: round(power_kw * UTILIZATION * ci, 1) for name, ci in GRID_CI.items()}
    crossover_ci = round(embodied_rate / (power_kw * UTILIZATION), 1)   # ~11.4 gCO2e/kWh

    # --- figures ---
    walk.bar_chart(
        fig / "eserve_host_vs_gpu.png",
        labels=["GPU\n(1 accel.)", "Host SSD\n(22.7 TB)", "Host DRAM\n(2 TB)", "Host other"],
        values=[gpu_total, host_ssd, host_dram, host_other],
        title=(f"Host dominates embodied carbon: host {host_total:,.0f} "
               f"vs GPU {gpu_total:,.0f} kgCO2e (EcoServe Obs 2)"),
        color=["#5566bb", "#bb5566", "#cc7733", "#999999"],
        figsize=(7.8, 4.6),
    )
    crossover_figure(
        fig / "eserve_embodied_vs_operational.png",
        embodied_rate=embodied_rate, power_kw=power_kw, util=UTILIZATION,
        grid_ci=GRID_CI, crossover_ci=crossover_ci,
    )

    # context: the R740 general-purpose server from segment 1, if committed
    context = {}
    r740 = HERE / "inputs" / "from_01_act.json"
    if r740.exists():
        context["r740_server_embodied_kgco2e"] = json.loads(r740.read_text()).get("server_embodied_kgco2e")

    handoff = {
        "gpu": GPU,
        "gpu_embodied_kgco2e": gpu_total,            # per accelerator (verify_chain consumes this)
        "soc_kgco2e": round(gpu_full["SoC"], 2),
        "memory_kgco2e": round(gpu_full["memory"], 2),
        "memory_type": cfg.get("memory_type"),
        "soc_node_nm": cfg.get("process_node"),
        "host_embodied_kgco2e": host_total,          # full host: CPU board + 2 TB DRAM + 22.7 TB SSD
        "host_storage_kgco2e": host_ssd,
        "host_dram_kgco2e": host_dram,
        "per_accelerator_embodied_kgco2e": per_accel,   # 1 GPU + host (the Obs-2 "host is ~95%" base)
        "n_gpus_per_node": N_GPUS,
        "server_embodied_kgco2e": node_embodied_kg,     # full HGX node = 8 GPU + host (total)
        "embodied_rate_gco2e_per_hr": embodied_rate,
        "crossover_ci_gco2e_per_kwh": crossover_ci,
        "note": (
            "EcoServe Section-3 carbon model on the H100 HGX node. The HOST (2 TB DRAM + "
            "22.7 TB SSD) dominates embodied carbon, not the GPU (Obs 2: host ~91% of one "
            "accelerator's embodied; storage+DRAM ~8x the GPU). Storage is priced on "
            "act_core's shared bare-die NAND (nand_10nm, as ACT/MicroGreen), so the host is "
            "DRAM-led (DRAM 580 > SSD 227 kg). Amortized over a 4-yr life the node's embodied "
            "rate (~54 gCO2e/hr) outweighs operational only below ~11 gCO2e/kWh (Obs 3) -- "
            "operational dominates on essentially every real grid; embodied wins only on the "
            "very cleanest. Fair-CO2 (seg 6) time-allocates this embodied carbon to "
            "co-located queries; gpu_embodied_kgco2e is the per-accelerator figure it cites."
        ),
    }

    result = {
        "segment": "05_eserve",
        "tool": "EServe / EcoServe",
        "anchor": f"NVIDIA {GPU} node ({N_GPUS} GPU + host)",
        "headline": {
            "gpu_embodied_kgco2e": gpu_total,
            "host_embodied_kgco2e": host_total,
            "host_pct_of_per_accelerator": host_pct,
            "storage_dram_vs_gpu_ratio": storage_dram_vs_gpu,
            "embodied_rate_gco2e_per_hr": embodied_rate,
            "crossover_ci_gco2e_per_kwh": crossover_ci,
        },
        "host_breakdown_kgco2e": {"ssd": host_ssd, "dram": host_dram,
                                  "other": host_other, "total": host_total},
        "gpu_breakdown_kgco2e": {k: round(v, 2) for k, v in gpu_full.items() if k != "total"},
        "operational_rate_gco2e_per_hr": op_rates,
        "node": {"n_gpus": N_GPUS, "power_kw": power_kw, "utilization": UTILIZATION,
                 "lifetime_years": gspecs.lifetime_years, "node_embodied_kgco2e": node_embodied_kg},
        "context": context,
        "handoff": handoff,
    }
    walk.save_result(HERE, result)

    extra = ""
    if context:
        extra = f"  [R740 server (seg 1) was {context['r740_server_embodied_kgco2e']:,.0f} kg]"
    print(f"[05_eserve] HOST {host_total:,.0f} vs GPU {gpu_total:,.0f} kgCO2e "
          f"(host = {host_pct:.1f}% of per-accelerator embodied; storage+DRAM = "
          f"{storage_dram_vs_gpu:.0f}x the GPU). Node embodied {embodied_rate:.0f} g/hr "
          f"> operational below ~{crossover_ci:.1f} gCO2e/kWh.{extra}")

    dst = HERE.parent / "06_fairco2" / "inputs"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "from_05_eserve.json").write_text(json.dumps(handoff, indent=2) + "\n")


if __name__ == "__main__":
    main()
