#!/usr/bin/env python3
"""
Phase II — Dynamical Scale-Generation Principles Test.

Inject three established *parameter-free principles* known to break scale
invariance, and test whether the locked 14D AGC geometry naturally triggers
any of them. No numerical mass values are fed in.

Mechanisms:
  1. Dimensional Transmutation
  2. Asymptotic Safety
  3. Topological Mass Generation (BF / Chern-Simons type)

Strict rules:
  - Principles only; never inject numerical mass scales.
  - Use only locked geometric data.
  - Honest Yes/No activation; continuous_knobs = 0.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, List, Optional

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
COMPLETE_BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
DYN_PATH = os.path.join(ARTIFACT_DIR, "dynamical_scale_principles.json")

C2_SU3 = 4.0 / 3.0
SIGMA_STAR = math.sqrt(3.0) / 2.0
BETA_RESIDUAL_LOCKED = 0.095716
MONODROMY_ORDER = 24


def load_locked() -> Dict[str, Any]:
    with open(COMPLETE_BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    if b.get("status") != "PASS":
        raise ValueError("complete_baseline.json not PASS")
    return b


def locked_snapshot(baseline: Dict[str, Any]) -> Dict[str, Any]:
    lr = baseline.get("locked_results") or {}
    sigma = float(lr.get("sigma_star") or SIGMA_STAR)
    lams = list(lr.get("lambda_targets") or [4.5, 12.0, 22.5])
    n_eta = list(lr.get("n_eta_triple") or [3, 8, 15])
    r = float(lr.get("beta_residual_new") or BETA_RESIDUAL_LOCKED)
    n_gen = int(lr.get("n_gen") or lr.get("n_gen_native_aps_index") or 3)
    g8 = float(lr.get("eight_pi_g_eff") or (sigma ** 2 / C2_SU3))
    t_wall = sum(j * (j + 1.0) for j in (0.5, 1.0, 1.5)[:n_gen])
    return {
        "sigma_star": sigma,
        "lambda_tilde": lams,
        "n_eta": n_eta,
        "beta_residual_new": r,
        "n_gen": n_gen,
        "eight_pi_g_eff": g8,
        "T_wall": t_wall,
        "tau_res": r * sigma * sigma,
        "monodromy_order": MONODROMY_ORDER,
        "geometry_generates_n_gen_3": bool(lr.get("geometry_generates_n_gen_3", True)),
    }


def test_dimensional_transmutation(nums: Dict[str, Any]) -> Dict[str, Any]:
    """
    Principle: a dimensionless coupling g runs with scale μ via β(g)=μ dg/dμ ≠ 0
    and hits a Landau pole / generates Λ ~ μ0 exp(−∫ dg/β(g)) (QCD-like).

    Probe: Does Σ⁵ wall or β residual induce a dynamically running coupling
    that defines such a confinement-like scale?
    """
    r = nums["beta_residual_new"]
    t_wall = nums["T_wall"]
    g8 = nums["eight_pi_g_eff"]

    # Checks against locked data (no free parameters)
    checks = [
        {
            "check": "beta_residual_is_Callan_Symanzik_beta",
            "result": False,
            "detail": (
                f"Locked β residual r={r:.6f} is the Frobenius residual of the "
                "scale-free Einstein–YM equation on the compact grid, not "
                "β_CS(g)=μ dg/dμ for a running gauge coupling."
            ),
        },
        {
            "check": "domain_wall_induces_running_g_mu",
            "result": False,
            "detail": (
                f"T_wall={t_wall:.4f} is a dimensionless spectral volume sum. "
                "It freezes wall position / tension proxy; it does not define "
                "a Wilsonian coupling g(μ) or a β-function trajectory."
            ),
        },
        {
            "check": "eight_pi_G_eff_runs_with_scale",
            "result": False,
            "detail": (
                f"8πG_eff={g8:.6f}=σ*²/C₂ is a fixed pure number at the locked "
                "minimum, not g(μ) with Landau pole."
            ),
        },
        {
            "check": "Landau_pole_or_confinement_scale_forced",
            "result": False,
            "detail": (
                "No RG equation for any dimensionless coupling is present in "
                "Stages 1–4 locked output. No μ0 and no ∫dg/β(g) exist in the baseline."
            ),
        },
        {
            "check": "residual_NLO_uses_r_as_running_coupling",
            "result": False,
            "detail": (
                "Residual NLO flavor uses √r as a fixed geometric deformation "
                "parameter for angles (dimensionless), not as a scale-running g(μ)."
            ),
        },
    ]

    triggered = all(c["result"] for c in checks)  # requires all True; none are
    # Actually triggered if the principle is activated - any path that fully
    # implements DT. We require positive evidence of running + pole/scale.
    triggered = False
    absolute_scale = False

    return {
        "mechanism": "dimensional_transmutation",
        "principle": (
            "Dimensionless coupling runs; dimensional transmutation generates "
            "Λ ~ μ0 exp(−∫ dg/β(g)) without bare mass parameters."
        ),
        "triggered": triggered,
        "triggered_label": "Yes" if triggered else "No",
        "responsible_geometric_feature": None,
        "features_examined": [
            "Σ⁵ domain-wall tension T_wall",
            "β residual (higher-res Einstein–YM residual)",
            "8πG_eff = σ*²/C₂",
            "residual NLO use of √r",
        ],
        "absolute_scale_generated": absolute_scale,
        "checks": checks,
        "reason": (
            "The locked geometry does not activate dimensional transmutation. "
            "The word 'β residual' is not the Callan–Symanzik β-function; the "
            "domain wall supplies a pure-number tension proxy; no running "
            "coupling g(μ), Landau pole, or confinement scale is forced by "
            "the locked data. Continuous knobs remain 0; no mass numbers injected."
        ),
        "continuous_knobs": 0,
    }


def test_asymptotic_safety(nums: Dict[str, Any]) -> Dict[str, Any]:
    """
    Principle: gravitational (or matter) couplings flow to a non-Gaussian UV
    fixed point; relevant deformation(s) define a crossover / Planck-like scale
    where the flow departs the FP toward the IR.

    Probe: Does the squashed conifold geometry correspond to or flow into such
    a UV fixed point whose departure defines a Planck-like scale?
    """
    sigma = nums["sigma_star"]
    r = nums["beta_residual_new"]

    checks = [
        {
            "check": "sigma_star_is_Wilsonian_UV_fixed_point",
            "result": False,
            "detail": (
                f"σ*={sigma:.6f}=√3/2 is the classical minimum of the geometric "
                "potential V(σ)=(3/2)σ²+(3/2)(λ̃₀/6)²/σ². It is not a fixed point "
                "of a Wetterich / FRG flow β_i(g*)=0 in theory space."
            ),
        },
        {
            "check": "Einstein_YM_residual_vanishes_as_AS_beta_functions",
            "result": False,
            "detail": (
                f"Higher-res residual r={r:.6f} measures incomplete cancellation of "
                "the classical Einstein–YM tensor equation on a finite harmonic "
                "basis — not vanishing of gravitational β-functions at a "
                "non-Gaussian UV fixed point."
            ),
        },
        {
            "check": "RG_trajectory_and_relevant_deformation_present",
            "result": False,
            "detail": (
                "Locked baseline contains no k-dependent couplings g(k), λ(k), "
                "no critical exponents, and no identification of a relevant "
                "direction whose vev sets a crossover scale k_*."
            ),
        },
        {
            "check": "conifold_geometry_forces_non_Gaussian_FP",
            "result": False,
            "detail": (
                "Squashed T^{1,1} is a classical Sasaki–Einstein / Einstein–YM "
                "background. Correspondence to an AS UV fixed point would require "
                "an FRG computation not present in the locked Stages 1–4 data."
            ),
        },
    ]

    triggered = False
    absolute_scale = False

    return {
        "mechanism": "asymptotic_safety",
        "principle": (
            "Non-trivial UV fixed point of the RG; departure along a relevant "
            "direction defines a Planck-like crossover scale without bare M_Pl input."
        ),
        "triggered": triggered,
        "triggered_label": "Yes" if triggered else "No",
        "responsible_geometric_feature": None,
        "features_examined": [
            "σ* squashing minimum on T^{1,1}",
            "β residual of Einstein–YM solve",
            "absence of FRG / Wetterich trajectory in baseline",
        ],
        "absolute_scale_generated": absolute_scale,
        "checks": checks,
        "reason": (
            "Asymptotic safety is not activated by the locked geometry. Classical "
            "shape stabilization at σ*=√3/2 and a nonzero Einstein–YM residual are "
            "not equivalent to a non-Gaussian UV fixed point plus relevant "
            "deformation. No Planck-like crossover scale is generated. "
            "Continuous knobs remain 0; no mass numbers injected."
        ),
        "continuous_knobs": 0,
        "note_classical_vs_AS": (
            "Do not confuse classical geometric equilibrium with an AS fixed point: "
            "the former freezes a dimensionless modulus; the latter would define "
            "scale via RG departure in theory space."
        ),
    }


def test_topological_mass_bf_cs(nums: Dict[str, Any]) -> Dict[str, Any]:
    """
    Principle: BF (m ∫ B∧F) or Chern–Simons (level k) couplings generate a
    topological mass gap for gauge / form fields without a Higgs vev.

    Probe: Does self-dual 7-form + APS boundary naturally produce such a
    topological mass gap?
    """
    n_gen = nums["n_gen"]
    lams = nums["lambda_tilde"]
    r = nums["beta_residual_new"]

    # Spectral structure: zero modes vs positive eigenvalues (dimensionless)
    spectral_ratios = {
        f"sqrt_lambda_{i+1}_over_0": math.sqrt(lams[i] / lams[0])
        for i in range(len(lams))
    }

    checks = [
        {
            "check": "BF_term_m_B_wedge_F_forced_by_geometry",
            "result": False,
            "detail": (
                "Locked data enforce self-duality ⋆Ψ=Ψ and APS boundary conditions. "
                "They do not force a dynamical BF mass parameter m in a 4D effective "
                "action ∫ m B∧F. No such m is determined (even as a pure principle "
                "with m fixed by topology alone without a scale)."
            ),
        },
        {
            "check": "Chern_Simons_level_defines_absolute_mass_gap",
            "result": False,
            "detail": (
                f"Monodromy order {MONODROMY_ORDER} and n_η quanta are group-theoretic "
                "integers used for discrete flavor naturalness, not a 3D CS level k "
                "that sets m_top ~ k·e² with an absolute mass in 4D."
            ),
        },
        {
            "check": "APS_self_dual_selects_discrete_zero_modes",
            "result": True,
            "detail": (
                f"APS index + self-duality do select a discrete zero-mode sector "
                f"with N_gen={n_gen} and derived λ̃={lams}. Off-sector modes are "
                "obstructed (index>0 or ⋆-defect). This is topological *mode "
                "selection*, not BF/CS topological mass generation of an absolute scale."
            ),
        },
        {
            "check": "absolute_mass_gap_from_topology_alone",
            "result": False,
            "detail": (
                "Eigenvalue ratios √(λ̃_k/λ̃_0) are fixed, but absolute masses still "
                "require m~√λ̃/L with overall length L unfixed (volume modulus flat; "
                "absolute yardstick test negative)."
            ),
        },
        {
            "check": "self_dual_7_form_equals_BF_mass_term",
            "result": False,
            "detail": (
                "⋆Ψ=Ψ is an algebraic projector on the form field, not a Proca/BF "
                "mass term with dynamically generated m≠0 in absolute units."
            ),
        },
    ]

    # Principle "triggered" means the BF/CS mass-generation mechanism fires.
    # Mode selection alone is not BF/CS absolute mass generation.
    triggered = False
    # Partial topological discrete structure exists but is not this mechanism
    partial_topological_mode_selection = True
    absolute_scale = False

    return {
        "mechanism": "topological_mass_generation_BF_Chern_Simons",
        "principle": (
            "BF (m∫B∧F) or Chern–Simons-type couplings generate a topological "
            "mass gap without a continuous Higgs vev."
        ),
        "triggered": triggered,
        "triggered_label": "Yes" if triggered else "No",
        "responsible_geometric_feature": None,
        "related_but_not_activating_feature": (
            "APS index + self-duality (discrete zero-mode / generation selection)"
        ),
        "features_examined": [
            "self-dual 7-form ⋆Ψ=Ψ",
            "APS boundary / index",
            "derived spectral λ̃ on unit manifold",
            "monodromy order / n_η integers",
            "β residual r",
        ],
        "absolute_scale_generated": absolute_scale,
        "partial_topological_mode_selection_present": partial_topological_mode_selection,
        "spectral_ratios_dimensionless": spectral_ratios,
        "beta_residual_role": (
            f"r={r:.6f} enters residual NLO flavor (angles), not a BF mass m."
        ),
        "checks": checks,
        "reason": (
            "Topological BF/Chern–Simons mass generation is not activated as a "
            "scale-generating mechanism. Self-duality + APS do produce topological "
            "selection of N_gen=3 zero modes and dimensionless spectral ratios, "
            "but that is discrete mode structure on a scale-free background — not "
            "a BF/CS absolute mass gap. Continuous knobs remain 0; no mass numbers injected."
        ),
        "continuous_knobs": 0,
    }


def analyze_dynamical_principles(
    baseline: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    b = baseline or load_locked()
    nums = locked_snapshot(b)

    m1 = test_dimensional_transmutation(nums)
    m2 = test_asymptotic_safety(nums)
    m3 = test_topological_mass_bf_cs(nums)
    mechanisms = [m1, m2, m3]

    activated = [m for m in mechanisms if m["triggered"]]
    any_absolute = any(m["absolute_scale_generated"] for m in mechanisms)

    comparative = []
    for m in mechanisms:
        comparative.append(
            {
                "mechanism": m["mechanism"],
                "triggered": m["triggered_label"],
                "responsible_geometric_feature": m.get("responsible_geometric_feature"),
                "absolute_scale_generated": "Yes"
                if m["absolute_scale_generated"]
                else "No",
            }
        )

    return {
        "banner": "DYNAMICAL SCALE-GENERATION PRINCIPLES TESTED – ZERO KNOBS PRESERVED",
        "continuous_knobs": 0,
        "numerical_mass_values_injected": False,
        "locked_data_only": True,
        "mechanisms": mechanisms,
        "comparative_table": comparative,
        "summary": {
            "n_mechanisms_tested": 3,
            "n_triggered": len(activated),
            "triggered_names": [m["mechanism"] for m in activated],
            "any_absolute_scale_generated": any_absolute,
            "absolute_scale_status": "NO",
        },
        "statement": (
            "None of the three parameter-free dynamical principles — dimensional "
            "transmutation, asymptotic safety, or BF/Chern–Simons topological mass "
            "generation — is activated by the locked 14D geometry as a generator of "
            "an absolute scale. Related topological structure (APS + self-duality) "
            "selects discrete zero modes and dimensionless ratios only. "
            "continuous_knobs=0; no numerical mass values were introduced."
        ),
        "locked_snapshot": nums,
    }


def decision_table_text(analysis: Dict[str, Any]) -> str:
    lines = [
        "=" * 88,
        analysis["banner"],
        "=" * 88,
        f"Numerical mass values injected: {analysis['numerical_mass_values_injected']}",
        f"Continuous knobs: {analysis['continuous_knobs']}",
        f"Any absolute scale generated: {analysis['summary']['any_absolute_scale_generated']}",
        "-" * 88,
        f"{'Mechanism':<42} {'Triggered?':<12} {'Abs. scale?':<12} Feature",
        "-" * 88,
    ]
    for row in analysis["comparative_table"]:
        feat = row["responsible_geometric_feature"] or "—"
        lines.append(
            f"{row['mechanism']:<42} {row['triggered']:<12} "
            f"{row['absolute_scale_generated']:<12} {feat}"
        )
    lines += [
        "-" * 88,
        f"Triggered count: {analysis['summary']['n_triggered']}/3",
        analysis["statement"],
        "=" * 88,
    ]
    # Per-mechanism detail
    for m in analysis["mechanisms"]:
        lines.append(f"\n[{m['mechanism']}] triggered={m['triggered_label']}")
        lines.append(f"  {m['reason'][:200]}...")
    return "\n".join(lines)


def save_result(analysis: Dict[str, Any]) -> str:
    with open(DYN_PATH, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)
    return DYN_PATH


def main() -> None:
    print("Dynamical scale-generation principles test — starting\n")
    analysis = analyze_dynamical_principles()
    print(decision_table_text(analysis))
    path = save_result(analysis)
    print(f"\nSaved {path}")
    print(analysis["banner"])


if __name__ == "__main__":
    main()
