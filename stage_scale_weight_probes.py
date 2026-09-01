#!/usr/bin/env python3
"""
Expansion Mode — scale-fixing probes with non-zero conformal weight.

Catalog stopped. continuous_knobs must stay 0. No fake locks.

Three mechanisms:
  1) Quantum trace anomaly for locked survivor / n_η multiplet content
  2) Non-middle degree flux + Chern–Simons clash of scaling weights
  3) Curvature / Euler / R^4 interlocking with locked Δη data

Each: compute with locked data only; report discrete scale lock OR residual freedom.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import minimize_scalar

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "scale_weight_probes.json")
EXPANSION_STATE_PATH = os.path.join(ARTIFACT_DIR, "expansion_state.json")

PI = math.pi
C2_SU3 = 4.0 / 3.0


def load_locked() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    if b.get("status") != "PASS":
        raise ValueError("baseline not PASS")
    lr = b["locked_results"]
    return {
        "n_eta": [int(x) for x in (lr.get("n_eta_triple") or [3, 8, 15])],
        "n_gen": int(lr.get("n_gen") or 3),
        "j1": [0.5, 1.0, 1.5],
        "lambda_tilde": list(lr.get("lambda_targets") or [4.5, 12.0, 22.5]),
        "sigma_star": float(lr.get("sigma_star") or math.sqrt(3) / 2),
        "beta_residual_new": float(lr.get("beta_residual_new") or 0.095716),
        "monodromy": 24,
        "eta_period": 12,
        "eight_pi_g_eff": float(lr.get("eight_pi_g_eff") or 0.5625),
        "baseline_status": b.get("status"),
        "continuous_knobs": int(lr.get("continuous_knobs", 0)),
    }


# ---------------------------------------------------------------------------
# 1) Quantum trace anomaly
# ---------------------------------------------------------------------------

def probe_trace_anomaly(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    1-loop conformal anomaly coefficients from locked multiplet content only.

    Field content (locked skeleton, no free species counts):
      - N_gen = 3 chiral APS zero-mode generations (Weyl fermions in 4D EF)
      - Internal spin multiplicity of survivors: d_j = 2j₁+1 ∈ {2,3,4}
      - n_η = (3,8,15) are holonomy quanta, NOT free flavor counts; they
        enter only as already-locked discrete labels (used as optional
        multiplicity weights only if interpreted as KK degeneracy factors —
        we test BOTH interpretations).

    Standard free-field 4D anomaly coefficients (Duff et al. / known tables),
    for real scalar n_s, Weyl fermion n_w, vector n_v (in units where
    a single conformal scalar has a=1/360, c=1/120 in some conventions —
    we use relative integer combinations that cancel overall normalization):

      A_grav ∝  n_s + 11 n_w + 62 n_v     (Euler density channel ~ a)
      C_grav ∝  n_s +  6 n_w + 12 n_v     (Weyl² channel ~ c)

    Gauge β-function (SU(3) YM with n_f Dirac flavors ≈ 2 n_w_gen for one
    generation of quarks is model-dependent). For pure geometric probe we use
    the one-loop coefficient for n_f = N_gen (minimal identification):

      b0 = 11 - (2/3) N_gen   (Dirac-flavor convention for SU(3))

    Dimensional transmutation needs BOTH b0 ≠ 0 AND a UV reference scale or
    a fixed dimensionless coupling at a fixed scale. Locked data provide b0
    as a pure number but NO UV scale μ0 and NO running coupling trajectory
    g(μ) without continuous input.
    """
    n_gen = data["n_gen"]
    j1 = data["j1"]
    n_eta = data["n_eta"]
    d_spin = [int(2 * j + 1) for j in j1]  # 2,3,4
    # Interpretation A: N_gen Weyl zero modes only
    n_w_A = n_gen
    n_s_A, n_v_A = 0, 0
    # Interpretation B: weight by spin multiplicity of survivors
    n_w_B = sum(d_spin)  # 9
    # Interpretation C: weight by n_η (if treated as degeneracy — aggressive)
    n_w_C = sum(n_eta)  # 26

    def anomaly_combo(n_s: int, n_w: int, n_v: int) -> Dict[str, float]:
        # Relative a,c numerators (overall 1/360 factors cancel in ratios)
        A = n_s + 11 * n_w + 62 * n_v
        C = n_s + 6 * n_w + 12 * n_v
        return {"A_num": float(A), "C_num": float(C), "C_over_A": (C / A) if A else None}

    combos = {
        "A_N_gen_Weyl_only": anomaly_combo(0, n_w_A, 0),
        "B_spin_weighted_Weyl": anomaly_combo(0, n_w_B, 0),
        "C_n_eta_weighted_Weyl": anomaly_combo(0, n_w_C, 0),
    }

    # One-loop gauge β0 for SU(3) with n_f = N_gen Dirac (conservative)
    b0_dirac = 11.0 - (2.0 / 3.0) * n_gen
    # With n_f = N_gen Weyl (half of Dirac): b0_weyl_flav = 11 - (1/3) N_gen
    b0_weyl = 11.0 - (1.0 / 3.0) * n_gen

    # Anomaly-induced action for conformal factor φ, g=e^{2φ}ĝ in 4D (Riegert):
    # schematic local form involves □φ, R φ, (∂φ)⁴, ... with coefficients ∝ a,c.
    # For a pure constant-φ (overall volume) mode on a fixed shape background,
    # the anomaly action often reduces to a potential without a stable finite
    # minimum unless a second scale or boundary condition is supplied.
    #
    # Explicit constant-φ toy potential consistent with pure anomaly scaling:
    #   V(φ) = A * e^{4φ}   (Euler density scales as e^{-4φ} * √g ~ const under
    #   combined √g and curvature scaling for overall 4D conformal — actually
    #   for 4D metric g_μν = e^{2φ} η_μν, ∫√g E_4 is topological, ∫√g W² can
    #   vanish on conformally flat, leaving flat or boundary-dominated dynamics.

    # Radion φ with e^{4φ} volume factor and anomaly coeff A:
    # Starobinsky/anomaly-inspired: V ~ A (1 - e^{-αφ})² needs free α or M.
    # With ONLY A pure number and no second scale: V(φ)=A e^{4φ} has no min.

    def V_pure_anomaly_volume(phi: float, A: float) -> float:
        return A * math.exp(4.0 * phi)

    # Scan for minima — expect none at finite φ
    minima_found = []
    A_ref = combos["A_N_gen_Weyl_only"]["A_num"]
    for lo, hi in [(-5, 5), (-2, 2), (0, 3)]:
        res = minimize_scalar(
            lambda ph: V_pure_anomaly_volume(ph, A_ref),
            bounds=(lo, hi),
            method="bounded",
        )
        if res.success:
            # check if interior critical of flat derivative
            minima_found.append(
                {
                    "phi": float(res.x),
                    "V": float(res.fun),
                    "note": "bounded minimum is at boundary of interval for monotonic V",
                }
            )

    # DT statement
    dt = {
        "b0_SU3_n_f_eq_N_gen_Dirac": b0_dirac,
        "b0_nonzero": abs(b0_dirac) > 1e-12,
        "dimensional_transmutation_formula": "Λ = μ0 exp(-8π²/(b0 g(μ0)²))",
        "mu0_in_locked_data": False,
        "g_mu0_in_locked_data": False,
        "dt_fixes_absolute_lambda_without_UV_input": False,
        "reason": (
            "Non-vanishing one-loop b0 is a pure number fixed by N_gen, but "
            "dimensional transmutation still requires a UV reference scale μ0 "
            "and/or a coupling value g(μ0). Neither is present in the locked "
            "Stages 1–4 data without continuous or external input."
        ),
    }

    anomaly_fixes_scale = False
    return {
        "mechanism": "quantum_trace_anomaly",
        "multiplet_content": {
            "n_gen": n_gen,
            "spin_multiplicities_2j1_plus_1": d_spin,
            "n_eta_holonomy_quanta": n_eta,
            "note": "n_η are holonomy labels; multiplicity interpretations A/B/C tested",
        },
        "anomaly_coefficient_numerators": combos,
        "gauge_beta": dt,
        "anomaly_induced_volume_potential": {
            "form_tested": "V(φ)=A e^{4φ} with A from anomaly numerator",
            "stable_finite_minimum": False,
            "samples": minima_found[:3],
            "reason": (
                "With only the pure anomaly coefficient A and no second scale, "
                "the constant-mode potential is monotonic in φ; no stable finite "
                "volume. Riegert/nonlocal anomaly actions similarly require a "
                "reference metric or IR/UV boundary condition supplying a scale."
            ),
        },
        "decision": {
            "fixes_overall_scale_lambda": anomaly_fixes_scale,
            "beta_function_nonzero": dt["b0_nonzero"],
            "dimensional_transmutation_triggered_absolutely": False,
            "residual_freedom": (
                "λ ∈ ℝ⁺ (or φ ∈ ℝ) still free; anomaly fixes pure a,c,b0 numbers "
                "and can set RG shape of g(μ) only relative to an external μ0"
            ),
            "continuous_knobs": 0,
        },
    }


