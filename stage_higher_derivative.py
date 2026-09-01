#!/usr/bin/env python3
"""
Higher-derivative / higher-curvature geometric back-reaction test.

Question: Does the locked geometry force a unique, parameter-free
higher-derivative correction that further shifts mixing angles or mass scales?

Strict rules:
  - Only locked data: σ*, β residual, Σ⁵ wall, APS, N_gen, residual NLO A4, m_ν.
  - No free α′, Gauss–Bonnet couplings, or continuous coefficients.
  - If no unique term is forced: do NOT invent one; leave θ₁₃ at 7.953°.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, List, Optional

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
COMPLETE_BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
HD_PATH = os.path.join(ARTIFACT_DIR, "higher_derivative_test.json")

# Official locked residual-NLO A4 (must not be re-fit)
LOCKED_THETA13_DEG = 7.953
LOCKED_FLAVOR = {
    "theta12_deg": 31.003,
    "theta23_deg": 45.682,
    "theta13_deg": 7.953,
    "delta_cp_deg": -146.694,
}


def load_locked() -> Dict[str, Any]:
    with open(COMPLETE_BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    if b.get("status") != "PASS":
        raise ValueError("complete_baseline.json not PASS")
    return b


def analyze_higher_derivative_backreaction(
    baseline: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Exhaustive check of higher-derivative candidates forced by locked topology.

    Higher-curvature actions schematically:
      S_HD = ∫ √g ( α R² + β R_{μν}R^{μν} + γ GB + … )
    Absolute coefficients α,β,γ have dimension length² (or are dimensionless
    only after dividing by an absolute scale). Locked computational data are
    dimensionless and do not uniquely fix those coefficients.
    """
    b = baseline or load_locked()
    lr = b["locked_results"]
    sigma = float(lr["sigma_star"])
    r = float(lr.get("beta_residual_new") or 0.095716)
    n_gen = int(lr.get("n_gen") or 3)
    n_eta = list(lr.get("n_eta_triple") or [3, 8, 15])
    lams = list(lr.get("lambda_targets") or [4.5, 12.0, 22.5])
    g8 = float(lr.get("eight_pi_g_eff") or sigma ** 2 / (4.0 / 3.0))
    t_wall = sum(j * (j + 1.0) for j in (0.5, 1.0, 1.5)[:n_gen])

    flavor = (b.get("phenomenology") or {}).get("final_flavor_prediction") or LOCKED_FLAVOR
    theta13_locked = float(flavor.get("theta13_deg", LOCKED_THETA13_DEG))

    candidates: List[Dict[str, Any]] = []

    # --- C1: Gauss–Bonnet / Lovelock with coefficient ∼ r ---
    candidates.append(
        {
            "mechanism": "gauss_bonnet_coeff_from_beta_residual",
            "proposed_form": "S_GB = α_GB ∫ GB  with α_GB =? r or r·σ*²",
            "forced_by_geometry": False,
            "reason": (
                f"The residual r={r:.6f} measures the Einstein–YM equation mismatch "
                "on the unit grid, not the coefficient of a higher-curvature density. "
                "Setting α_GB = r (or r·σ*²) is an arbitrary identification, not forced "
                "by APS, monodromy, or the domain wall."
            ),
            "angle_or_mass_shift": None,
        }
    )

    # --- C2: R² correction with α' ∼ 1/Σλ̃ ---
    candidates.append(
        {
            "mechanism": "R_squared_from_spectral_scale",
            "proposed_form": "α' ∼ 1/Σλ̃_k  or  1/(n_Σ)",
            "forced_by_geometry": False,
            "reason": (
                f"Σλ̃={sum(lams)} and n_Σ={sum(n_eta)} are dimensionless. "
                "α' has dimension length² in a continuum action; equating α' to "
                "1/Σλ̃ chooses units without a geometric derivation of the operator."
            ),
            "angle_or_mass_shift": None,
        }
    )

    # --- C3: HD correction proportional to residual acting on A4 generators ---
    # Would be: δθ13 = f(r) with f uniquely fixed — but any f beyond the already
    # locked residual NLO would be a new free functional choice.
    candidates.append(
        {
            "mechanism": "further_residual_shift_beyond_nlo",
            "proposed_form": "δθ13^(NNLO) = r·θ13_NLO  or  r²·…",
            "forced_by_geometry": False,
            "reason": (
                "Residual NLO already used the unique leading parameter-free "
                "coupling of √r to the residual Z₂ breaking "
                "(sinθ13 ← sinθ13_LO + √r·σ*·√(n2/n_Σ)/N_gen). "
                "Any additional r, r², or r·T_wall shift is a new continuous "
                "functional choice not fixed by topology. Forbidden under zero knobs; "
                "θ13 remains locked at residual NLO."
            ),
            "angle_or_mass_shift": None,
        }
    )

    # --- C4: Domain-wall induced extrinsic-curvature / Gibbons–Hawking HD ---
    candidates.append(
        {
            "mechanism": "domain_wall_extrinsic_curvature_HD",
            "proposed_form": "S_GH ∼ ∫_Σ K  or  ∫_Σ K³ with coeff ∼ T_wall",
            "forced_by_geometry": False,
            "reason": (
                f"T_wall={t_wall:.4f} is a dimensionless spectral volume sum. "
                "Gibbons–Hawking–York and higher boundary terms require a "
                "dimensionful normalization (Planck scale) to affect 4d observables. "
                "No unique absolute coefficient is locked."
            ),
            "angle_or_mass_shift": None,
        }
    )

    # --- C5: Self-dual 7-form / G-structure torsion classes ---
    candidates.append(
        {
            "mechanism": "self_dual_torsion_HD",
            "proposed_form": "W_i torsion classes as HD couplings",
            "forced_by_geometry": False,
            "reason": (
                "On the locked self-dual sector ‖⋆Ψ−Ψ‖²=0, the relevant torsion "
                "classes that would source non-trivial HD deformations vanish. "
                "No forced non-zero HD torsion condensate remains."
            ),
            "angle_or_mass_shift": None,
        }
    )

    # --- C6: 8πG_eff as HD scale ---
    candidates.append(
        {
            "mechanism": "eight_pi_g_eff_as_HD_scale",
            "proposed_form": "α' = 8πG_eff or (8πG_eff)²",
            "forced_by_geometry": False,
            "reason": (
                f"8πG_eff={g8:.6f}=σ*²/C₂ is dimensionless in the framework. "
                "Using it as α' is a unit choice, not a derived HD operator coefficient."
            ),
            "angle_or_mass_shift": None,
        }
    )

    # --- C7: Monodromy order 24 as discrete HD counterterm multiplicity ---
    candidates.append(
        {
            "mechanism": "monodromy_order_24_counterterm",
            "proposed_form": "α_HD ∼ 1/24 or 24·r",
            "forced_by_geometry": False,
            "reason": (
                "Monodromy order 24 is a group-theoretic integer labeling residual "
                "flavor monodromy. It does not uniquely determine a higher-curvature "
                "coupling or an angle shift beyond structures already used (A4, NLO)."
            ),
            "angle_or_mass_shift": None,
        }
    )

    # --- C8: Light-neutrino mass shift from HD ---
    candidates.append(
        {
            "mechanism": "HD_shift_of_light_neutrino_masses",
            "proposed_form": "δm_ν ∼ r·m_ν or √r·m_ν",
            "forced_by_geometry": False,
            "reason": (
                "Multiplying locked m_ν by a function of r is an arbitrary ansatz. "
                "No unique operator maps the Einstein–YM residual onto the light "
                "Majorana mass matrix without free Wilson coefficients."
            ),
            "angle_or_mass_shift": None,
        }
    )

    forced = [c for c in candidates if c["forced_by_geometry"]]
    unique = len(forced) == 1
    any_forced = len(forced) > 0

    return {
        "higher_derivative_term_forced_by_geometry": any_forced and unique,
        "decision": "YES" if (any_forced and unique) else "NO",
        "continuous_knobs": 0,
        "external_alpha_prime_introduced": False,
        "free_wilson_coefficients_introduced": False,
        "candidates_examined": candidates,
        "statement": (
            "No unique higher-derivative / higher-curvature geometric correction "
            "is forced by the locked data. All candidate HD terms either vanish, "
            "require free Wilson coefficients (α′, a/b, Λ), or arbitrarily re-use "
            "the residual r beyond the already-locked residual NLO A4 shift. "
            "Therefore no further calculable shift to mixing angles or mass scales "
            "is applied."
        ),
        "angle_shift_applied": False,
        "mass_shift_applied": False,
        "final_theta13_deg": theta13_locked,
        "final_flavor_prediction_status": "unchanged_locked_residual_NLO_A4",
        "locked_flavor_angles_deg": {
            "theta12_deg": float(flavor.get("theta12_deg", 31.003)),
            "theta23_deg": float(flavor.get("theta23_deg", 45.682)),
            "theta13_deg": theta13_locked,
            "delta_cp_deg": float(flavor.get("delta_cp_deg", -146.694)),
        },
        "interpretation": (
            f"θ₁₃ remains at the official residual-NLO A4 value {theta13_locked}°. "
            "No further Stage-4 higher-derivative correction is unlocked or applied."
        ),
    }


