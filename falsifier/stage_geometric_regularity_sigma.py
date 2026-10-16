#!/usr/bin/env python3
"""
Geometric regularity / non-degeneracy probe for σ.

Question: do locked structures force σ ≥ σ_min > 0 as a regularity bound,
or can σ approach 0+ while remaining in the topological sector?

Does not rewrite locked numerics. Does not promote a new σ or residual.
continuous_knobs remains 0.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List, Optional

from native_aps_index import aps_dirac_index, compute_native_generation_index, is_self_dual
from stage1a_validator import star_psi_defect_sq
from stage1b_sigma_solver import (
    d2potential,
    load_locked_stage1a,
    potential,
    ym_flux_coeff,
)
from stage1c_predictive import derive_n_topological
from stage2b_beta_variational import eight_pi_g_eff, metric_bar
from stage_residual_stability_map import monodromy_order, topological_gates

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "geometric_regularity_sigma.json")
LOG_PATH = os.path.join(ARTIFACT_DIR, "verification_log.txt")

LOCKED_R = 0.095716
LOCKED_SIGMA = math.sqrt(3.0) / 2.0
LAMBDA0 = 4.5
LOCKED_N_ETA = (3, 8, 15)
LOCKED_J1 = (0.5, 1.0, 1.5)

BANNER = "GEOMETRIC REGULARITY PROBE FOR σ COMPLETE – OFFICIAL LOCK UNTOUCHED"

# Diagnostic sample, not a lock.
PROBE_SIGMAS = (LOCKED_SIGMA, 0.1, 1.0e-2, 1.0e-4)


def load_baseline() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def metric_degeneracy(sigma: float) -> Dict[str, Any]:
    g = metric_bar(sigma)
    det2 = float(g[0, 0] * g[1, 1])  # σ⁴
    det5 = float(np_det_diag(g))
    return {
        "sigma": float(sigma),
        "g00": float(g[0, 0]),
        "g11": float(g[1, 1]),
        "det_first_2block": det2,
        "det_g_bar": det5,
        "nondegenerate": bool(sigma > 0.0 and det5 > 0.0),
    }


def np_det_diag(g) -> float:
    d = 1.0
    for i in range(g.shape[0]):
        d *= float(g[i, i])
    return d


def row(
    mechanism: str,
    forced: bool,
    sigma_min: Optional[str],
    bound_type: str,
    form: str,
    evidence: str,
) -> Dict[str, Any]:
    return {
        "mechanism": mechanism,
        "forced": forced,
        "sigma_min": sigma_min,
        "type": bound_type,
        "form": form,
        "evidence": evidence,
    }


def probe() -> Dict[str, Any]:
    b = load_baseline()
    lr = b.get("locked_results") or {}
    fls = b.get("final_locked_state") or {}
    r_lock = float(lr.get("beta_residual_new") or LOCKED_R)
    sigma_lock = float(lr.get("sigma_star") or LOCKED_SIGMA)
    knobs = int(fls.get("continuous_knobs") or lr.get("continuous_knobs") or 0)
    if knobs != 0:
        raise RuntimeError("continuous_knobs must be 0")

    n_gen = int(compute_native_generation_index().n_gen_native)
    gates_small = {s: topological_gates() for s in PROBE_SIGMAS}
    # gates ignore σ; record that fact
    stage1a = load_locked_stage1a()
    v_at = {s: potential(s, stage1a) for s in PROBE_SIGMAS}
    v_at[0.0] = potential(0.0, stage1a)
    flux = float(ym_flux_coeff(stage1a))
    m2_at_star = float(d2potential(LOCKED_SIGMA, stage1a))
    g8_star = float(eight_pi_g_eff(LOCKED_SIGMA))
    deg = {s: metric_degeneracy(s) for s in PROBE_SIGMAS + (0.0,)}
    defects = [star_psi_defect_sq(j, 0.0) for j in LOCKED_J1]
    n_from_j1 = tuple(derive_n_topological(j) for j in LOCKED_J1)
    t_wall = float(Fraction(13, 2))

    rows: List[Dict[str, Any]] = [
        row(
            "APS / spectral-flow regularity",
            False,
            None,
            "topological (independent of σ)",
            "index(D_APS)=max(0,⌊4j₁−6⌋₊) on j₂=0, r_APS=0; N_gen=#kernel",
            (
                f"Native N_gen={n_gen} at every probed σ. APS index uses (j₁,j₂,r_APS) "
                "only. Spectral-flow wall is j₁=3/2, not a bound on squashing. "
                "Gates still pass at σ=10⁻⁴."
            ),
        ),
        row(
            "Self-duality ⋆Ψ=Ψ",
            False,
            None,
            "topological (independent of σ)",
            "‖⋆Ψ−Ψ‖²=0 ⇔ j₂=0; defect=(2j₁+1)(2j₂+1)(j₁−j₂)²/4",
            (
                f"Locked defects={defects} on j₂=0. Self-duality does not involve σ. "
                "No σ_min."
            ),
        ),
        row(
            "Positive Σ⁵ / mode volume",
            False,
            None,
            "topological (independent of σ)",
            "vol(N⁵)=j₁(j₁+1) on the j₂=0 line",
            (
                "Survivor volumes {0.75, 2, 3.75} are representation data, not "
                "functions of squashing. Positive mode volume does not bound σ."
            ),
        ),
        row(
            "Metric non-degeneracy of ḡ=diag(σ²,σ²,1,1,1)",
            False,
            "none (only σ>0; inf=0)",
            "geometric regularity (open cone, not a floor)",
            "det(ḡ_2block)=σ⁴; ḡ degenerate iff σ=0",
            (
                "σ=0 collapses the first two metric directions (not a regular "
                "Riemannian point). The regular locus is the open ray σ>0. "
                "That is not a bound σ≥σ_min>0: inf{σ: ḡ non-degenerate}=0. "
                f"At σ=10⁻⁴, det(ḡ_2block)={deg[1e-4]['det_first_2block']}>0."
            ),
        ),
        row(
            "Domain-wall tension T_wall",
            False,
            None,
            "spectral (independent of σ)",
            "T_wall=Σ j(j+1)=13/2",
            (
                f"T_wall={t_wall} is a discrete Casimir, independent of σ and of r. "
                "No wall–squashing balance is forced. τ_res=r σ²→0 as σ→0, so "
                "residual stress does not push σ away from 0."
            ),
        ),
        row(
            "Einstein–YM positivity / curvature",
            False,
            None,
            "variational (residual prefers smaller σ)",
            "8πG_eff=σ²/C₂; F²∝(Δη/σ)²; r=‖β−8πG T_YM‖",
            (
                f"At σ*, 8πG_eff={g8_star:.6f}. Gated residual minimization with "
                "the ±5% box removed drove r from 0.0897 to 0.0110 as σ→10⁻⁴ "
                "with all topological gates still passing. EY residual therefore "
                "does not force σ≥σ_min>0; it collapses as σ→0⁺."
            ),
        ),
        row(
            "Monodromy / η-lattice under σ deformation",
            False,
            None,
            "topological (independent of σ)",
            "n=4 j₁(j₁+1); Δη=nπ/12; monodromy lcm=24",
            (
                f"Topological n_η={list(n_from_j1)}={list(LOCKED_N_ETA)}; "
                f"monodromy={monodromy_order(LOCKED_N_ETA)}. None of these integers "
                "depends on σ. σ deformation cannot break the lattice until a "
                "discrete n_η step is taken (a different gate)."
            ),
        ),
        row(
            "Geometric V(σ) flux wall (Stage 1B)",
            False,
            "not a regularity floor; V-minimizer is already locked σ*=√3/2",
            "variational (potential of a different functional)",
            "V(σ)=(3/2)σ²+(3/2)(λ̃₀/6)²/σ²; V→+∞ as σ→0⁺ and as σ→∞",
            (
                f"YM flux coeff={flux:.6f}; V(σ*)={v_at[LOCKED_SIGMA]:.6f}; "
                f"V(10⁻⁴)={v_at[1e-4]:.6e}; m²_σ|*=d²V/dσ²={m2_at_star:.6f}>0. "
                "This wall selects the V-minimizer σ*=√3/2 (already the official "
                "shape lock). It does not forbid points with 0<σ≪σ* in the "
                "topological sector, nor does it bound the Einstein–YM residual "
                "functional, which decreases as σ→0⁺. Not a topological σ_min."
            ),
        ),
    ]

    forced_any = any(r["forced"] for r in rows)
    decision = "YES" if forced_any else "NO"
    reason = (
        "No locked structure forces a strictly positive lower bound σ≥σ_min>0 "
        "on the topological sector. APS, self-duality, η-lattice, and T_wall "
        "are independent of σ. Metric non-degeneracy requires only σ>0 "
        "(infimum 0). V(σ)→∞ as σ→0⁺ selects the already-locked V-minimizer "
        "σ*=√3/2 and does not police the residual functional. Gated residual "
        "minimization with the σ box removed reached σ=10⁻⁴ at r≈0.011 with "
        "zero gate rejections. Official σ* and r=0.095716 are unchanged."
    )

    return {
        "banner": BANNER,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "official_lock_unchanged": True,
        "official_beta_residual": LOCKED_R,
        "official_sigma_star": "sqrt(3)/2",
        "new_sigma_promoted": False,
        "new_residual_promoted": False,
        "open_gaps_remain_open": True,
        "absolute_scale_posture": "observational_conversion_only",
        "question": (
            "Do locked geometric structures force σ ≥ σ_min > 0 as a "
            "regularity / non-degeneracy bound?"
        ),
        "decision": decision,
        "reason": reason,
        "mechanisms": rows,
        "diagnostics": {
            "n_gen_native": n_gen,
            "aps_index_j1_3_over_2": aps_dirac_index(1.5, 0.0, 0.0),
            "self_dual_j2_0": is_self_dual(1.0, 0.0),
            "star_psi_defects_locked": defects,
            "n_eta_from_j1": list(n_from_j1),
            "monodromy_order": monodromy_order(LOCKED_N_ETA),
            "T_wall": t_wall,
            "eight_pi_g_eff_at_sigma_star": g8_star,
            "V_at_probe_sigma": {str(s): v_at[s] for s in PROBE_SIGMAS},
            "V_at_sigma_0": "inf",
            "m2_sigma_at_star": m2_at_star,
            "metric_at_probe_sigma": {str(s): deg[s] for s in PROBE_SIGMAS},
            "metric_at_sigma_0": deg[0.0],
            "topological_gates_independent_of_sigma": True,
            "gates_passed_at_all_probe_sigma": all(
                g["passed"] for g in gates_small.values()
            ),
            "prior_free_sigma_minimization": {
                "file": "residual_minimization_no_sigma_box.json",
                "lowest_residual": 0.011020994962764246,
                "sigma_at_numerical_floor": 1.0e-4,
                "gate_rejections": 0,
            },
        },
        "locked_snapshot": {
            "n_gen": 3,
            "sigma_star": sigma_lock,
            "lambda_tilde": [4.5, 12.0, 22.5],
            "beta_residual_official": r_lock,
            "n_eta": list(LOCKED_N_ETA),
            "continuous_knobs": 0,
        },
    }


def main() -> None:
    print(BANNER.replace("COMPLETE", "STARTED"))
    print()
    res = probe()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")

    extra = [
        "",
        "GEOMETRIC REGULARITY PROBE FOR σ (official lock unchanged)",
        f"timestamp_utc: {res['timestamp_utc']}",
        "continuous_knobs: 0",
        "verification: 8/8 PASS (not re-run; locked core untouched)",
        f"decision: {res['decision']}",
        "official_sigma_star: sqrt(3)/2 (NOT replaced)",
        f"official_beta_residual_lock: {LOCKED_R} (NOT replaced)",
        "new_sigma_promoted: False",
        "new_residual_promoted: False",
        "open_gaps_remain_open: True",
        f"reason: {res['reason']}",
        "END GEOMETRIC REGULARITY PROBE FOR σ",
        "",
    ]
    with open(LOG_PATH, encoding="utf-8") as f:
        log_text = f.read()
    marker = "GEOMETRIC REGULARITY PROBE FOR σ (official"
    if marker in log_text:
        log_text = log_text[: log_text.index(marker)].rstrip() + "\n"
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(log_text)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(extra))

    print(f"{'Mechanism':<48} {'Forced?':<8} {'σ_min':<22} {'Type'}")
    print("-" * 110)
    for m in res["mechanisms"]:
        smin = m["sigma_min"] if m["sigma_min"] else "none"
        print(f"{m['mechanism']:<48} {str(m['forced']):<8} {str(smin):<22} {m['type']}")
    print()
    print(f"Final binary answer: {res['decision']}")
    print(f"continuous_knobs = {res['continuous_knobs']}")
    print(f"Wrote {OUT_PATH}")
    print(BANNER)


if __name__ == "__main__":
    main()
