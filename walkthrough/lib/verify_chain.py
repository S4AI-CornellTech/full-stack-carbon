#!/usr/bin/env python3
"""Verify the walkthrough's committed handoffs line up across segments.

Each segment commits its handoff into the next segment's inputs/. This checks
those committed values match the producing segment's golden result, so the
"the numbers line up across tools" claim is mechanically true on pristine
submodules. Exits non-zero on any mismatch.
"""
import json
import sys
from pathlib import Path

WALK = Path(__file__).resolve().parents[1]


def golden(seg, *keys):
    d = json.loads((WALK / seg / "golden" / "result.json").read_text())
    for k in keys:
        d = d[k]
    return d


def commit_input(seg, name, *keys):
    d = json.loads((WALK / seg / "inputs" / name).read_text())
    for k in keys:
        d = d[k]
    return d


checks = []


def check(desc, a, b, tol=1e-6):
    checks.append((abs(float(a) - float(b)) <= tol, desc, a, b))


act_server = golden("01_act", "handoff", "server_embodied_kgco2e")
check("ACT R740 embodied -> 05_eserve/inputs",
      act_server, commit_input("05_eserve", "from_01_act.json", "server_embodied_kgco2e"))
check("ACT R740 embodied -> 06_fairco2/inputs",
      act_server, commit_input("06_fairco2", "from_01_act.json", "server_embodied_kgco2e"))

es_gpu = golden("05_eserve", "handoff", "gpu_embodied_kgco2e")
check("EServe H100 embodied -> 06_fairco2/inputs",
      es_gpu, commit_input("06_fairco2", "from_05_eserve.json", "gpu_embodied_kgco2e"))

check("Fair-CO2 cites ACT R740 number",
      act_server, golden("06_fairco2", "server_embodied_budget", "from_segment1_R740_kgco2e"))
check("Fair-CO2 cites EServe H100 number",
      es_gpu, golden("06_fairco2", "server_embodied_budget", "from_segment5_H100_kgco2e"))

print("Walkthrough chain consistency")
print("=" * 60)
all_ok = True
for ok, desc, a, b in checks:
    print(f"  [{'OK ' if ok else 'FAIL'}] {desc}\n         {a} == {b}")
    all_ok = all_ok and ok

cf = golden("06_fairco2", "server_embodied_budget", "ACT_cpu_chip_cf_gco2e")
ps = golden("01_act", "handoff", "cpu_per_socket_kgco2e")
print("=" * 60)
print(f"  (info) Fair-CO2 hardcodes ACT_cpu_chip_cf = {cf} gCO2e for its Xeon node;")
print(f"         ACT segment-1 R740 per-socket CPU = {ps} kg (illustrative 28nm BOM).")
print(f"         Related by method, not identical — see segment 1/6 talking points.")

print("=" * 60)
print("ALL CONSISTENT" if all_ok else "MISMATCH DETECTED")
sys.exit(0 if all_ok else 1)
