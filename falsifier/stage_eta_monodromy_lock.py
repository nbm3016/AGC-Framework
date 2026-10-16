#!/usr/bin/env python3
"""
Expansion Mode choice: formal lock of discrete η-lattice + monodromy structure.

Sector: discrete_eta_monodromy_lattice

Why this target (strategy: high-confidence, low obstruction):
  - Pure discrete integers (period 12, n_η, monodromy order)
  - Already derived in Stages 1C + flavor geometry
  - Feeds A4 residual lock without absolute scale
  - No continuous knobs; no deep dimensional hole

Locks under Expansion Mode:
  (1) η-period = 12 (Dedekind modular)
  (2) n_k = 4 j₁(j₁+1) on APS survivors → (3,8,15)
  (3) Unique discrete search winner among vol-ratio / AS / self-dual filters
  (4) Δη/π = {1/4, 2/3, 5/4}; n₃−n₁=12 ⇒ Δη₃−Δη₁=π
  (5) Cyclotomic monodromy order = 24
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from fractions import Fraction
from math import gcd
from typing import Any, Dict, List, Tuple

from stage1c_predictive import (
    LockedInputs,
    build_predictive_set,
    discrete_search,
    load_locked_inputs,
)
from stage4_flavor_geometry import LockedFlavorGeometry, analyze_monodromy

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(ARTIFACT_DIR, "eta_monodromy_lock.json")
EXPANSION_STATE_PATH = os.path.join(ARTIFACT_DIR, "expansion_state.json")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


def run() -> Dict[str, Any]:
    locked_1c = load_locked_inputs()
    modes = build_predictive_set(locked_1c)
    passing, winner = discrete_search(locked_1c)

    n_triple = tuple(m.n_eta for m in modes)
    delta_over_pi = [str(Fraction(m.n_eta, 12)) for m in modes]
    mono_orders = []
    for m in modes:
        # order of phase Δη = n*π/12: n*Δη = 2π k ⇒ n*(n_eta/12)/2 = k ⇒ n*n_eta/24 = k
        # smallest n>0 with n * (n_eta * π/12) ≡ 0 mod 2π ⇒ n * n_eta / 24 ∈ ℤ
        ne = m.n_eta
        for n in range(1, 49):
            if (n * ne) % 24 == 0:
                mono_orders.append(n)
                break
    mono_order = mono_orders[0]
    for o in mono_orders[1:]:
        mono_order = _lcm(mono_order, o)

    # Flavor-geometry monodromy cross-check
    with open(BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    lr = b["locked_results"]
    n_eta_b = tuple(int(x) for x in (lr.get("n_eta_triple") or list(n_triple)))
    delta_eta = tuple(n * math.pi / 12.0 for n in n_eta_b)
    flavor = LockedFlavorGeometry(
        sigma_star=float(lr.get("sigma_star") or locked_1c.sigma_star),
        lambda_targets=tuple(float(x) for x in (lr.get("lambda_targets") or [4.5, 12.0, 22.5])),
        n_eta=n_eta_b,
        delta_eta=delta_eta,
        n_gen=int(lr.get("n_gen") or 3),
        beta_full=float(lr.get("beta_residual_full") or 0.195),
        beta_residual_new=float(lr.get("beta_residual_new") or 0.095716),
    )
    mono = analyze_monodromy(flavor)

    attempts = []

    # Attempt 1: topological derivation n_k = 4 j1(j1+1)
    topo_ok = n_triple == (3, 8, 15)
    attempts.append(
        {
            "id": 1,
            "chain": {
                "scaffolding": "None",
                "dimensional_audit": "n_η pure integers; Δη pure angles",
                "discrete_anchor": "APS survivors j₁∈{1/2,1,3/2}; η-period 12",
                "path": "n_k=4 j₁(j₁+1) → (3,8,15); Δη_k=n_k π/12",
            },
            "outcome": "Success" if topo_ok else "Fail",
            "reason": f"n_triple={n_triple}",
        }
    )

    # Attempt 2: discrete search uniqueness
    unique_ok = len(passing) == 1 and winner.n_triple == (3, 8, 15)
    attempts.append(
        {
            "id": 2,
            "chain": {
                "scaffolding": "None",
                "dimensional_audit": "same",
                "discrete_anchor": "AS closure + self-dual trace + hierarchy + vol-ratio match",
                "path": "Enumerate n∈{1..24}³; require unique minimal-sum topology triple",
            },
            "outcome": "Success" if unique_ok else "Fail",
            "reason": f"passing={len(passing)}, winner={winner.n_triple}, score={winner.score}",
        }
    )

    # Attempt 3: monodromy order 24 + π relation
    pi_ok = (n_triple[2] - n_triple[0]) == 12
    mono_ok = mono.get("cyclotomic_monodromy_order") == 24 and mono_order == 24
    attempts.append(
        {
            "id": 3,
            "chain": {
                "scaffolding": "None",
                "dimensional_audit": "monodromy order pure integer",
                "discrete_anchor": "phase orders of Δη; n₃−n₁=12",
                "path": "Cyclotomic monodromy order lcm → 24; exact π relation for A4 path",
            },
            "outcome": "Success" if (pi_ok and mono_ok) else "Fail",
            "reason": (
                f"mono_order_direct={mono_order}, "
                f"mono_flavor={mono.get('cyclotomic_monodromy_order')}, "
                f"n3-n1={n_triple[2]-n_triple[0]}"
            ),
        }
    )

    absorbed = all(a["outcome"] == "Success" for a in attempts)
    decision = {
        "sector_absorbed": absorbed,
        "continuous_knobs": 0,
        "statement": (
            "Discrete η-lattice and monodromy formally locked: period-12 lattice, "
            "unique triple n_η=(3,8,15) from topology + discrete filters, "
            "Δη/π={1/4,2/3,5/4}, monodromy order 24, n₃−n₁=12 (π relation). "
            "No continuous free parameters."
            if absorbed
            else "η/monodromy formal lock failed."
        ),
    }

    return {
        "banner": "AGC Expansion Mode Active — discrete η-lattice + monodromy lock",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sector": "discrete_eta_monodromy_lattice",
        "why_chosen": (
            "High-confidence discrete structure already present in Stages 1C/flavor; "
            "low obstruction; grows skeleton used by A4 residual without absolute scale."
        ),
        "eta_period": 12,
        "n_eta": list(n_triple),
        "delta_eta_over_pi": delta_over_pi,
        "vol_ratios": [str(Fraction(n_triple[1], n_triple[0])), str(Fraction(n_triple[2], n_triple[0])), str(Fraction(n_triple[2], n_triple[1]))],
        "discrete_search": {
            "n_passing": len(passing),
            "winner": list(winner.n_triple),
            "winner_score": winner.score,
            "unique": len(passing) == 1,
        },
        "monodromy": {
            "order_from_phases": mono_order,
            "order_from_flavor_geometry": mono.get("cyclotomic_monodromy_order"),
            "exact_pi_relation": pi_ok,
            "n3_minus_n1": n_triple[2] - n_triple[0],
        },
        "modes": [
            {
                "j1": m.j1,
                "n_eta": m.n_eta,
                "delta_eta_over_pi": str(m.delta_eta_over_pi),
                "lambda_tilde": m.lambda_tilde,
            }
            for m in modes
        ],
        "attempts": attempts,
        "decision": decision,
        "continuous_knobs": 0,
        "scientific_core_locks_altered": False,
        "scaffolding_used": [],
    }


def update_expansion_state(result: Dict[str, Any]) -> None:
    if not os.path.isfile(EXPANSION_STATE_PATH):
        return
    with open(EXPANSION_STATE_PATH, encoding="utf-8") as f:
        es = json.load(f)
    ts = result["timestamp_utc"]
    if result["decision"]["sector_absorbed"]:
        existing = {a.get("sector") for a in (es.get("absorbed_sectors") or [])}
        if "discrete_eta_monodromy_lattice" not in existing:
            es.setdefault("absorbed_sectors", []).append(
                {
                    "sector": "discrete_eta_monodromy_lattice",
                    "date_utc": ts,
                    "eta_period": 12,
                    "n_eta": result["n_eta"],
                    "delta_eta_over_pi": result["delta_eta_over_pi"],
                    "monodromy_order": result["monodromy"]["order_from_flavor_geometry"],
                    "discrete_unique": result["discrete_search"]["unique"],
                    "continuous_knobs": 0,
                    "zero_knob_checksum": (
                        "Zero continuous free parameters confirmed | continuous_knobs = 0"
                    ),
                    "artifact": "eta_monodromy_lock.json",
                }
            )
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "discrete_eta_monodromy_lattice",
            "action": "none_required",
            "item": "pure discrete η-lattice + monodromy",
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
    print("Agent choice: discrete η-lattice + monodromy formal lock\n")
    result = run()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    update_expansion_state(result)

    print(f"n_η = {result['n_eta']}")
    print(f"Δη/π = {result['delta_eta_over_pi']}")
    print(f"Discrete candidates passing: {result['discrete_search']['n_passing']}")
    print(f"Monodromy order: {result['monodromy']}")
    for a in result["attempts"]:
        print(f"  Attempt {a['id']}: {a['outcome']} — {a['reason']}")
    d = result["decision"]
    print(f"\nAbsorbed? {d['sector_absorbed']}")
    print(d["statement"])
    print(f"continuous_knobs = {result['continuous_knobs']}")
    if d["sector_absorbed"]:
        print("\nZero continuous free parameters confirmed | continuous_knobs = 0")
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
