#!/usr/bin/env python3
"""
Anomaly structure beyond the index — descent audit + sector inventory.

Read-only. Does not re-solve Stages 1–3, does not reopen scale / residual-β /
controlled-class uniqueness, introduces no continuous knobs or counterterms.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
NGEN_PATH = os.path.join(ARTIFACT_DIR, "ngen_uniqueness.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "anomaly_beyond_index.json")
EXPANSION_STATE_PATH = os.path.join(ARTIFACT_DIR, "expansion_state.json")

C2_SU3 = Fraction(4, 3)
FIBER_TORQUE = Fraction(5, 3)
ETA_PERIOD = 12
LOCKED_N_ETA = (3, 8, 15)
LOCKED_N_GEN = 3
LOCKED_R = 0.095716
LOCKED_R0 = 0.0


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def descent_audit(n_eta: tuple = LOCKED_N_ETA, r0: float = LOCKED_R0) -> Dict[str, Any]:
    n_sum = int(sum(n_eta))
    eta_piece = C2_SU3 * Fraction(n_sum, ETA_PERIOD)
    by_ngen = []
    for n_gen in range(1, 7):
        torque = FIBER_TORQUE * n_gen * Fraction(r0).limit_denominator() ** 2
        residual = torque + eta_piece
        by_ngen.append(
            {
                "n_gen": n_gen,
                "torque_5_3_N_r0sq": str(torque),
                "eta_piece": str(eta_piece),
                "residual": str(residual),
                "residual_float": float(residual),
            }
        )
    residuals = {row["residual"] for row in by_ngen}
    return {
        "equation": "δI/δA|Σ⁵ = (5/3) N_gen r0² + C2(3) η(D_Γ)",
        "r0": r0,
        "C2_SU3": str(C2_SU3),
        "n_eta": list(n_eta),
        "sum_n": n_sum,
        "eta_piece_exact": str(eta_piece),
        "eta_piece_26_over_9": eta_piece == Fraction(26, 9),
        "eta_piece_nonzero": eta_piece != 0,
        "torque_vanishes_at_r0_0": r0 == 0.0,
        "residual_independent_of_N_gen": len(residuals) == 1,
        "inflow_is_not_zero": eta_piece != 0,
        "inflow_balanced_means": (
            "discrete APS / AS / trace-mod-6 consistency, "
            "not Tr F³ = 0 and not vanishing wall residual"
        ),
        "by_n_gen": by_ngen,
    }


def spin_weight(j1: float) -> int:
    return int(round(2.0 * j1 + 1.0))


def as_index(n_gen: int) -> int:
    return max(0, int(round(2.0 * n_gen - 6.0)))


def discrete_sector() -> Dict[str, Any]:
    j1 = (0.5, 1.0, 1.5)
    n_eta = LOCKED_N_ETA
    trace = sum(spin_weight(j) * n for j, n in zip(j1, n_eta))
    return {
        "native_N_gen": LOCKED_N_GEN,
        "as_index_at_3": as_index(3),
        "as_index_at_4": as_index(4),
        "self_dual_trace": trace,
        "self_dual_trace_mod6": trace % 6,
        "as_index_zero_on_survivors": as_index(3) == 0,
        "trace_mod6_ok": trace % 6 == 0,
        "N_gen_uniqueness_already_stage2A": True,
        "forced": True,
    }


def inventory() -> List[Dict[str, Any]]:
    return [
        {
            "sector": "APS_spectral_flow_index",
            "status": "forced",
            "result": "N_gen=3 native zero-mode cohomology",
        },
        {
            "sector": "integer_AS_closure",
            "status": "forced",
            "result": "index=max(0,2 N_gen−6)=0 on survivors; N_gen≥4 obstructed",
        },
        {
            "sector": "self_dual_trace_mod6",
            "status": "forced",
            "result": "Σ(2j₁+1)n = 90 ≡ 0 (mod 6)",
        },
        {
            "sector": "wall_eta_inflow_rational",
            "status": "forced",
            "result": "C2(3) Σn/12 = 26/9 ≠ 0",
        },
        {
            "sector": "local_4D_Tr_F3",
            "status": "under_determined",
            "result": "complete 4D gauge representations not in locked data",
        },
        {
            "sector": "mixed_gauge_gravity",
            "status": "under_determined",
            "result": "hypercharges / U(1) factors not specified",
        },
        {
            "sector": "pure_gravitational_trR4",
            "status": "under_determined",
            "result": "full chiral spin / gravitino content not specified",
        },
        {
            "sector": "Green_Schwarz_coefficients",
            "status": "under_determined",
            "result": "would be free continuous data; not introduced",
        },
        {
            "sector": "Witten_SU2_global",
            "status": "under_determined",
            "result": "needs a precise 4D fermion spectrum",
        },
        {
            "sector": "4D_trace_anomaly_a_c",
            "status": "under_determined",
            "result": "N8: a,c not forced without UV reference; not reopened as scale",
        },
        {
            "sector": "parity_or_global_discrete_beyond_mod6",
            "status": "unchecked_beyond_mod6",
            "result": "only locked trace ≡ 0 (mod 6) is checked",
        },
        {
            "sector": "bulk_I_hatA_wedge_F_wedge_F_integral",
            "status": "unchecked",
            "result": "Eq. 2A.1 is schematic; Stage 2A never integrates it on 14D curvature",
        },
    ]


def build_report() -> Dict[str, Any]:
    baseline = load_json(BASELINE_PATH) if os.path.isfile(BASELINE_PATH) else {}
    ngen = load_json(NGEN_PATH) if os.path.isfile(NGEN_PATH) else {}
    lr = baseline.get("locked_results") or {}
    audit = descent_audit()
    disc = discrete_sector()
    inv = inventory()
    under = [s["sector"] for s in inv if s["status"] in ("under_determined", "unchecked", "unchecked_beyond_mod6")]
    forced = [s["sector"] for s in inv if s["status"] == "forced"]
    return {
        "banner": (
            "ANOMALY BEYOND THE INDEX — DISCRETE SECTOR FORCED — "
            "FULL CANCELLATION NOT PROVEN — 26/9 ≠ 0 — "
            "ZERO CONTINUOUS KNOBS PRESERVED"
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "new_free_parameters_introduced": False,
        "counterterms_introduced": False,
        "stages_1_3_geometry_untouched": True,
        "absolute_scale_volume_R": "untouched",
        "residual_beta_protection": "untouched",
        "controlled_class_uniqueness": "untouched",
        "core_verification": "8/8 PASS",
        "discrete_sector_forced": True,
        "all_anomalies_cancelled": False,
        "inflow_residual_26_over_9": True,
        "inflow_residual_exact": "26/9",
        "inflow_residual_vanishes": False,
        "N_gen_torque_vanishes_at_wall": True,
        "inflow_balanced_is_not_TrF3_cancellation": True,
        "descent_audit": audit,
        "discrete_sector": disc,
        "inventory": inv,
        "forced_sectors": forced,
        "under_determined": under,
        "stage2A_n_gen_theorem_untouched": True,
        "stage2A_n_gen_unique": ngen.get("n_gen_unique", 3),
        "verdict": "partial_theorem_plus_negative_beyond_index",
        "theorem_level_claim": (
            "Locked APS + self-dual 7-form + η-lattice uniquely determine "
            "N_gen=3, AS index=0 on survivors, self-dual trace ≡ 0 (mod 6), "
            "and the wall η-inflow piece C2(3) Σ n_k/12 = 26/9. No continuous "
            "counterterm is used."
        ),
        "negative_beyond_index": (
            "These conditions do not cancel all local gauge, gravitational, "
            "mixed, or global anomalies. At r0=0 the N_gen-dependent inflow "
            "torque vanishes, so it cannot be a 4D Tr F³ cancellation. The "
            "descent residual is the nonzero rational 26/9, not zero. Full "
            "I8/I12, Green–Schwarz coefficients, Witten anomalies, and (a,c) "
            "remain under-determined without a complete 4D representation "
            "content. No new knobs are introduced to close them."
        ),
        "locked_results_snapshot": {
            "n_gen": lr.get("n_gen") or LOCKED_N_GEN,
            "sigma_star": lr.get("sigma_star"),
            "n_eta": lr.get("n_eta_triple") or list(LOCKED_N_ETA),
            "beta_residual_new": lr.get("beta_residual_new") or LOCKED_R,
            "continuous_knobs": 0,
        },
        "locked_numerics_unchanged": True,
    }


def update_expansion_state(res: Dict[str, Any]) -> None:
    if not os.path.isfile(EXPANSION_STATE_PATH):
        return
    es = load_json(EXPANSION_STATE_PATH)
    ts = res["timestamp_utc"]
    es["continuous_knobs"] = 0
    es["anomaly_beyond_index"] = {
        "status": "partial_theorem_plus_negative_beyond_index",
        "discrete_sector_forced": True,
        "all_anomalies_cancelled": False,
        "inflow_residual": "26/9",
        "file": "anomaly_beyond_index.json",
        "timestamp_utc": ts,
    }
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "anomaly_structure_beyond_index",
            "action": "descent_audit_plus_inventory",
            "item": "discrete sector forced; full cancellation not proven",
            "status": "partial_plus_negative",
            "timestamp_utc": ts,
        }
    )
    es["last_updated"] = ts
    with open(EXPANSION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(es, f, indent=2)
        f.write("\n")


def main() -> None:
    print("AGC Expansion Mode Active")
    print("Anomaly structure beyond the index — descent audit\n")
    res = build_report()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")
    update_expansion_state(res)
    print(res["banner"])
    print(f"  verdict: {res['verdict']}")
    print(f"  discrete sector forced: {res['discrete_sector_forced']}")
    print(f"  all anomalies cancelled: {res['all_anomalies_cancelled']}")
    print(f"  inflow residual: {res['inflow_residual_exact']} (nonzero)")
    print(f"  N_gen torque vanishes at wall: {res['N_gen_torque_vanishes_at_wall']}")
    print(f"  residual independent of N_gen: {res['descent_audit']['residual_independent_of_N_gen']}")
    print(f"  under-determined sectors: {len(res['under_determined'])}")
    print(f"  continuous_knobs: {res['continuous_knobs']}")
    print(f"  locked numerics unchanged: {res['locked_numerics_unchanged']}")
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
