#!/usr/bin/env python3
"""Segment 5 - EServe tutorial helper: model a GPU accelerator's embodied carbon, add the
host server it racks into, and find the embodied-vs-operational grid crossover.

Participant-facing runner for the hands-on tutorial (see TUTORIAL.md). It does NOT touch the
canonical demo (run.sh / recompute.py) or its golden/handoff: it reuses EServe's OWN
calculators and the segment's crossover math (imported from recompute.py).

  ./tutorial.sh --gpu H100HGX                                  one GPU's embodied breakdown
  ./tutorial.sh --gpu H100HGX --host                           + the host server (the reveal)
  ./tutorial.sh --gpu-file exercises/gpu_l4.json               an edited segment-local config
  ./tutorial.sh --gpu H100HGX --host --grid-ci 30 --util 0.5   sweep your region's grid
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import walk  # noqa: E402,F401  (kept for parity; SUITE_ROOT etc.)
import recompute as rc  # noqa: E402  reuse CONFIG, N_GPUS, UTILIZATION, GRID_CI, crossover_figure
from server_carbon import (  # noqa: E402  same import line as recompute.py (editable install)
    GPUCarbonCalculator, CPUCarbonCalculator,
    json_to_gpuspecs, json_to_cpuspecs, MemoryType,
)


def _resolve(p):
    p = Path(p)
    return p if p.is_absolute() else HERE / p


def load_gpu(args):
    if args.gpu_file:
        return json.loads(_resolve(args.gpu_file).read_text()), f"file:{args.gpu_file}"
    return json.loads(rc.CONFIG.read_text())[args.gpu], args.gpu


def host_cpu_configs(cfg, args):
    """Return (cpu_configs dict, borrowed_from-or-None). A GPU config may carry its own host
    (cpu_configs); host-less GPUs (e.g. L4) borrow a reference host so the reveal stays honest."""
    if cfg.get("cpu_configs"):
        return cfg["cpu_configs"], None
    src = args.host_source
    p = _resolve(src)
    if p.exists():
        d = json.loads(p.read_text())
        return d.get("cpu_configs", d), src
    return json.loads(rc.CONFIG.read_text())[src]["cpu_configs"], src


def main():
    ap = argparse.ArgumentParser(description="EServe hands-on: GPU + host embodied + grid crossover")
    ap.add_argument("--gpu", default="H100HGX", help="GPU key in EServe/config/gpuconfigs.json")
    ap.add_argument("--gpu-file", help="load a flat single-GPU JSON instead (segment-relative ok)")
    ap.add_argument("--host", action="store_true", help="also model the host server")
    ap.add_argument("--host-source", default="H100HGX",
                    help="GPU name or JSON file whose cpu_configs to borrow if the GPU has none")
    ap.add_argument("--n-gpus", type=int, default=rc.N_GPUS)
    ap.add_argument("--util", type=float, default=rc.UTILIZATION)
    ap.add_argument("--grid-ci", type=float, nargs="+", default=None,
                    help="grid carbon intensities gCO2e/kWh (default: the segment's three)")
    ap.add_argument("--fig", action="store_true", help="also render the crossover PNG into figures/tutorial/")
    ap.add_argument("--expect", action="append", default=[], metavar="KEY=VAL",
                    help="assert a value: gpu|host|crossover|per_accel|node|embodied_rate (repeatable)")
    args = ap.parse_args()

    cfg, label = load_gpu(args)

    # --- GPU: full-lifetime embodied (ratio = 1 -> the manufactured carbon) ---
    g = json_to_gpuspecs(cfg)
    lt_h = g.lifetime_years * 365 * 24
    gpu_full = GPUCarbonCalculator(g).calculate_total_cf(execution_time_hours=lt_h)
    gpu_total = round(gpu_full["total"], 1)
    results = {"gpu": gpu_total}

    print(f"[05_eserve tutorial] GPU {label}: embodied {gpu_total} kgCO2e")
    for k in ("SoC", "PDN", "memory", "cooling", "PCB", "connection"):
        if k in gpu_full:
            print(f"    {k:<11} {gpu_full[k]:>8.2f}")

    cspecs = None
    if args.host:
        host_cfg, borrowed = host_cpu_configs(cfg, args)
        cspecs = json_to_cpuspecs(host_cfg)
        host_calc = CPUCarbonCalculator(
            lifetime_years=g.lifetime_years, execution_time=lt_h,
            ssd_capacity_gb=cspecs.storage_size, memory_capacity_gb=cspecs.cpu_memory,
            memory_type=MemoryType.DDR4, die_area_mm2=1600.0, process_node_nm=7,
        )
        host = host_calc.calculate_total_cf()
        host_total = round(host["total_cf"], 1)
        host_ssd = round(host_calc.calculate_ssd_cf(), 1)
        host_dram = round(host_calc.calculate_memory_cf(), 1)
        host_other = round(host_total - host_ssd - host_dram, 1)
        per_accel = round(gpu_total + host_total, 1)
        host_pct = round(100 * host_total / per_accel, 1)
        ratio = round((host_ssd + host_dram) / gpu_total, 1)
        results.update({"host": host_total, "per_accel": per_accel})

        note = f"  (borrowed cpu_configs from {borrowed})" if borrowed else ""
        print(f"  HOST: {host_total} kgCO2e{note}")
        print(f"    SSD {host_ssd}   DRAM {host_dram}   other {host_other}")
        print(f"  -> host = {host_pct}% of one accelerator; storage+DRAM = {ratio}x the GPU")

        # --- crossover: whole-node embodied (amortized) vs operational on the grid ---
        node_embodied = round(args.n_gpus * gpu_total + host_total, 1)
        embodied_rate = round(node_embodied * 1000 / lt_h, 1)
        power_kw = round((args.n_gpus * g.tdp + cspecs.cpu_tdp) / 1000.0, 2)
        crossover_ci = round(embodied_rate / (power_kw * args.util), 1)
        results.update({"node": node_embodied, "embodied_rate": embodied_rate, "crossover": crossover_ci})

        grid = args.grid_ci if args.grid_ci is not None else list(rc.GRID_CI.values())
        print(f"  NODE ({args.n_gpus} GPU + host): embodied {node_embodied} kg "
              f"-> {embodied_rate} g/hr amortized; {power_kw} kW @ {int(args.util * 100)}% util")
        for ci in grid:
            op = round(power_kw * args.util * ci, 1)
            who = "embodied wins" if ci < crossover_ci else "operational wins"
            print(f"    grid CI {ci:>6.0f} g/kWh -> operational {op:>8.1f} g/hr   ({who})")
        print(f"  -> crossover ~{crossover_ci} gCO2e/kWh (below it, building outweighs running)")

        if args.fig:
            rc.crossover_figure(
                HERE / "figures" / "tutorial" / "crossover.png",
                embodied_rate=embodied_rate, power_kw=power_kw, util=args.util,
                grid_ci={f"CI {int(ci)}": ci for ci in grid}, crossover_ci=crossover_ci,
            )

    # --- optional CI assertions ---
    failures = []
    for spec in args.expect:
        key, _, raw = spec.partition("=")
        key = key.strip()
        got = results.get(key)
        if got is None:
            failures.append(f"{key}: not computed (need --host?)")
            continue
        want = float(raw)
        tol = max(0.05, 0.001 * abs(want))
        if abs(got - want) > tol:
            failures.append(f"{key}: got {got}, expected {want}")
    if failures:
        for f in failures:
            print(f"  EXPECT FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    if args.expect:
        print("  EXPECT OK")


if __name__ == "__main__":
    main()
