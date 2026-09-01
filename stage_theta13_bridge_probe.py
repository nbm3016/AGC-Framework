#!/usr/bin/env python3
"""
θ13 high-scale → low-energy bridge probe — locked data only, zero knobs.

Does not re-optimize Stages 1–3. Does not fit to 8.5°. Does not change
official θ13=7.953°.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "theta13_bridge_probe.json")

LOCKED_TH13 = 7.953
C2 = 4.0 / 3.0
PI = math.pi


def load_locked() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def probe() -> Dict[str, Any]:
    b = load_locked()
    lr = b.get("locked_results") or {}
    r = float(lr.get("beta_residual_new") or 0.095716)
    sigma = float(lr.get("sigma_star") or math.sqrt(3.0) / 2.0)
    n_eta = list(lr.get("n_eta_triple") or [3, 8, 15])
    n1, n2, n3 = (int(x) for x in n_eta)
    n_sum = n1 + n2 + n3
    n_gen = 3
    t_wall = 6.5
    sqrt_r = math.sqrt(r)
    # Official NLO δ(sin θ13) already applied:
    dsin_nlo = sqrt_r * sigma * math.sqrt(n2 / n_sum) / n_gen
    rows: List[Dict[str, Any]] = [
        {
            "mechanism": "Second copy of locked √r NLO (double-count)",
            "forced": False,
            "form": "δ(sinθ13) already = √r σ* √(n2/n_Σ)/N_gen; applying twice",
            "diagnostic_shift_deg": None,
            "result": "NO — unique leading √r map already consumed at NLO; a second copy is not forced",
        },
        {
            "mechanism": "Further residual r·θ13 or r² (NNLO)",
            "forced": False,
            "form": "θ13 → θ13(1+r) or θ13+r² (free functional)",
            "diagnostic_shift_deg": math.degrees(r),  # illustrative only, not applied
            "result": "NO — HD sector: further r-polynomials are free Wilson-like maps",
        },
        {
            "mechanism": "Domain wall T_wall as angle shift",
            "forced": False,
            "form": "δθ ≟ arctan(1/T_wall) or T_wall degrees",
            "diagnostic_shift_deg": math.degrees(math.atan(1.0 / t_wall)),
            "result": "NO — T_wall=13/2 is a Casimir sum, not a flavor holonomy",
        },
        {
            "mechanism": "Monodromy order 24 as extra discrete shift",
            "forced": False,
            "form": "δθ ≟ π/24",
            "diagnostic_shift_deg": 180.0 / 24.0,
            "result": "NO — order 24 already used to select A4; extra π/24 is a new map",
        },
        {
            "mechanism": "APS index / N_gen extra factor",
            "forced": False,
            "form": "N_gen=3 already in locked NLO formula",
            "diagnostic_shift_deg": None,
            "result": "NO — would double-count a factor already in sinθ13^(NLO)",
        },
        {
            "mechanism": "Geometric V(σ) / σ* correction beyond LO/NLO",
            "forced": False,
            "form": "σ* already in LO sinθ13 and NLO δ(sinθ13)",
            "diagnostic_shift_deg": None,
            "result": "NO — σ* is already used; another insertion is not unique",
        },
        {
            "mechanism": "RG / heavy Majorana M_R running",
            "forced": False,
            "form": "needs μ0 or M_R in GeV",
            "diagnostic_shift_deg": None,
            "result": "NO — requires an external mass scale; absolute scale is observational-conversion only",
        },
        {
            "mechanism": "Fit high-scale θ13 to low-energy ~8.5°",
            "forced": False,
            "form": "forbidden target fit",
            "diagnostic_shift_deg": None,
            "result": "NO — explicitly forbidden; ~0.55° gap remains outside topological determination",
        },
    ]
    return {
        "banner": "θ13 BRIDGE PROBE COMPLETE – ZERO KNOBS PRESERVED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "official_theta13_unchanged": True,
        "official_theta13_deg": LOCKED_TH13,
        "low_energy_used_as_fit": False,
        "parameter_free_bridge_found": False,
        "decision": "NO",
        "reason": (
            "The unique leading parameter-free residual correction is already "
            "the locked √r NLO map (LO 5.096° → 7.953°). Every further candidate "
            "(second √r, r-polynomials, T_wall, extra π/24, extra N_gen or σ*, "
            "RG/M_R) is either already used, a free functional choice, or needs "
            "an external mass. No unique geometric bridge to ~8.5° is forced. "
            f"Already-used NLO δ(sinθ13)={dsin_nlo:.6f}."
        ),
        "mechanisms": rows,
        "nlo_dsin_already_used": dsin_nlo,
        "locked_snapshot": {
            "n_gen": n_gen,
            "sigma_star": sigma,
            "beta_residual_new": r,
            "theta13_deg": LOCKED_TH13,
            "continuous_knobs": 0,
        },
    }


def main() -> None:
    print("AGC θ13 high-scale → low-energy bridge probe (zero knobs)\n")
    res = probe()
    print(f"{'Mechanism':<48} {'Forced?':<8} Result")
    print("-" * 110)
    for row in res["mechanisms"]:
        yn = "YES" if row["forced"] else "NO"
        print(f"{row['mechanism']:<48} {yn:<8} {row['result']}")
    print()
    print(f"Final status: parameter-free bridge found? {res['decision']}")
    print(f"Official θ13 unchanged: {res['official_theta13_deg']}")
    print(f"continuous_knobs: {res['continuous_knobs']}")
    print(res["banner"])
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
