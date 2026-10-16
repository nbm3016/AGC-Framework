#!/usr/bin/env python3
"""
Expansion Mode controlled probe: monodromy Dehn-twist scale quantization.

Question: Do locked monodromy data (order-24 cyclotomic structure, Δη/π set,
n_η, APS self-dual survivors) force the continuous residual scale family
λ ∈ ℝ⁺ down to a discrete arithmetic set?

Rules:
  - Only locked monodromy / domain-wall / self-dual data
  - No new free integers, free phases, or continuous coefficients
  - Do not force a lock; report unique discrete set OR residual freedom
  - continuous_knobs remain 0
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from fractions import Fraction
from math import gcd, lcm
from typing import Any, Dict, List, Tuple

import numpy as np

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "monodromy_dehn_scale_probe.json")
EXPANSION_STATE_PATH = os.path.join(ARTIFACT_DIR, "expansion_state.json")

PI = math.pi
TWO_PI = 2.0 * PI


def load_locked() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    if b.get("status") != "PASS":
        raise ValueError("baseline not PASS")
    return b


def locked_monodromy_data(b: Dict[str, Any]) -> Dict[str, Any]:
    lr = b["locked_results"]
    n_eta = [int(x) for x in (lr.get("n_eta_triple") or [3, 8, 15])]
    # Δη_g = n_g * π / 12  (η-period 12 locked)
    period = 12
    delta_eta = [n * PI / period for n in n_eta]
    delta_over_pi = [Fraction(n, period) for n in n_eta]
    # Phase factors on U(1): exp(i Δη)
    phases = [complex(math.cos(d), math.sin(d)) for d in delta_eta]
    # Order of each phase: smallest k>0 with k*Δη ∈ 2πℤ
    orders = []
    for n in n_eta:
        # k * n * π/12 = 2π m  ⇒  kn/24 = m  ⇒ kn ≡ 0 (mod 24)
        for k in range(1, 49):
            if (k * n) % 24 == 0:
                orders.append(k)
                break
    mono = orders[0]
    for o in orders[1:]:
        mono = math.lcm(mono, o)
    return {
        "n_eta": n_eta,
        "eta_period": period,
        "delta_eta": delta_eta,
        "delta_eta_over_pi": [str(f) for f in delta_over_pi],
        "phase_orders": orders,
        "cyclotomic_monodromy_order": mono,
        "survivors_j1": [0.5, 1.0, 1.5],
        "self_dual": "j2=0",
        "n_gen": int(lr.get("n_gen") or 3),
        "sigma_star": float(lr.get("sigma_star") or math.sqrt(3) / 2),
        "lambda_tilde": list(lr.get("lambda_targets") or [4.5, 12.0, 22.5]),
        "T_wall": sum(j * (j + 1.0) for j in (0.5, 1.0, 1.5)),
    }


def monodromy_matrices(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map locked Δη monodromy to U(1) / Dehn-type actions on fiber cycles.

    On each generation sector g, holonomy around the η-circle / fiber is
      U_g = exp(i Δη_g) ∈ U(1),
    with U_g^{ord_g} = 1. These are isometries of the unit T^{1,1}-type fiber,
    not free SL(2,ℤ) matrices with free integer entries.

    Dehn-twist analogy: on a circle factor S¹_η, a rotation by 2π·(n/24) is
    the unique isometry in the cyclic group of order 24 compatible with the
    locked Δη lattice (period-12 η modular structure with monodromy order 24).
    """
    n_eta = data["n_eta"]
    period = data["eta_period"]  # 12
    mono = data["cyclotomic_monodromy_order"]  # 24
    # Rotation angles in units of 2π: θ/(2π) = Δη/(2π) = n/24
    rotations_mod_1 = [Fraction(n, 2 * period) for n in n_eta]  # n/24
    # As integer powers of primitive 24th root of unity ζ = exp(2π i / 24)
    zeta_powers = [int(n) for n in n_eta]  # ζ^{n} with ζ^{24}=1; Δη = 2π n/24
    # Check consistency: Δη = n*π/12 = 2π n/24
    return {
        "description": (
            "Monodromy acts as simultaneous U(1) rotations by 2π·(n_g/24) on "
            "fiber/η-circles of the three APS survivors; group cyclic of order 24."
        ),
        "primitive_root_order": mono,
        "zeta_powers_n_g": zeta_powers,
        "rotations_as_fraction_of_2pi": [str(f) for f in rotations_mod_1],
        "mapping_torus_construction": (
            "Mapping torus M_f = (Y × [0,1]) / ~ with (y,0)~(f(y),1), where f is "
            "the fiber isometry implementing the product of U(1) rotations. "
            "f^{24} = id on the unit-geometry fiber (order divides 24)."
        ),
        "is_isometry_of_unit_metric": True,
        "free_SL2Z_integers_introduced": False,
    }