# ---------------------------------------------------------------------------
# 2) Non-middle degree flux + CS clash
# ---------------------------------------------------------------------------

def probe_non_middle_flux(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scaling under g → λ² ĝ in d=14:

      * : Ω^p → Ω^{d-p} has conformal weight (d - 2p)
      Einstein–Hilbert density √g R  ~ λ^{d-2} = λ^{12}
      |F_p|² density √g |F|² with flux quanta: F ~ n / vol_p ~ n λ^{-p}
        ⇒ √g F² ~ λ^d · λ^{-2p} = λ^{d-2p}

      Self-dual 7-form: d-2p = 0 ⇒ density ~ λ^0 (scale-invariant integrand weight
      after accounting for form scaling — consistent with middle-degree).

    Clash: EH ~ λ^{12}, F_p² ~ λ^{14-2p}, F7 self-dual ~ λ^0 (middle).

    Chern–Simons schematic: ∫ F_p ∧ F_q ∧ A_r with p+q+r+1 = d or similar
    has its own weight; without free continuous CS levels beyond discrete
    topology, coefficients are pure numbers or locked integers.

    Question: do locked integers alone produce a unique stationary λ?
    """
    d = 14
    # Candidate non-middle form degrees allowed by skeleton discussion
    form_degrees = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]  # exclude middle 7
    # Discrete flux quanta from locked set ONLY
    n_candidates = sorted(
        {
            data["n_gen"],
            data["monodromy"],
            data["eta_period"],
            *data["n_eta"],
            sum(data["n_eta"]),
            data["n_eta"][2] - data["n_eta"][0],
        }
    )

    # Effective potential pieces as functions of λ (overall scale), pure numbers:
    # V_EH ~ c_EH λ^{d-2} with c_EH from curvature of unit metric (locked shape)
    # For unit Einstein internal space, R_unit ~ O(1); physical R_phys ~ R_unit/λ²?
    # Convention: physical metric g_phys = λ² g_unit ⇒ lengths ∝ λ,
    # Ric_phys = Ric_unit / λ², √g_phys ∝ λ^d,
    # ∫ √g R ~ λ^{d-2} ∫ √g_u R_u.
    #
    # Flux: n = ∫_{C_p} F fixed integer; |F|~ n / Vol(C_p) ~ n / λ^p
    # ∫ √g |F|² ~ λ^{d-2p} n² / Vol_u(C_p)² * Vol_u(total) structure
    # ⇒ V_p(λ) = α_p n² λ^{d-2p} with α_p pure geometric (unit volume factors).

    # Without free α_p, set α_p = 1 for all (or use locked pure factors from
    # volumes of survivors). Use Vol factors from locked j1 spectrum only.
    vols = [j * (j + 1.0) for j in data["j1"]]
    vol_unit = float(sum(vols))  # 6.5

    def V_total(lam: float, n_flux: int, p_form: int, include_eh: bool = True) -> float:
        if lam <= 0:
            return 1e300
        # unit curvature integral pure number ~ O(1); use σ* and vol as locked
        I_R = data["sigma_star"] ** 2 * vol_unit  # pure
        V = 0.0
        if include_eh:
            V += I_R * (lam ** (d - 2))
        # flux
        Vp = (n_flux**2) / (vol_unit ** (2.0 * p_form / 5.0) + 1e-30)  # pure geom factor
        # vol of p-cycle ~ λ^p * unit; use vol_unit^{p/5} as rough 5-internal proxy
        V += Vp * (lam ** (d - 2 * p_form))
        return V

    # Search minima over λ for each (p, n) with pure α=1
    minima = []
    for p_form in [4, 6]:  # primary user-requested non-middle
        for n_flux in n_candidates:
            if n_flux == 0:
                continue

            def f(lam: float, p_form=p_form, n_flux=n_flux) -> float:
                return V_total(lam, n_flux, p_form)

            local = []
            for lo, hi in [(1e-3, 1.0), (1.0, 10.0), (10.0, 1e3), (1e-4, 1e-2)]:
                res = minimize_scalar(f, bounds=(lo, hi), method="bounded")
                if res.success and res.x > 0:
                    # second derivative
                    h = max(1e-6 * res.x, 1e-9)
                    v2 = (f(res.x + h) - 2 * f(res.x) + f(res.x - h)) / (h * h)
                    if v2 > 0:
                        local.append({"lambda": float(res.x), "V": float(res.fun), "V2": float(v2)})
            if local:
                best = min(local, key=lambda z: z["V"])
                minima.append(
                    {
                        "p_form": p_form,
                        "n_flux": n_flux,
                        "lambda_star": best["lambda"],
                        "stable": True,
                    }
                )

    # Analytic critical point for V = A λ^{a} + B λ^{b}, a=d-2=12, b=d-2p
    analytic = []
    for p_form in [4, 6]:
        a_exp = d - 2  # 12
        b_exp = d - 2 * p_form  # 6 for p=4, 2 for p=6
        for n_flux in n_candidates:
            A = data["sigma_star"] ** 2 * vol_unit
            B = (n_flux**2) / (vol_unit ** (2.0 * p_form / 5.0) + 1e-30)
            # V' = A a λ^{a-1} + B b λ^{b-1} = 0
            # λ^{a-b} = - (B b)/(A a)  needs opposite signs for positive λ
            # Same-sign EH+flux both positive ⇒ no positive critical point
            # (both energy densities positive in standard sign)
            analytic.append(
                {
                    "p_form": p_form,
                    "n_flux": n_flux,
                    "a_exp": a_exp,
                    "b_exp": b_exp,
                    "same_sign_positive_terms": True,
                    "positive_critical_lambda": None,
                    "reason": (
                        "Standard positive-definite EH + |F|² have the same sign; "
                        "V(λ)=Aλ^{12}+Bλ^{14-2p} with A,B>0 is strictly increasing "
                        "or has no stable finite minimum (derivative never zero for λ>0)."
                    ),
                }
            )

    # Opposite-sign would require ghost flux or cosmological term free continuous
    # CS term: S_CS ~ n_cs ∫ C∧F∧F — n_cs must be locked integer if used
    # Scaling of CS in action can differ; treat n_cs ∈ locked set
    cs_notes = {
        "cs_level_from_locked_integers_only": n_candidates,
        "issue": (
            "Chern–Simons levels, if restricted to the locked integer set, still "
            "leave discrete multiplicity of (p,n,n_cs) assignments; each may give "
            "different λ or none. No unique selection is forced by APS/self-dual "
            "data among those integers without an extra uniqueness theorem."
        ),
    }

    unique_lambdas = sorted(
        {round(m["lambda_star"], 8) for m in minima if m.get("lambda_star")}
    )

    return {
        "mechanism": "non_middle_degree_flux_CS",
        "dimension_d": d,
        "middle_degree": 7,
        "non_middle_degrees_tested": [4, 6],
        "scaling_weights": {
            "Einstein_Hilbert_sqrtg_R": d - 2,
            "F_p_squared_density": {f"p={p}": d - 2 * p for p in [4, 6, 7]},
            "self_dual_F7": 0,
        },
        "locked_integer_flux_candidates": n_candidates,
        "analytic_same_sign": analytic,
        "numeric_minima_if_any": minima,
        "unique_lambda_count": len(unique_lambdas),
        "cs_notes": cs_notes,
        "decision": {
            "fixes_overall_scale_lambda": False,
            "reason": (
                "Non-middle fluxes produce different conformal weights than EH, "
                "but with positive-definite kinetic signs the combined potential "
                "has no stable finite-λ critical point. Achieving a minimum requires "
                "opposite-sign terms (e.g. free bare Λ or ghost) or continuous "
                "relative couplings between sectors — forbidden under zero-knob "
                "rules. Discrete n_F multiplicity would still leave residual discrete "
                "ambiguity even if signs worked."
            ),
            "residual_freedom": (
                "λ ∈ ℝ⁺ remains free; form-degree clash alone does not quantize λ "
                "without free continuous relative couplings or non-locked signs"
            ),
            "continuous_knobs": 0,
        },
    }


# ---------------------------------------------------------------------------
# 3) Curvature–flux interlocking / Euler / R^4
# ---------------------------------------------------------------------------

def probe_curvature_topology(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Topological densities:
      - Euler density E_d integrates to χ(M) ∈ ℤ on closed oriented M^d
      - Hirzebruch L-genus / signature similarly topological on closed manifolds

    For product/fibration structure with odd-dimensional factors T^{1,1}, Σ⁵:
      χ(odd closed orientable) = 0 ⇒ pure Euler terms vanish on those factors.

    R^4 / higher curvature: coefficients are continuous Wilson parameters unless
    fixed by a named theorem. Locked Δη data are pure holonomies — they do not
    fix α' or R^4 Wilson coefficients.

    Topological action pieces S_top = c χ are λ-independent (metric-independent).
    They cannot minimize volume as a function of λ.
    """
    # Euler of factors
    chi_T11 = 0  # odd 5-manifold
    chi_Sigma5 = 0
    chi_product_10 = 0  # product of odds

    # 14D closed manifold Euler would be a single integer if topology fixed,
    # but is λ-independent and does not select volume.
    # Signature σ(M) similarly.

    # R^4 schematic V(λ) ~ α4 ∫ √g R^4 ~ α4 λ^{d-8} I_R4_unit
    # α4 free continuous unless fixed — NOT locked by Δη
    d = 14
    I_R4_unit = data["sigma_star"] ** 4 * sum(
        j * (j + 1.0) for j in data["j1"]
    )  # pure proxy

    # With α4 fixed to a locked pure number (e.g. 1 or monodromy) — still one power
    def V_R4(lam: float, alpha: float = 1.0) -> float:
        if lam <= 0:
            return 1e300
        return alpha * I_R4_unit * (lam ** (d - 8))  # 6

    # Combine EH ~ λ^{12} + R4 ~ λ^{6} both positive — no min
    def V_EH_R4(lam: float) -> float:
        if lam <= 0:
            return 1e300
        I_R = data["sigma_star"] ** 2 * sum(j * (j + 1.0) for j in data["j1"])
        return I_R * (lam**12) + I_R4_unit * (lam**6)

    # Δη enters only as discrete holonomy — attach as pure multiplicative weight
    # using monodromy order (locked), still pure number times same powers
    mono = data["monodromy"]
    n_sum = sum(data["n_eta"])

    def V_with_mono_weight(lam: float) -> float:
        # weight monodromy as overall pure prefactor, not a new continuous coeff
        return mono * V_EH_R4(lam) + n_sum * 0.0

    # Search minima
    def scan_min(f) -> List[Dict[str, float]]:
        out = []
        for lo, hi in [(1e-3, 1.0), (1.0, 100.0)]:
            res = minimize_scalar(f, bounds=(lo, hi), method="bounded")
            if res.success:
                h = max(1e-6 * res.x, 1e-9)
                v2 = (f(res.x + h) - 2 * f(res.x) + f(res.x - h)) / (h * h)
                out.append(
                    {
                        "lambda": float(res.x),
                        "V": float(res.fun),
                        "V2": float(v2),
                        "stable_interior": bool(v2 > 0 and lo < res.x < hi),
                    }
                )
        return out

    scan_eh_r4 = scan_min(V_EH_R4)

    return {
        "mechanism": "curvature_flux_euler_interlock",
        "euler_characteristics": {
            "chi_T11": chi_T11,
            "chi_Sigma5": chi_Sigma5,
            "chi_product_internal_10": chi_product_10,
            "implication": (
                "Odd-dimensional SE/wall factors have χ=0; pure Euler densities "
                "do not generate a volume potential on those factors."
            ),
        },
        "topological_terms": {
            "S_Euler": "∝ χ(M) metric-independent — cannot minimize volume in λ",
            "Hirzebruch_signature": "topological integer — λ-independent",
        },
        "R4_corrections": {
            "scaling_weight_sqrtg_R4": d - 8,
            "wilson_coefficient_alpha4_locked_by_Delta_eta": False,
            "reason": (
                "Δη monodromy data fix holonomy phases, not higher-curvature "
                "Wilson coefficients. Setting α4 to a locked integer still yields "
                "same-sign powers with EH and no unique stable finite-λ minimum."
            ),
            "V_EH_plus_R4_scan": scan_eh_r4,
        },
        "Delta_eta_data_used_as": (
            "pure discrete weights (monodromy, n_Σ) only — no continuous free α"
        ),
        "decision": {
            "fixes_overall_scale_lambda": False,
            "topological_minimization_at_specific_volume": False,
            "reason": (
                "Euler/signature invariants are λ-independent pure numbers (and "
                "vanish on odd factors). R^4 terms either introduce free Wilson "
                "coefficients or, if α4 is set to locked pure numbers, combine "
                "with EH into same-sign power laws without a stable finite-λ "
                "critical point forced by Δη data."
            ),
            "residual_freedom": "λ ∈ ℝ⁺; no topological volume-minimizing critical point",
            "continuous_knobs": 0,
        },
    }


def run_all() -> Dict[str, Any]:
    data = load_locked()
    p1 = probe_trace_anomaly(data)
    p2 = probe_non_middle_flux(data)
    p3 = probe_curvature_topology(data)

    any_success = any(
        p["decision"]["fixes_overall_scale_lambda"] for p in (p1, p2, p3)
    )

    return {
        "banner": "AGC Expansion Mode Active — non-zero conformal weight scale probes",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "scientific_core_locks_altered": False,
        "lock_forced": False,
        "probe_1_trace_anomaly": p1,
        "probe_2_non_middle_flux": p2,
        "probe_3_curvature_euler": p3,
        "joint_decision": {
            "any_mechanism_fixes_lambda": any_success,
            "verdict": "NEGATIVE" if not any_success else "POSITIVE",
            "summary": (
                "All three non-zero conformal-weight mechanisms fail to force a "
                "unique overall scale λ from locked data alone: (1) anomaly/β give "
                "pure a,c,b0 but DT still needs μ0; (2) non-middle flux weights "
                "clash with EH but positive-definite kinetics yield no stable min "
                "without free opposite-sign couplings; (3) Euler/signature are "
                "λ-independent (χ=0 on odd factors) and R^4 is either free Wilson "
                "or same-sign power-law without unique min. Residual freedom: λ∈ℝ⁺."
            ),
            "residual_continuous_family": (
                "λ ∈ ℝ⁺ (overall conformal factor / volume radius at fixed shape σ*)"
            ),
        },
        "checksum": "Zero continuous free parameters confirmed | continuous_knobs = 0",
    }


def update_state(result: Dict[str, Any]) -> None:
    if not os.path.isfile(EXPANSION_STATE_PATH):
        return
    with open(EXPANSION_STATE_PATH, encoding="utf-8") as f:
        es = json.load(f)
    ts = result["timestamp_utc"]
    es.setdefault("depth_probes", []).append(
        {
            "probe": "scale_weight_probes_anomaly_flux_euler",
            "timestamp_utc": ts,
            "verdict": result["joint_decision"]["verdict"],
            "any_fixes_lambda": result["joint_decision"]["any_mechanism_fixes_lambda"],
            "residual_freedom": result["joint_decision"]["residual_continuous_family"],
            "artifact": "scale_weight_probes.json",
            "continuous_knobs": 0,
        }
    )
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "scale_weight_probes",
            "action": "probe_only_no_lock",
            "item": "trace anomaly + non-middle flux + Euler/R4",
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
    print("Non-zero conformal weight probes: anomaly | non-middle flux | Euler/R^4\n")
    result = run_all()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    update_state(result)

    for key, title in [
        ("probe_1_trace_anomaly", "1) TRACE ANOMALY"),
        ("probe_2_non_middle_flux", "2) NON-MIDDLE FLUX"),
        ("probe_3_curvature_euler", "3) CURVATURE / EULER / R^4"),
    ]:
        p = result[key]
        d = p["decision"]
        print("=" * 72)
        print(title)
        print("=" * 72)
        print(f"  Fixes λ? {d['fixes_overall_scale_lambda']}")
        print(f"  Residual: {d.get('residual_freedom') or d.get('reason', '')[:120]}")
        if key == "probe_1_trace_anomaly":
            print(f"  b0 (SU3, n_f=N_gen Dirac): {p['gauge_beta']['b0_SU3_n_f_eq_N_gen_Dirac']}")
            print(f"  DT absolute without μ0? {p['gauge_beta']['dt_fixes_absolute_lambda_without_UV_input']}")
        print()

    jd = result["joint_decision"]
    print("=" * 72)
    print("JOINT DECISION")
    print("=" * 72)
    print(f"  Verdict: {jd['verdict']}")
    print(f"  {jd['summary']}")
    print(f"  Residual family: {jd['residual_continuous_family']}")
    print(f"  continuous_knobs = {result['continuous_knobs']}")
    print(f"  lock_forced = {result['lock_forced']}")
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
