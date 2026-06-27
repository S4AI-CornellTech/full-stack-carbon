#!/usr/bin/env python3
"""Segment 6 - Fair-CO2 tutorial helper: fairly attribute a shared carbon budget across
co-located jobs, comparing the industry-default proportional (RUP) split to the fair
Shapley split — using Fair-CO2's OWN `peak_shapley`.

Participant-facing runner for the hands-on tutorial (see TUTORIAL.md). It does NOT touch the
canonical demo (run.sh / recompute.py) or its golden/handoff; the Fair-CO2 submodule is only
ever read.

  ./tutorial.sh --workloads exercises/workloads.json     proportional (RUP) vs fair (Shapley) split
  ./tutorial.sh --swing llama                            "your carbon bill depends on your neighbor"
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import walk  # noqa: E402,F401
import recompute as rc  # noqa: E402  reuse grouped_bars + EMB_MATRIX (recompute is import-safe)
import pandas as pd  # noqa: E402
sys.path.insert(0, str(walk.SUITE_ROOT / "Fair-CO2" / "forecast"))
from emb_shapley_lib import peak_shapley  # noqa: E402  Fair-CO2's real Shapley attribution


def _resolve(p):
    p = Path(p)
    return p if p.is_absolute() else HERE / p


def default_budget():
    """The shared embodied budget = ACT's R740 from segment 1 (committed handoff), in kg."""
    p = HERE / "inputs" / "from_01_act.json"
    if p.exists():
        return float(json.loads(p.read_text())["server_embodied_kgco2e"])
    return 1523.1


def token(name):
    return name.split()[0].strip("(),").lower()


def attribute(jobs, budget):
    names = [j["name"] for j in jobs]
    peaks = {j["name"]: float(j["peak"]) for j in jobs}
    rts = {j["name"]: float(j["resource_time"]) for j in jobs}
    total_rt = sum(rts.values())
    rup = {n: budget * rts[n] / total_rt for n in names}             # proportional to CPU x runtime
    shap = dict(zip(names, peak_shapley(names, peaks, rts, budget)))  # Fair-CO2's fair share
    return names, rup, shap


def main():
    ap = argparse.ArgumentParser(description="Fair-CO2 hands-on: proportional (RUP) vs fair (Shapley) carbon split")
    ap.add_argument("--workloads", default="exercises/workloads.json",
                    help="JSON: {jobs:[{name,peak,resource_time}], budget_source?}")
    ap.add_argument("--budget", type=float, default=None, help="shared embodied budget in kg (overrides config/default)")
    ap.add_argument("--swing", metavar="WORKLOAD", help="show a job's attributed-carbon swing across co-location partners")
    ap.add_argument("--fig", action="store_true", help="render the attribution chart into figures/tutorial/")
    ap.add_argument("--expect", action="append", default=[], metavar="KEY=VAL",
                    help="assert a value: <jobtoken>_rup|_shapley|_dev, or swing (repeatable)")
    args = ap.parse_args()

    results = {}

    if args.swing:
        emb = pd.read_csv(rc.EMB_MATRIX).set_index("workload")
        if args.swing not in emb.index:
            print(f"ERROR: '{args.swing}' not in matrix. Available: {', '.join(emb.index)}", file=sys.stderr)
            sys.exit(1)
        row = emb.loc[args.swing]
        lo, hi = float(row.min()), float(row.max())
        results["swing"] = round(hi / lo, 2)
        print(f"[06_fairco2 tutorial] '{args.swing}' attributed embodied carbon across co-location partners:")
        print(f"    isolated (nothing):  {float(row['nothing']):.4f} gCO2e")
        print(f"    sharing with spark:  {float(row['spark']):.4f} gCO2e")
        print(f"    min {lo:.4f} (w/ {row.idxmin()})    max {hi:.4f} (w/ {row.idxmax()})")
        print(f"  -> the same job's attributed bill swings {results['swing']}x just from its neighbor")
    else:
        cfg = json.loads(_resolve(args.workloads).read_text())
        jobs = cfg["jobs"]
        if args.budget is not None:
            budget = args.budget
        elif cfg.get("budget_source") == "from_01_act":
            budget = default_budget()
        else:
            budget = float(cfg.get("budget_kg", default_budget()))
        names, rup, shap = attribute(jobs, budget)
        print(f"[06_fairco2 tutorial] splitting {budget:,.1f} kgCO2e across {len(names)} co-located jobs")
        print(f"  {'job':<22}{'RUP (proportional)':>20}{'fair (Shapley)':>18}{'RUP error':>14}")
        for n in names:
            dev = abs(rup[n] - shap[n]) / shap[n] * 100 if shap[n] else 0.0
            over = "over-charges" if rup[n] > shap[n] else "under-charges"
            tok = token(n)
            results[f"{tok}_rup"] = round(rup[n], 1)
            results[f"{tok}_shapley"] = round(shap[n], 1)
            results[f"{tok}_dev"] = round(dev, 1)
            print(f"  {n:<22}{rup[n]:>16,.1f} kg{shap[n]:>14,.1f} kg{dev:>10.0f}% {over}")
        print("  -> RUP charges by resource-use; Shapley charges by marginal contribution to the peak the")
        print("     hardware was built for. A high-runtime / low-peak batch job is over-charged by RUP.")
        if args.fig:
            rc.grouped_bars(
                HERE / "figures" / "tutorial" / "attribution.png",
                groups=[token(n) for n in names],
                series={"RUP (proportional)": [round(rup[n], 1) for n in names],
                        "fair (Shapley)": [round(shap[n], 1) for n in names]},
                title="Proportional vs fair carbon attribution",
                subtitle="RUP over/under-charges jobs vs the fair Shapley share",
                ylabel="attributed embodied carbon (kgCO₂e)",
                colors=["#bb5566", "#3b7a57"], unit="", ann_fmt="{:.0f}",
            )

    failures = []
    for spec in args.expect:
        key, _, raw = spec.partition("=")
        key = key.strip()
        got = results.get(key)
        if got is None:
            failures.append(f"{key}: not computed")
            continue
        want = float(raw)
        tol = max(0.1, 0.005 * abs(want))
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
