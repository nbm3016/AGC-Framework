#!/usr/bin/env python3
"""
Stage 4 — Heavy Majorana scale test from locked topology only.

Question: Does the locked AGC baseline uniquely determine a heavy
right-handed Majorana mass M_R (or a unique discrete heavy spectrum)?

Strict rules:
  - Use only locked quantities (σ*, λ̃, n_η, Δη, N_gen, β residual, APS, monodromy).
  - No free continuous parameters, no arbitrary intermediate scale, no tunable Yukawa.
  - If M_R is not uniquely forced, do NOT invent one and do NOT run RG.

Conclusion of this analysis (documented in code and output):
  The locked baseline consists of dimensionless spectral/topological data.
  Nothing in Stages 1–3 supplies an absolute energy unit (GeV). Therefore
  no unique heavy Majorana scale in absolute mass units is forced.
  RG of θ₁₃ is not computable without additional external input.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

PI = math.pi
C2_SU3 = 4.0 / 3.0


def analyze_heavy_majorana_from_locked(
    sigma_star: float,
    lambda_targets: Tuple[float, float, float],
    n_eta: Tuple[int, int, int],
    n_gen: int,
    beta_residual_new: float,
    beta_full: float,
    eight_pi_g_eff: float,
    sum_m_nu_eV: float,
    monodromy_order: int = 24,
) -> Dict[str, Any]:
    """
    Exhaustive check of whether locked topology uniquely fixes M_R.

    Candidate constructions are enumerated and each is rejected as
    non-unique if it requires an external unit, a free prefactor, or
    an ambiguous discrete choice not forced by the topology.
    """
    n1, n2, n3 = n_eta
    n_sum = n1 + n2 + n3
    lam0, lam1, lam2 = lambda_targets
    r = beta_residual_new if beta_residual_new > 0 else beta_full

    rejections: List[Dict[str, str]] = []

    # --- Candidate A: seesaw M_R ~ m_D² / m_ν with m_D ~ σ* · v ---
    # Requires electroweak vev v (not locked by Stages 1–3) and Yukawa y.
    rejections.append(
        {
            "candidate": "type_I_seesaw_M_R = m_D^2 / m_nu",
            "status": "rejected_not_unique",
            "reason": (
                "Requires Dirac scale m_D (Yukawa × electroweak vev). "
                "Neither y nor v_EW is fixed by locked σ*, λ̃, n_η, APS, or β residual. "
                "Introducing v_EW would be an external continuous scale."
            ),
        }
    )

    # --- Candidate B: M_R ~ exp(n_sum) · σ*  (dimensionless warp) ---
    warp = math.exp(float(n_sum) * sigma_star / n_gen)  # dimensionless
    rejections.append(
        {
            "candidate": f"M_R / Λ = exp(n_Σ·σ*/N_gen) = {warp:.6e}",
            "status": "rejected_not_unique",
            "reason": (
                "Gives only a dimensionless warp factor. Absolute M_R requires a "
                "reference scale Λ (M_Pl, string scale, GUT scale). No such absolute "
                "scale is present in complete_baseline.json. Choice of Λ is free continuous input."
            ),
            "dimensionless_warp_factor": warp,
        }
    )

    # --- Candidate C: M_R ~ 1/√(8πG_eff)  in geometric units ---
    # eight_pi_g_eff is already dimensionless (σ*²/C₂) in the AGC code units.
    rejections.append(
        {
            "candidate": f"M_R ~ 1/√(8πG_eff) with 8πG_eff={eight_pi_g_eff:.6f}",
            "status": "rejected_not_unique",
            "reason": (
                "In the computational framework, 8πG_eff = σ*²/C₂(3) is dimensionless. "
                "It does not define a mass in GeV without an external unit conversion."
            ),
        }
    )

    # --- Candidate D: discrete spectrum M_k ~ λ̃_k · (something) ---
    rejections.append(
        {
            "candidate": "M_k proportional to λ̃_k or n_η_k",
            "status": "rejected_not_unique",
            "reason": (
                "Relative ratios M_k/M_j = √(λ̃_k/λ̃_j) or n_k/n_j are fixed, but the "
                "overall heavy scale remains free. Topology fixes ratios, not absolute M_R."
            ),
            "relative_ratios_from_lambda": {
                "M2/M1": math.sqrt(lam1 / lam0),
                "M3/M1": math.sqrt(lam2 / lam0),
            },
            "relative_ratios_from_n_eta": {
                "M2/M1": n2 / n1,
                "M3/M1": n3 / n1,
            },
        }
    )

    # --- Candidate E: APS index / eta-invariant scale ---
    rejections.append(
        {
            "candidate": "APS index / η-invariant mass gap",
            "status": "rejected_not_unique",
            "reason": (
                "Locked APS data fix index=0 on survivors and Δη modular period 12. "
                "These constrain discrete mode selection and phase lattice, already used "
                "for N_gen and Δη, not a new absolute Majorana mass."
            ),
        }
    )

    # --- Candidate F: β residual as mass gap ---
    rejections.append(
        {
            "candidate": f"M_R ~ √r or r with r=β_residual_new={r:.6f}",
            "status": "rejected_not_unique",
            "reason": (
                "β residual is a dimensionless Frobenius residual of the Einstein–YM "
                "equation on the compact T^{1,1} grid, not a mass eigenvalue in GeV. "
                "Already used for NLO θ₁₃; does not set heavy Majorana scale."
            ),
        }
    )

    # --- Candidate G: monodromy order 24 as scale ---
    rejections.append(
        {
            "candidate": f"M_R ~ monodromy_order={monodromy_order}",
            "status": "rejected_not_unique",
            "reason": (
                "Monodromy order 24 is a dimensionless group-theoretic integer "
                "(lcm of Δη phase orders). It labels the residual discrete group, "
                "not an energy scale."
            ),
        }
    )

    # --- Candidate H: domain wall tension of Σ⁵ ---
    # Vol-like quantities from survivors are relative (0.75, 2, 3.75).
    rejections.append(
        {
            "candidate": "Σ⁵ domain wall tension ~ Vol(N⁵) or S_eff of survivors",
            "status": "rejected_not_unique",
            "reason": (
                "Survivor volumes Vol(N⁵)=j₁(j₁+1) and S_eff are dimensionless spectral "
                "data already used for Δη = n·π/12. Tension would need a dimensionful "
                "string/Planck prefactor not locked by Stages 1–3."
            ),
        }
    )

    unique = False
    # Light-sector ratios that ARE fixed (report for completeness)
    light_sector_fixed = {
        "sum_m_nu_eV": sum_m_nu_eV,
        "note": (
            "Light-neutrino absolute masses were fixed only after anchoring Δm²_21 "
            "to the PDG reference value (an external spectral anchor for the light "
            "sector). That does not fix the heavy seesaw scale without m_D."
        ),
    }

    return {
        "unique_heavy_majorana_scale_forced": unique,
        "decision": "NO",
        "statement": (
            "The locked topology does not uniquely determine a heavy right-handed "
            "Majorana mass scale M_R (or a unique absolute heavy spectrum). All "
            "candidate constructions either lack an absolute energy unit, require "
            "an external continuous scale (v_EW, M_Pl, Yukawa), or only fix "
            "dimensionless ratios among heavy states."
        ),
        "rg_shift_computed": False,
        "rg_shift_reason": (
            "RG evolution of θ₁₃ from a high scale to low energy requires a "
            "definite high-scale mass M_R (or threshold). Because M_R is not "
            "forced by the locked geometry, no parameter-free RG shift can be "
            "computed without additional input. θ₁₃ remains at the residual-NLO "
            "geometric value."
        ),
        "theta13_remains_deg": None,  # filled by caller with NLO value
        "M_R_GeV": None,
        "heavy_spectrum_GeV": None,
        "candidates_examined": rejections,
        "what_geometry_does_fix": {
            "light_sector": light_sector_fixed,
            "heavy_relative_ratios_if_spectrum_exists": {
                "from_lambda": {
                    "M2/M1": math.sqrt(lam1 / lam0),
                    "M3/M1": math.sqrt(lam2 / lam0),
                },
                "from_n_eta": {"M2/M1": n2 / n1, "M3/M1": n3 / n1},
                "note": (
                    "If a heavy spectrum exists, topology can constrain ratios; "
                    "it does not fix the overall scale."
                ),
            },
            "dimensionless_warps_available": {
                "exp_n_sum_sigma_over_Ngen": warp,
                "eight_pi_g_eff": eight_pi_g_eff,
                "beta_residual_new": r,
                "monodromy_order": monodromy_order,
                "note": "Dimensionless only — need external unit for GeV.",
            },
        },
        "continuous_knobs": 0,
        "external_input_would_be_required_for_RG": [
            "absolute heavy scale M_R (or M_Pl + warp identification)",
            "and/or Dirac Yukawa / electroweak scale for type-I seesaw",
        ],
    }


def majorana_decision_table(analysis: Dict[str, Any], theta13_nlo_deg: float) -> str:
    lines = [
        "=" * 88,
        "HEAVY MAJORANA SCALE TEST — locked topology only",
        "=" * 88,
        f"Unique M_R forced by geometry?  {analysis['decision']}",
        f"Statement: {analysis['statement']}",
        "-" * 88,
        "Candidates examined and rejected:",
    ]
    for c in analysis["candidates_examined"]:
        lines.append(f"  • {c['candidate']}")
        lines.append(f"      → {c['status']}: {c['reason'][:110]}...")
    lines += [
        "-" * 88,
        f"RG shift of θ₁₃ computed?  {analysis['rg_shift_computed']}",
        f"Reason: {analysis['rg_shift_reason']}",
        f"θ₁₃ left at residual-NLO geometric value: {theta13_nlo_deg:.4f}°",
        f"Continuous knobs: {analysis['continuous_knobs']}",
        "=" * 88,
    ]
    return "\n".join(lines)