def scale_weight_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Under overall metric rescaling g → λ² ĝ (λ ∈ ℝ⁺ = residual scale family):

      - lengths ∝ λ
      - k-form periods ∫_γ α ∝ λ^{deg} if α is metric-normalized volume form pieces;
        for a flat U(1) connection A, holonomy ∮ A is scale-invariant
      - Hodge star * on p-forms in d dimensions: * : Ω^p → Ω^{d-p}
        conformal weight: *_{λ²g} = λ^{d-2p} *_{g}  (on the form components)

    Critical: middle-degree forms (p = d/2) have d-2p = 0 ⇒ * is
    conformal-invariant. AGC self-dual 7-form lives in d=14, p=7 = d/2
    ⇒ self-duality ⋆Ψ=Ψ is scale-invariant.

    Fiber U(1) holonomies exp(i Δη) are pure gauge data on the η-lattice —
    already discrete and scale-invariant.
    """
    d_bulk = 14
    p_form = 7  # self-dual 7-form
    conf_weight_star = d_bulk - 2 * p_form  # 0
    return {
        "scale_family": "λ ∈ ℝ⁺ (overall conformal factor / volume radius unit)",
        "holonomy_scale_weight": 0,
        "holonomy_constraint": (
            "Locked monodromy only constrains scale-invariant holonomies "
            "exp(i Δη_g)=ζ^{n_g}. No condition on λ."
        ),
        "self_dual_7form": {
            "dimension_d": d_bulk,
            "form_degree_p": p_form,
            "star_conformal_weight_d_minus_2p": conf_weight_star,
            "self_duality_scale_invariant": conf_weight_star == 0,
            "implication": (
                "⋆Ψ=Ψ is unchanged under g→λ²ĝ. Monodromy of self-dual periods "
                "cannot quantize λ via self-duality matching."
            ),
        },
        "spectral_eigenvalues": {
            "code_lambda_tilde": data["lambda_tilde"],
            "physical_scaling": "λ_phys = λ_tilde / R² with R∝λ",
            "monodromy_action_on_spectrum": (
                "Fiber isometries preserve the spectrum of the unit metric; "
                "they do not select a preferred R."
            ),
        },
        "shape_modulus_sigma": {
            "sigma_star": data["sigma_star"],
            "note": (
                "σ* is already frozen by V(σ); monodromy does not further "
                "discretize overall volume once shape is fixed."
            ),
        },
    }


def mapping_torus_smoothness(data: Dict[str, Any], mono: Dict[str, Any]) -> Dict[str, Any]:
    """
    Smoothness of the mapping torus for a finite-order isometry f of a compact
    Riemannian manifold (Y,g) requires only that f be a smooth isometry (or
    diffeomorphism) of Y — not that a continuous scale parameter of g be discrete.

    Here f^{24}=id acts as fiber rotations of the unit geometry. Extending g → λ²ĝ
    with the same angular isometry f still gives a smooth mapping torus for every λ>0.
    """
    return {
        "finite_order": mono["primitive_root_order"],
        "f_power_equals_id": True,
        "smooth_mapping_torus_for_all_positive_lambda": True,
        "reason": (
            "f is an isometry of every overall rescaling of the metric that preserves "
            "the unit angular/fiber geometry (Dehn-type rotation angles fixed). "
            "Smoothness of M_f therefore holds for the entire continuous family λ∈ℝ⁺."
        ),
        "no_new_integers_required": True,
    }


def period_matching_test(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suppose periods of a scale-weighted form Π(λ) = λ^w Π̂ transform under
    monodromy M as Π ↦ M Π. Smoothness/identification across the monodromy
    cut requires M Π ~ Π in the projectivized period domain for geometric
    moduli — but for overall scale, Π and MΠ share the same |scale| weight,
    so the condition is homogeneous in λ and never isolates a unique λ>0.

    Explicit model using only locked data:
      Π_g(λ) = λ^{w} · exp(i Δη_g) · v_g
    with v_g built from locked survivor volumes (pure numbers).
    Monodromy multiplies phases by ζ^{n_g}; |Π_g| ∝ λ^w for all monodromy images.
    """
    n_eta = data["n_eta"]
    vols = [j * (j + 1.0) for j in data["survivors_j1"]]
    # Sample λ continuum; check monodromy only rotates phases
    lambdas = np.array([0.1, 0.5, 1.0, 2.0, 10.0])
    w = 1.0  # arbitrary common weight — result independent of w
    residuals = []
    for lam in lambdas:
        mags = []
        for n, vol in zip(n_eta, vols):
            phase = 2.0 * PI * n / 24.0
            Pi = (lam**w) * vol * complex(math.cos(phase), math.sin(phase))
            # monodromy: multiply by ζ^n again (one Dehn step)
            dphase = 2.0 * PI * n / 24.0
            Pi_m = Pi * complex(math.cos(dphase), math.sin(dphase))
            mags.append((abs(Pi), abs(Pi_m)))
        # magnitudes identical under monodromy
        ok = all(abs(a - b) < 1e-12 for a, b in mags)
        residuals.append({"lambda": float(lam), "magnitudes_preserved": ok})

    return {
        "model": "Π_g(λ)=λ^w · Vol_g · exp(i Δη_g)",
        "weight_w_common": w,
        "monodromy_preserves_magnitude_for_all_lambda": all(
            r["magnitudes_preserved"] for r in residuals
        ),
        "samples": residuals,
        "implication": (
            "Period matching under monodromy is homogeneous in λ and is satisfied "
            "for every λ>0. No discrete arithmetic subset of ℝ⁺ is selected."
        ),
    }