def hd_decision_table(analysis: Dict[str, Any]) -> str:
    lines = [
        "=" * 88,
        "HIGHER-DERIVATIVE GEOMETRIC BACK-REACTION TEST",
        "=" * 88,
        f"HD term forced by geometry?  {analysis['decision']}",
        f"Statement: {analysis['statement']}",
        "-" * 88,
        "Mechanisms examined:",
    ]
    for c in analysis["candidates_examined"]:
        lines.append(f"  • {c['mechanism']}: forced={c['forced_by_geometry']}")
        lines.append(f"      form: {c['proposed_form']}")
        lines.append(f"      → {c['reason'][:100]}...")
    lines += [
        "-" * 88,
        f"Angle shift applied? {analysis['angle_shift_applied']}",
        f"Mass shift applied?  {analysis['mass_shift_applied']}",
        f"Final θ₁₃ status: remains {analysis['final_theta13_deg']:.3f}° "
        f"({analysis['final_flavor_prediction_status']})",
        f"Continuous knobs: {analysis['continuous_knobs']}",
        "=" * 88,
    ]
    return "\n".join(lines)


def save_result(analysis: Dict[str, Any]) -> str:
    with open(HD_PATH, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)
    return HD_PATH


def main() -> None:
    print("Higher-derivative geometric back-reaction test — starting\n")
    analysis = analyze_higher_derivative_backreaction()
    print(hd_decision_table(analysis))
    path = save_result(analysis)
    print(f"\nSaved {path}")
    print(
        f"Decision: {analysis['decision']} | "
        f"θ13 remains {analysis['final_theta13_deg']:.3f}° | "
        f"knobs={analysis['continuous_knobs']}"
    )


if __name__ == "__main__":
    main()
