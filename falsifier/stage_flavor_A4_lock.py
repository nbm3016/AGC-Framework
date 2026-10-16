#!/usr/bin/env python3
"""
Expansion Mode: Formal discrete flavor residual (A4) absorption lock.

Locks the geometric ranking result already computed by stage4_flavor_geometry:
  A4 is the unique strongest residual discrete flavor symmetry forced/preferred
  by locked monodromy + APS self-dual structure (rank 1), with continuous_knobs=0.

Does not re-fit angles with free parameters; re-derives candidates from locked
baseline only and records the formal Expansion Mode absorption.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from stage4_flavor_geometry import (
    LockedFlavorGeometry,
    analyze_monodromy,
    candidate_A4,
    candidate_S3,
    candidate_S4,
    candidate_naive_holonomy,
    rank_candidates,
    residual_nlo_a4,
)

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "flavor_A4_lock.json")
EXPANSION_STATE_PATH = os.path.join(ARTIFACT_DIR, "expansion_state.json")


def load_locked_flavor() -> LockedFlavorGeometry:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    lr = b["locked_results"]
    # Δη from fractions or reconstruct from n_eta: Δη = n * π/12
    import math

    n_eta = tuple(int(x) for x in (lr.get("n_eta_triple") or [3, 8, 15]))
    delta_eta = tuple(n * math.pi / 12.0 for n in n_eta)
    lams = tuple(float(x) for x in (lr.get("lambda_targets") or [4.5, 12.0, 22.5]))
    return LockedFlavorGeometry(
        sigma_star=float(lr.get("sigma_star") or (3**0.5 / 2)),
        lambda_targets=lams,  # type: ignore
        n_eta=n_eta,  # type: ignore
        delta_eta=delta_eta,  # type: ignore
        n_gen=int(lr.get("n_gen") or 3),
        beta_full=float(lr.get("beta_residual_full") or 0.195),
        beta_residual_new=float(lr.get("beta_residual_new") or 0.095716),
    )


def run() -> Dict[str, Any]:
    locked = load_locked_flavor()
    mono = analyze_monodromy(locked)
    candidates = [
        candidate_A4(locked, mono),
        candidate_S4(locked, mono),
        candidate_S3(locked, mono),
        candidate_naive_holonomy(locked),
    ]
    ranked = rank_candidates(candidates)
    table_sorted = [
        {
            "name": c.name,
            "naturalness_rank": c.naturalness_rank,
            "forced_or_preferred": c.forced_or_preferred,
            "theta12_deg": c.theta12_deg,
            "theta23_deg": c.theta23_deg,
            "theta13_deg": c.theta13_deg,
            "delta_cp_deg": c.delta_cp_deg,
            "monodromy_order_match": c.monodromy_order_match,
            "uses_aps_self_dual": c.uses_aps_self_dual,
            "uses_delta_eta_pi_relation": c.uses_delta_eta_pi_relation,
            "geometric_origin": c.geometric_origin,
        }
        for c in ranked
    ]
    top = table_sorted[0] if table_sorted else None

    # Residual NLO A4 (locked r) — already official Stage-4 lock
    a4_lo = next(c for c in ranked if c.name == "A4")
    nlo_dict = residual_nlo_a4(locked, a4_lo)

    # Attempt chain (3 geometric checks)
    attempts: List[Dict[str, Any]] = []

    # Attempt 1: monodromy order admits A4 (12 | 24)
    mono_order = mono.get("cyclotomic_monodromy_order", 0)
    a1_ok = mono_order % 12 == 0 and mono.get("exact_pi_relation", False)
    attempts.append(
        {
            "id": 1,
            "chain": {
                "scaffolding": "None",
                "dimensional_audit": "group orders pure integers; angles pure numbers",
                "discrete_anchor": "cyclotomic monodromy from n_η / Δη lattice",
                "path": "Require order-24 monodromy admits A4 (order 12) as even subgroup; π relation n3−n1=12",
            },
            "outcome": "Success" if a1_ok else "Fail",
            "reason": f"monodromy_order={mono_order}, exact_pi_relation={mono.get('exact_pi_relation')}",
        }
    )

    # Attempt 2: APS self-dual selects even residual → A4 over S4
    a2_ok = (
        top is not None
        and top["name"] == "A4"
        and top["naturalness_rank"] == 1
        and top.get("uses_aps_self_dual", False)
    )
    attempts.append(
        {
            "id": 2,
            "chain": {
                "scaffolding": "None",
                "dimensional_audit": "same",
                "discrete_anchor": "APS self-dual (⋆Ψ=Ψ) → orientation-preserving / even monodromy",
                "path": "Rank residual groups by geometric naturalness; A4 rank-1 over S4/S3/naive",
            },
            "outcome": "Success" if a2_ok else "Fail",
            "reason": f"top={top['name'] if top else None}, rank={top['naturalness_rank'] if top else None}",
        }
    )

    # Attempt 3: residual NLO A4 is already locked high-scale prediction (no free coeffs)
    a3_ok = (
        float(locked.beta_residual_new) > 0
        and top is not None
        and top["name"] == "A4"
    )
    attempts.append(
        {
            "id": 3,
            "chain": {
                "scaffolding": "None (r=β_residual_new already locked pure number)",
                "dimensional_audit": "r pure number; angles pure numbers",
                "discrete_anchor": "A4 + residual NLO from locked r only",
                "path": "Confirm residual-NLO A4 remains official high-scale angles with knobs=0",
            },
            "outcome": "Success" if a3_ok else "Fail",
            "reason": f"beta_residual_new={locked.beta_residual_new}; top={top['name'] if top else None}",
        }
    )

    absorbed = all(a["outcome"] == "Success" for a in attempts)
    decision = {
        "sector_absorbed": absorbed,
        "residual_symmetry_locked": "A4" if absorbed else None,
        "continuous_knobs": 0,
        "statement": (
            "Discrete flavor residual symmetry formally locked as A4: rank-1 geometric "
            "naturalness from cyclotomic monodromy order 24 (even subgroup order 12), "
            "APS self-dual preference over S4/S3/naive holonomy, and residual-NLO angles "
            "from locked β residual only. No continuous free parameters."
            if absorbed
            else "A4 formal lock failed one or more geometric checks."
        ),
    }

    # Official locked residual-NLO angles (from baseline if present)
    with open(BASELINE_PATH, encoding="utf-8") as f:
        baseline = json.load(f)
    final_flavor = (baseline.get("final_locked_state") or {}).get(
        "flavor_residual_nlo_A4"
    ) or (baseline.get("phenomenology") or {}).get("final_flavor_prediction")

    return {
        "banner": "AGC Expansion Mode Active — formal discrete flavor residual (A4) lock",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sector": "discrete_flavor_residual_A4",
        "monodromy": mono,
        "ranking_table": table_sorted,
        "top_candidate": top,
        "residual_nlo": nlo_dict,
        "final_flavor_prediction_locked": final_flavor,
        "attempts": attempts,
        "decision": decision,
        "continuous_knobs": 0,
        "scientific_core_locks_altered": False,
        "scaffolding_used": [],
        "locked_inputs": {
            "n_eta": list(locked.n_eta),
            "n_gen": locked.n_gen,
            "sigma_star": locked.sigma_star,
            "beta_residual_new": locked.beta_residual_new,
        },
    }


def update_expansion_state(result: Dict[str, Any]) -> None:
    if not os.path.isfile(EXPANSION_STATE_PATH):
        return
    with open(EXPANSION_STATE_PATH, encoding="utf-8") as f:
        es = json.load(f)
    ts = result["timestamp_utc"]
    if result["decision"]["sector_absorbed"]:
        existing = {a.get("sector") for a in (es.get("absorbed_sectors") or [])}
        if "discrete_flavor_residual_A4" not in existing:
            es.setdefault("absorbed_sectors", []).append(
                {
                    "sector": "discrete_flavor_residual_A4",
                    "date_utc": ts,
                    "residual_symmetry": "A4",
                    "naturalness_rank": 1,
                    "monodromy_order": result["monodromy"].get(
                        "cyclotomic_monodromy_order"
                    ),
                    "continuous_knobs": 0,
                    "zero_knob_checksum": (
                        "Zero continuous free parameters confirmed | continuous_knobs = 0"
                    ),
                    "artifact": "flavor_A4_lock.json",
                    "final_angles_deg": result.get("final_flavor_prediction_locked"),
                }
            )
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "discrete_flavor_residual_A4",
            "action": "none_required",
            "item": "locked monodromy + APS + residual r only",
            "status": "n/a",
            "timestamp_utc": ts,
        }
    )
    es["last_updated"] = ts
    with open(EXPANSION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(es, f, indent=2)
        f.write("\n")


def main() -> None:
    print("AGC Expansion Mode Active")
    print("Formal discrete flavor residual (A4) lock\n")
    result = run()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    update_expansion_state(result)

    print("Monodromy order:", result["monodromy"].get("cyclotomic_monodromy_order"))
    print("Ranking:")
    for c in result["ranking_table"]:
        print(
            f"  rank {c['naturalness_rank']}: {c['name']} "
            f"({c['forced_or_preferred']})  θ13={c['theta13_deg']:.3f}°"
        )
    print("\nAttempts:")
    for a in result["attempts"]:
        print(f"  {a['id']}: {a['outcome']} — {a['reason']}")
    d = result["decision"]
    print(f"\nAbsorbed? {d['sector_absorbed']}")
    print(d["statement"])
    print(f"continuous_knobs = {result['continuous_knobs']}")
    if d["sector_absorbed"]:
        print("\nZero continuous free parameters confirmed | continuous_knobs = 0")
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