def arithmetic_candidates_from_monodromy_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pure numbers naturally associated to monodromy (NOT forced as values of λ):
      {1, 2, 3, 8, 12, 15, 24, 26, ...} from n_η, period, order, sums.
    These label discrete structure already locked; elevating any of them to
    'the' value of overall scale λ would be an arbitrary unit choice, not a
    monodromy obstruction.
    """
    n_eta = data["n_eta"]
    arithmetic_set = sorted(
        {
            1,
            data["eta_period"],
            data["cyclotomic_monodromy_order"],
            *n_eta,
            sum(n_eta),
            n_eta[2] - n_eta[0],
            data["n_gen"],
        }
    )
    return {
        "discrete_integers_already_locked": arithmetic_set,
        "forced_as_value_of_overall_scale_lambda": False,
        "reason": (
            "These integers classify holonomy/η-lattice data. Identifying λ with "
            "any of them would assign a pure number to a dimensionful (or "
            "conformal-factor) quantity without a monodromy obstruction forcing it."
        ),
    }


def run_probe() -> Dict[str, Any]:
    b = load_locked()
    data = locked_monodromy_data(b)
    mono = monodromy_matrices(data)
    scale = scale_weight_analysis(data)
    mt = mapping_torus_smoothness(data, mono)
    periods = period_matching_test(data)
    arith = arithmetic_candidates_from_monodromy_only(data)

    # Decision
    success_unique_discrete_scale = False
    # Residual freedom: overall conformal / volume scale
    residual_family = {
        "parameter": "λ ∈ ℝ⁺",
        "meaning": (
            "Overall conformal factor of the internal metric (volume radius R ∝ λ "
            "with shape σ* held fixed at √3/2)"
        ),
        "constrained_by_monodromy": False,
        "constrained_by_self_duality": False,
        "constrained_by_mapping_torus_smoothness": False,
        "constrained_by_period_matching": False,
        "explicit_residual_freedom": "λ ∈ ℝ^{+} unrestricted by locked monodromy/Dehn data",
    }

    decision = {
        "discrete_scale_lock_achieved": success_unique_discrete_scale,
        "unique_positive_pure_number_for_lambda": None,
        "unique_arithmetic_set_for_lambda": None,
        "verdict": "NEGATIVE",
        "summary": (
            "Locked monodromy maps to a cyclic order-24 U(1)/Dehn action on fiber "
            "cycles. Holonomies and middle-degree self-duality are scale-invariant; "
            "mapping-torus smoothness and period matching hold for every λ>0. "
            "Therefore monodromy constrains shape/fiber holonomy only and leaves "
            "the overall scale family λ∈ℝ⁺ continuous. No discrete arithmetic "
            "quantization of overall scale is forced."
        ),
        "residual_continuous_family": residual_family,
        "continuous_knobs": 0,
        "lock_forced": False,
    }

    return {
        "banner": "AGC Expansion Mode Active — monodromy Dehn-twist scale quantization probe",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "locked_inputs_used": data,
        "monodromy_as_dehn_twist": mono,
        "scale_weight_analysis": scale,
        "mapping_torus_smoothness": mt,
        "period_matching_test": periods,
        "arithmetic_integers_not_scale": arith,
        "decision": decision,
        "scientific_core_locks_altered": False,
        "scaffolding_retained": False,
    }


def update_state(result: Dict[str, Any]) -> None:
    if not os.path.isfile(EXPANSION_STATE_PATH):
        return
    with open(EXPANSION_STATE_PATH, encoding="utf-8") as f:
        es = json.load(f)
    ts = result["timestamp_utc"]
    es.setdefault("depth_probes", []).append(
        {
            "probe": "monodromy_dehn_twist_scale_quantization",
            "timestamp_utc": ts,
            "verdict": result["decision"]["verdict"],
            "discrete_scale_lock_achieved": result["decision"][
                "discrete_scale_lock_achieved"
            ],
            "residual_freedom": result["decision"]["residual_continuous_family"][
                "explicit_residual_freedom"
            ],
            "artifact": "monodromy_dehn_scale_probe.json",
            "continuous_knobs": 0,
        }
    )
    # Strengthen yardstick / volume parked notes
    for p in es.get("parked_bottlenecks") or []:
        sid = p.get("sector_id") or ""
        if "yardstick" in sid or "volume" in sid or "absolute" in sid.lower():
            p["monodromy_dehn_probe"] = {
                "verdict": "negative",
                "note": (
                    "Order-24 monodromy/Dehn action does not discretize overall scale; "
                    "λ∈ℝ⁺ remains free."
                ),
            }
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "monodromy_dehn_scale_probe",
            "action": "probe_only_no_lock",
            "item": "Dehn-twist scale quantization test",
            "status": "negative",
            "timestamp_utc": ts,
        }
    )
    es["last_updated"] = ts
    es["continuous_knobs"] = 0
    with open(EXPANSION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(es, f, indent=2)
        f.write("\n")


def main() -> None:
    print("AGC Expansion Mode Active")
    print("Controlled probe: monodromy Dehn-twist scale quantization\n")
    result = run_probe()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    update_state(result)

    d = result["decision"]
    print("=" * 72)
    print("MONODROMY → DEHN / MAPPING-TORUS")
    print("=" * 72)
    print(result["monodromy_as_dehn_twist"]["description"])
    print(f"  Order: {result['monodromy_as_dehn_twist']['primitive_root_order']}")
    print(
        f"  Rotations (of 2π): "
        f"{result['monodromy_as_dehn_twist']['rotations_as_fraction_of_2pi']}"
    )
    print()
    print("=" * 72)
    print("SCALE WEIGHTS")
    print("=" * 72)
    sd = result["scale_weight_analysis"]["self_dual_7form"]
    print(f"  Holonomy scale weight: 0 (scale-invariant)")
    print(
        f"  Self-dual 7-form * weight d-2p = {sd['star_conformal_weight_d_minus_2p']} "
        f"(scale-invariant: {sd['self_duality_scale_invariant']})"
    )
    print()
    print("=" * 72)
    print("MAPPING TORUS / PERIOD MATCHING")
    print("=" * 72)
    print(
        f"  Smooth for all λ>0: "
        f"{result['mapping_torus_smoothness']['smooth_mapping_torus_for_all_positive_lambda']}"
    )
    print(
        f"  Period |Π| preserved under monodromy for all sample λ: "
        f"{result['period_matching_test']['monodromy_preserves_magnitude_for_all_lambda']}"
    )
    print()
    print("=" * 72)
    print("DECISION")
    print("=" * 72)
    print(f"  Verdict: {d['verdict']}")
    print(f"  Discrete scale lock achieved: {d['discrete_scale_lock_achieved']}")
    print(f"  {d['summary']}")
    print()
    print("  RESIDUAL CONTINUOUS FAMILY:")
    rf = d["residual_continuous_family"]
    print(f"    {rf['explicit_residual_freedom']}")
    print(f"    meaning: {rf['meaning']}")
    print()
    print(f"  continuous_knobs = {d['continuous_knobs']}")
    print(f"  lock_forced = {d['lock_forced']}")
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
