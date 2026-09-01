#!/usr/bin/env python3
"""
Full anomaly-cancellation probe — locked data only, zero knobs.

Does not re-optimize Stages 1–3. Does not introduce representations or GS coefficients.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "full_anomaly_probe.json")

C2 = Fraction(4, 3)
N_ETA = (3, 8, 15)
J1 = (0.5, 1.0, 1.5)
LOCKED_R = 0.095716


def load_locked() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def as_index(n_gen: int) -> int:
    return max(0, int(round(2.0 * n_gen - 6.0)))


def spin_weight(j1: float) -> int:
    return int(round(2.0 * j1 + 1.0))


def probe() -> Dict[str, Any]:
    b = load_locked()
    lr = b.get("locked_results") or {}
    n_eta = tuple(lr.get("n_eta_triple") or N_ETA)
    n_sum = int(sum(n_eta))
    eta_piece = C2 * Fraction(n_sum, 12)
    trace = sum(spin_weight(j) * n for j, n in zip(J1, n_eta))
    idx3 = as_index(3)
    idx4 = as_index(4)
    rows: List[Dict[str, Any]] = [
        {
            "anomaly_type": "Gauge (local Tr F³ / 4D cubic)",
            "forced_cancellation": False,
            "form_or_obstruction": (
                f"Wall descent δI/δA = (5/3)N_gen r0² + C2 η → {eta_piece} ≠ 0 at r0=0; "
                "independent of N_gen. No locked 4D representation content for Tr F³."
            ),
            "requires_extra_parameter": True,
            "result": (
                "NO — leftover 26/9 is a nonzero rational, not cancellation. "
                "Tr F³ cannot be evaluated without free representations."
            ),
        },
        {
            "anomaly_type": "Mixed gauge–gravitational",
            "forced_cancellation": False,
            "form_or_obstruction": "Tr F tr R² / hypercharge factors not in locked data",
            "requires_extra_parameter": True,
            "result": "NO — U(1) charges and mixed polynomials are under-determined",
        },
        {
            "anomaly_type": "Pure gravitational (tr R⁴, (tr R²)²)",
            "forced_cancellation": False,
            "form_or_obstruction": "Full chiral spin / gravitino content not specified",
            "requires_extra_parameter": True,
            "result": "NO — I12 gravitational pieces cannot be computed from locked spectrum",
        },
        {
            "anomaly_type": "Global / discrete (APS index, AS integer, trace mod 6)",
            "forced_cancellation": True,
            "form_or_obstruction": (
                f"N_gen=3; AS index max(0,2N_gen−6)={idx3} (vs {idx4} at N_gen=4); "
                f"Σ(2j₁+1)n={trace}≡{trace % 6} (mod 6)"
            ),
            "requires_extra_parameter": False,
            "result": (
                "PARTIAL — discrete APS/AS/trace-mod-6 sector is forced and parameter-free. "
                "This is not Witten SU(2) or a full global-anomaly theorem."
            ),
        },
        {
            "anomaly_type": "Green–Schwarz counterterms",
            "forced_cancellation": False,
            "form_or_obstruction": "b_i, α_ij not present in locked baseline",
            "requires_extra_parameter": True,
            "result": "NO — introducing GS coefficients would be new continuous knobs",
        },
        {
            "anomaly_type": "Wall inflow residual as full cancellation",
            "forced_cancellation": False,
            "form_or_obstruction": f"C2(3) Σn/12 = {eta_piece} (≠ 0)",
            "requires_extra_parameter": False,
            "result": "NO — Stage 2A residual does not vanish; 'inflow balanced' ≠ Tr F³=0",
        },
    ]
    discrete_forced = True
    full = False
    return {
        "banner": "FULL ANOMALY CANCELLATION PROBE COMPLETE – ZERO KNOBS PRESERVED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "locked_numerics_unchanged": True,
        "full_anomaly_cancellation_achieved": False,
        "status": "Partial",
        "decision": "Partial",
        "discrete_sector_forced": discrete_forced,
        "all_anomalies_cancelled": full,
        "inflow_residual_exact": str(eta_piece),
        "inflow_residual_vanishes": eta_piece == 0,
        "as_index_at_3": idx3,
        "self_dual_trace": trace,
        "self_dual_trace_mod6": trace % 6,
        "reason": (
            "Locked data force the discrete APS / AS-index / trace-mod-6 sector "
            f"and a nonzero wall η-piece {eta_piece}. They do not force cancellation "
            "of local gauge, mixed, or pure gravitational polynomials, nor Witten "
            "SU(2). Completing those would require representations or GS coefficients "
            "not in the locked baseline."
        ),
        "anomalies": rows,
        "locked_snapshot": {
            "n_gen": 3,
            "sigma_star": lr.get("sigma_star"),
            "beta_residual_new": lr.get("beta_residual_new") or LOCKED_R,
            "n_eta": list(n_eta),
            "continuous_knobs": 0,
        },
    }


def main() -> None:
    print("AGC full anomaly-cancellation probe (zero knobs)\n")
    res = probe()
    print(f"{'Anomaly type':<48} {'Forced?':<10} Result")
    print("-" * 110)
    for row in res["anomalies"]:
        yn = "YES" if row["forced_cancellation"] else "NO"
        print(f"{row['anomaly_type']:<48} {yn:<10} {row['result']}")
    print()
    print(f"Final status: full anomaly cancellation achieved? {res['status']}")
    print(f"continuous_knobs: {res['continuous_knobs']}")
    print(f"wall residual: {res['inflow_residual_exact']} (vanishes={res['inflow_residual_vanishes']})")
    print(res["banner"])
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
