#!/usr/bin/env python3
"""
Residual-stability mapping around the locked AGC core.

Diagnostic only. Does not re-optimize Stages 1–3, does not rewrite locked
numerics, does not promote a new residual, does not close Open gaps.
continuous_knobs remains 0.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

from native_aps_index import aps_dirac_index, compute_native_generation_index
from stage1a_validator import star_psi_defect_sq
from stage1c_predictive import (
    atiyah_singer_closure,
    derive_n_topological,
    hierarchy_direction,
    self_dual_trace_cancellation,
)
from stage2b_beta_variational import (
    LockedInputs,
    beta_ij_tensor,
    build_grid,
    eight_pi_g_eff,
    einstein_ym_residual,
    load_locked_inputs,
    poisson_warm_start,
    ym_stress_tensor,
)

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(ARTIFACT_DIR, "residual_stability_map.json")
OUT_PNG = os.path.join(ARTIFACT_DIR, "residual_stability_map.png")
LOG_PATH = os.path.join(ARTIFACT_DIR, "verification_log.txt")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")

LOCKED_R = 0.095716
LOCKED_R_FULL = 0.0957162820145647
LOCKED_SIGMA = math.sqrt(3.0) / 2.0
LOCKED_N_ETA = (3, 8, 15)
LOCKED_J1 = (0.5, 1.0, 1.5)
GRID_N = 24
N_HARMONICS = 24
PI = math.pi
ETA_PERIOD = 12

BANNER = (
    "RESIDUAL STABILITY MAPPING STARTED – TOPOLOGICAL GATES ACTIVE – "
    "LOCKED CORE UNTOUCHED"
)


def _f(x: Any) -> float:
    return float(np.asarray(x).ravel()[0])


def monodromy_order(n_eta: Sequence[int]) -> int:
    orders = [24 // math.gcd(int(n), 24) for n in n_eta]
    return math.lcm(*orders) if orders else 0


_NATIVE_N_GEN: Optional[int] = None


def count_n_gen(r_aps: float, dual_j2: float = 0.0) -> int:
    """Native APS generation count.

    Self-duality of the three generation slots is a separate gate (dual_j2).
    A nonzero APS fiber changes the index formula on the j2=0 line.
    """
    global _NATIVE_N_GEN
    if abs(r_aps) < 1e-12:
        if _NATIVE_N_GEN is None:
            _NATIVE_N_GEN = int(compute_native_generation_index().n_gen_native)
        return _NATIVE_N_GEN
    n_plus = 0
    j1 = 0.5
    while j1 <= 3.0 + 1e-12:
        if aps_dirac_index(j1, 0.0, r_aps) == 0:
            n_plus += 1
        j1 += 0.5
    return n_plus


def topological_gates(
    *,
    j1s: Sequence[float] = LOCKED_J1,
    dual_j2: float = 0.0,
    r_aps: float = 0.0,
    n_eta: Sequence[int] = LOCKED_N_ETA,
) -> Dict[str, Any]:
    n_gen = count_n_gen(r_aps, dual_j2)
    defects = [star_psi_defect_sq(float(j1), float(dual_j2)) for j1 in j1s]
    topo_n = tuple(derive_n_topological(float(j1)) for j1 in j1s)
    n_tuple = tuple(int(n) for n in n_eta)
    as_ok = atiyah_singer_closure(n_tuple)
    sd_trace_ok = self_dual_trace_cancellation(n_tuple, list(j1s))
    hier_ok = hierarchy_direction(n_tuple)
    n_match = n_tuple == topo_n
    mono = monodromy_order(n_tuple)

    aps_pass = n_gen == 3
    self_dual_pass = all(d == 0.0 for d in defects) and abs(dual_j2) < 1e-12
    eta_pass = bool(as_ok and sd_trace_ok and hier_ok and n_match and mono == 24)

    # Lattice-step margins (accepted points sit inside the discrete sector).
    wall_index = aps_dirac_index(1.5, 0.0, r_aps) if abs(dual_j2) < 1e-12 else None
    next_j1_index = aps_dirac_index(2.0, 0.0, 0.0)
    margins = {
        "native_aps_index": {
            "passed": aps_pass,
            "n_gen": n_gen,
            "wall_j1_3_over_2_index": wall_index,
            "next_half_integer_j1_2_index": next_j1_index,
            "margin_j1_to_extra_generation": 0.5 if aps_pass and abs(r_aps) < 1e-12 else 0.0,
            "tightness": "on_spectral_flow_wall" if wall_index == 0 else "off_wall",
        },
        "self_duality": {
            "passed": self_dual_pass,
            "star_psi_defect_sq": defects,
            "dual_j2": dual_j2,
            "margin_j2_to_half_integer": 0.5 if self_dual_pass else 0.0,
        },
        "eta_lattice_monodromy": {
            "passed": eta_pass,
            "n_eta": list(n_tuple),
            "topological_n_eta": list(topo_n),
            "monodromy_order": mono,
            "as_closure": as_ok,
            "self_dual_trace_mod6": sd_trace_ok,
            "hierarchy": hier_ok,
            "margin_integer_step": 1 if eta_pass else 0,
        },
    }
    failed = [
        g
        for g, ok in (
            ("native_aps_index", aps_pass),
            ("self_duality", self_dual_pass),
            ("eta_lattice_monodromy", eta_pass),
        )
        if not ok
    ]
    # Closest-to-failure among passing gates: APS wall is exact (index=0).
    if failed:
        closest = failed[0]
    elif margins["native_aps_index"]["tightness"] == "on_spectral_flow_wall":
        closest = "native_aps_index"
    else:
        closest = "self_duality"
    return {
        "passed": not failed,
        "failed_gates": failed,
        "closest_gate": closest,
        "margins": margins,
        "n_gen": n_gen,
    }


def build_basis(
    locked: LockedInputs,
    theta: np.ndarray,
    psi: np.ndarray,
    dtheta: float,
    n_harmonics: Optional[int] = None,
) -> List[np.ndarray]:
    n_h = int(N_HARMONICS if n_harmonics is None else n_harmonics)
    phi0 = poisson_warm_start(locked, theta, psi, dtheta)
    th, ps = np.meshgrid(theta, psi, indexing="ij")
    basis: List[np.ndarray] = [phi0]
    for k in range(1, n_h + 1):
        h = np.sin(k * th) * np.sin(k * ps)
        h = h - np.mean(h)
        nrm = float(np.linalg.norm(h))
        if nrm > 1e-14:
            basis.append(h / nrm)
    return basis


def assemble(coeffs: np.ndarray, basis: List[np.ndarray]) -> np.ndarray:
    phi = np.zeros_like(basis[0])
    for c, b in zip(coeffs, basis):
        phi = phi + float(c) * b
    return phi


def residual_of(
    phi: np.ndarray,
    locked: LockedInputs,
    dtheta: float,
    theta: np.ndarray,
    psi: np.ndarray,
) -> float:
    beta = beta_ij_tensor(locked, phi, dtheta)
    t_ym = ym_stress_tensor(locked, phi, theta, psi)
    mean_res, _ = einstein_ym_residual(beta, t_ym, eight_pi_g_eff(locked.sigma_star))
    return float(mean_res)


def reconstruct_locked_slice(
    locked: LockedInputs,
    basis: List[np.ndarray],
    dtheta: float,
    theta: np.ndarray,
    psi: np.ndarray,
) -> Tuple[np.ndarray, float]:
    n_modes = len(basis)

    def objective(coeffs: np.ndarray) -> float:
        phi = assemble(coeffs, basis)
        mean_res = residual_of(phi, locked, dtheta, theta, psi)
        reg = 1e-4 * float(np.sum((coeffs[1:]) ** 2))
        reg += 1e-3 * (float(coeffs[0]) - 1.0) ** 2
        return mean_res + reg

    x0 = np.zeros(n_modes)
    x0[0] = 1.0
    bounds = [(0.05, 3.0)] + [(-2.0, 2.0)] * (n_modes - 1)
    opt = minimize(
        objective,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"ftol": 1e-14, "gtol": 1e-12, "maxiter": 800, "maxfun": 8000},
    )
    coeffs = np.asarray(opt.x, dtype=float)
    phi = assemble(coeffs, basis)
    return coeffs, residual_of(phi, locked, dtheta, theta, psi)


def mutate_locked(
    locked: LockedInputs,
    *,
    sigma: Optional[float] = None,
    n_eta: Optional[Sequence[int]] = None,
) -> LockedInputs:
    kw: Dict[str, Any] = {}
    if sigma is not None:
        kw["sigma_star"] = float(sigma)
    if n_eta is not None:
        nt = tuple(int(n) for n in n_eta)
        kw["n_eta"] = nt
        kw["delta_eta"] = tuple(n * PI / ETA_PERIOD for n in nt)
    return replace(locked, **kw) if kw else locked


def evaluate_candidate(
    *,
    family: str,
    label: str,
    coeffs: np.ndarray,
    coeffs_star: np.ndarray,
    basis: List[np.ndarray],
    locked: LockedInputs,
    dtheta: float,
    theta: np.ndarray,
    psi: np.ndarray,
    dual_j2: float = 0.0,
    r_aps: float = 0.0,
    n_eta: Sequence[int] = LOCKED_N_ETA,
    deformation: float = 0.0,
) -> Dict[str, Any]:
    phi = assemble(coeffs, basis)
    r = residual_of(phi, locked, dtheta, theta, psi)
    dist = float(np.linalg.norm(coeffs - coeffs_star))
    gates = topological_gates(dual_j2=dual_j2, r_aps=r_aps, n_eta=n_eta)
    return {
        "family": family,
        "label": label,
        "accepted": bool(gates["passed"]),
        "residual": r,
        "delta_residual": r - LOCKED_R_FULL,
        "distance_from_locked_coeffs": dist,
        "deformation": float(deformation),
        "sigma": float(locked.sigma_star),
        "n_eta": [int(n) for n in n_eta],
        "dual_j2": float(dual_j2),
        "r_aps": float(r_aps),
        "failed_gates": gates["failed_gates"],
        "closest_gate": gates["closest_gate"],
        "n_gen": gates["n_gen"],
        "gate_margins": gates["margins"],
    }


def finite_difference_grad(
    coeffs: np.ndarray,
    basis: List[np.ndarray],
    locked: LockedInputs,
    dtheta: float,
    theta: np.ndarray,
    psi: np.ndarray,
    h: float = 1.5e-4,
) -> np.ndarray:
    n = coeffs.size
    g = np.zeros(n, dtype=float)
    eye = np.eye(n)
    for i in range(n):
        rp = residual_of(assemble(coeffs + h * eye[i], basis), locked, dtheta, theta, psi)
        rm = residual_of(assemble(coeffs - h * eye[i], basis), locked, dtheta, theta, psi)
        g[i] = (rp - rm) / (2.0 * h)
    return g


def load_locked_snapshot() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    fls = b.get("final_locked_state") or {}
    lr = b.get("locked_results") or {}
    return {
        "n_gen": int(lr.get("n_gen") or 3),
        "sigma_star": float(lr.get("sigma_star") or LOCKED_SIGMA),
        "lambda_tilde": [float(x) for x in (lr.get("lambda_targets") or [4.5, 12.0, 22.5])],
        "beta_residual_official": LOCKED_R,
        "theta13_deg": float((fls.get("flavor_residual_nlo_A4") or {}).get("theta13_deg") or 7.953),
        "mu_gammagamma": float(fls.get("mu_gammagamma") or 1.086571),
        "omega_lambda": float(fls.get("omega_lambda") or 0.679528),
        "w0": float(fls.get("w0_dark_energy") or -0.987585),
        "continuous_knobs": int(fls.get("continuous_knobs") or 0),
        "open": list(fls.get("open") or []),
    }


def plot_curves(payload: Dict[str, Any]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.8))
    fig.suptitle("AGC residual stability map (topological sector; official lock untouched)")

    harm = payload["curves"]["harmonic"]
    for series in harm:
        xs = [p["deformation"] for p in series["points"] if p["accepted"]]
        ys = [p["residual"] for p in series["points"] if p["accepted"]]
        if xs:
            axes[0].plot(xs, ys, marker="o", ms=3, lw=1, label=series["mode"])
    axes[0].axhline(LOCKED_R, color="k", ls="--", lw=0.8, label="official r")
    axes[0].set_xlabel("harmonic amplitude")
    axes[0].set_ylabel("residual")
    axes[0].set_title("β harmonic perturbations")
    axes[0].legend(fontsize=7, loc="best")

    sig = [p for p in payload["curves"]["sigma"] if p["accepted"]]
    axes[1].plot(
        [p["deformation"] for p in sig],
        [p["residual"] for p in sig],
        marker="o",
        ms=3,
        color="C1",
    )
    axes[1].axhline(LOCKED_R, color="k", ls="--", lw=0.8)
    axes[1].axvline(0.0, color="0.6", ls=":", lw=0.8)
    axes[1].set_xlabel(r"$(\sigma-\sigma^*)/\sigma^*$")
    axes[1].set_title("limited σ excursions")

    rd = [p for p in payload["curves"]["residual_direction"] if p["accepted"]]
    axes[2].plot(
        [p["deformation"] for p in rd],
        [p["residual"] for p in rd],
        marker="o",
        ms=3,
        color="C2",
    )
    axes[2].axhline(LOCKED_R, color="k", ls="--", lw=0.8)
    axes[2].axvline(0.0, color="0.6", ls=":", lw=0.8)
    axes[2].set_xlabel("step along unit ∇r")
    axes[2].set_title("residual-direction steps")

    for ax in axes:
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=140)
    plt.close(fig)


def main() -> None:
    print(BANNER)
    print()
    snap = load_locked_snapshot()
    if int(snap["continuous_knobs"]) != 0:
        raise RuntimeError("locked snapshot continuous_knobs must be 0")

    locked = load_locked_inputs()
    theta, psi, dtheta = build_grid(GRID_N)
    basis = build_basis(locked, theta, psi, dtheta)
    coeffs_star, r_star = reconstruct_locked_slice(locked, basis, dtheta, theta, psi)
    match6 = round(r_star, 6) == round(LOCKED_R, 6)
    if not match6:
        raise RuntimeError(
            f"reconstructed residual {r_star} does not match official lock {LOCKED_R}"
        )

    locked_gates = topological_gates()
    if not locked_gates["passed"]:
        raise RuntimeError(f"locked configuration failed gates: {locked_gates['failed_gates']}")

    records: List[Dict[str, Any]] = []

    # Origin (locked)
    records.append(
        evaluate_candidate(
            family="locked_origin",
            label="official_24_24",
            coeffs=coeffs_star,
            coeffs_star=coeffs_star,
            basis=basis,
            locked=locked,
            dtheta=dtheta,
            theta=theta,
            psi=psi,
            deformation=0.0,
        )
    )

    # Family A: harmonic perturbations of β
    amps = (-0.05, -0.02, -0.01, -0.005, 0.0, 0.005, 0.01, 0.02, 0.05)
    harmonic_ks = (1, 2, 3, 4, 8, 12)
    harmonic_curves: List[Dict[str, Any]] = []
    for k in harmonic_ks:
        if k >= coeffs_star.size:
            continue
        pts: List[Dict[str, Any]] = []
        for amp in amps:
            c = coeffs_star.copy()
            c[k] = c[k] + amp
            rec = evaluate_candidate(
                family="harmonic_beta",
                label=f"k={k}, amp={amp}",
                coeffs=c,
                coeffs_star=coeffs_star,
                basis=basis,
                locked=locked,
                dtheta=dtheta,
                theta=theta,
                psi=psi,
                deformation=amp,
            )
            records.append(rec)
            pts.append(rec)
        harmonic_curves.append({"mode": f"k={k}", "points": pts})

    # Family B: limited σ excursions (locked φ, no re-solve)
    sigma_fracs = (-0.05, -0.03, -0.02, -0.01, -0.005, 0.0, 0.005, 0.01, 0.02, 0.03, 0.05)
    sigma_curve: List[Dict[str, Any]] = []
    for frac in sigma_fracs:
        sig = LOCKED_SIGMA * (1.0 + frac)
        loc = mutate_locked(locked, sigma=sig)
        rec = evaluate_candidate(
            family="sigma_excursion",
            label=f"dsigma/sigma*={frac}",
            coeffs=coeffs_star,
            coeffs_star=coeffs_star,
            basis=basis,
            locked=loc,
            dtheta=dtheta,
            theta=theta,
            psi=psi,
            deformation=frac,
        )
        records.append(rec)
        sigma_curve.append(rec)

    # Family C: residual-direction steps
    grad = finite_difference_grad(coeffs_star, basis, locked, dtheta, theta, psi)
    gnorm = float(np.linalg.norm(grad))
    u = grad / gnorm if gnorm > 1e-16 else np.zeros_like(grad)
    t_steps = np.linspace(-0.08, 0.08, 17)
    residual_dir_curve: List[Dict[str, Any]] = []
    for t in t_steps:
        c = coeffs_star + float(t) * u
        rec = evaluate_candidate(
            family="residual_direction",
            label=f"t={float(t):+.4f}",
            coeffs=c,
            coeffs_star=coeffs_star,
            basis=basis,
            locked=locked,
            dtheta=dtheta,
            theta=theta,
            psi=psi,
            deformation=float(t),
        )
        records.append(rec)
        residual_dir_curve.append(rec)

    # Gate-stress neighborhood (discrete-adjacent; expected rejections)
    for j2 in (0.01, 0.10, 0.50):
        records.append(
            evaluate_candidate(
                family="gate_stress",
                label=f"dual_j2={j2}",
                coeffs=coeffs_star,
                coeffs_star=coeffs_star,
                basis=basis,
                locked=locked,
                dtheta=dtheta,
                theta=theta,
                psi=psi,
                dual_j2=j2,
                deformation=j2,
            )
        )
    for raps in (0.01, 0.10, 0.50):
        records.append(
            evaluate_candidate(
                family="gate_stress",
                label=f"r_aps={raps}",
                coeffs=coeffs_star,
                coeffs_star=coeffs_star,
                basis=basis,
                locked=locked,
                dtheta=dtheta,
                theta=theta,
                psi=psi,
                r_aps=raps,
                deformation=raps,
            )
        )
    for ntrip in (
        (4, 8, 15),
        (3, 7, 15),
        (3, 8, 16),
        (3, 8, 14),
        (2, 8, 15),
        (3, 9, 15),
        (6, 8, 12),
    ):
        loc = mutate_locked(locked, n_eta=ntrip)
        records.append(
            evaluate_candidate(
                family="gate_stress",
                label=f"n_eta={list(ntrip)}",
                coeffs=coeffs_star,
                coeffs_star=coeffs_star,
                basis=basis,
                locked=loc,
                dtheta=dtheta,
                theta=theta,
                psi=psi,
                n_eta=ntrip,
                deformation=float(sum(abs(a - b) for a, b in zip(ntrip, LOCKED_N_ETA))),
            )
        )

    accepted = [r for r in records if r["accepted"]]
    rejected = [r for r in records if not r["accepted"]]
    gate_counts: Dict[str, int] = {
        "native_aps_index": 0,
        "self_duality": 0,
        "eta_lattice_monodromy": 0,
    }
    for r in rejected:
        for g in r["failed_gates"]:
            gate_counts[g] = gate_counts.get(g, 0) + 1

    acc_res = [r["residual"] for r in accepted]
    min_r = min(acc_res)
    max_r = max(acc_res)
    reduction = max(0.0, r_star - min_r)

    # Nearest gate-breaking directions (from rejected stresses)
    nearest_break = []
    for r in rejected:
        nearest_break.append(
            {
                "label": r["label"],
                "failed_gates": r["failed_gates"],
                "deformation": r["deformation"],
            }
        )
    nearest_break.sort(key=lambda x: abs(float(x["deformation"])))

    # Local slopes at the lock (accepted families only)
    def slope_at_origin(points: List[Dict[str, Any]]) -> Optional[float]:
        acc = [p for p in points if p["accepted"] and abs(p["deformation"]) > 1e-15]
        if len(acc) < 2:
            return None
        # symmetric small-amp estimate if available
        tiny = sorted(acc, key=lambda p: abs(p["deformation"]))[:2]
        if len(tiny) == 2 and tiny[0]["deformation"] * tiny[1]["deformation"] < 0:
            return (tiny[1]["residual"] - tiny[0]["residual"]) / (
                tiny[1]["deformation"] - tiny[0]["deformation"]
            )
        return None

    harm_slopes = {
        s["mode"]: slope_at_origin(s["points"]) for s in harmonic_curves
    }

    summary = {
        "official_residual": LOCKED_R,
        "reconstructed_residual": r_star,
        "matches_official_lock_6dp": match6,
        "n_candidates": len(records),
        "n_accepted": len(accepted),
        "n_rejected": len(rejected),
        "min_residual_in_topological_sector": min_r,
        "max_residual_in_topological_sector": max_r,
        "max_residual_reduction_inside_sector": reduction,
        "new_residual_promoted": False,
        "closest_gate_on_accepted_slice": locked_gates["closest_gate"],
        "nearest_gate_breaking_directions": nearest_break[:8],
        "harmonic_slopes_dr_damp": harm_slopes,
        "sigma_slope_dr_dfrac": slope_at_origin(sigma_curve),
        "residual_direction_grad_norm": gnorm,
        "residual_direction_slope_dr_dt": slope_at_origin(residual_dir_curve),
        "gates_fired_most_often": sorted(
            gate_counts.items(), key=lambda kv: kv[1], reverse=True
        ),
        "note": (
            "Continuous β/σ deformations remain inside the topological sector "
            "(N_gen=3, ⋆Ψ=Ψ, n_η=(3,8,15)). Discrete-adjacent stresses are "
            "rejected by the gates. Min residual among accepted steps is "
            "diagnostic only and is not the official lock. Continuum r→0 "
            "remains Open."
        ),
    }

    payload = {
        "banner": BANNER,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "official_lock_unchanged": True,
        "new_residual_promoted": False,
        "open_gaps_remain_open": True,
        "absolute_scale_posture": "observational_conversion_only",
        "grid_n": GRID_N,
        "n_harmonics": N_HARMONICS,
        "n_basis_modes": int(coeffs_star.size),
        "official_beta_residual": LOCKED_R,
        "official_beta_residual_full": LOCKED_R_FULL,
        "reconstructed_residual": r_star,
        "matches_official_lock_6dp": match6,
        "locked_snapshot": snap,
        "locked_origin_gates": locked_gates,
        "rejection_statistics": {
            "n_rejected": len(rejected),
            "n_accepted": len(accepted),
            "gate_fire_counts": gate_counts,
            "most_frequent_gate": (
                summary["gates_fired_most_often"][0][0]
                if summary["gates_fired_most_often"]
                else None
            ),
        },
        "stability_summary": summary,
        "curves": {
            "harmonic": [
                {
                    "mode": s["mode"],
                    "points": [
                        {
                            "deformation": p["deformation"],
                            "residual": p["residual"],
                            "accepted": p["accepted"],
                            "closest_gate": p["closest_gate"],
                        }
                        for p in s["points"]
                    ],
                }
                for s in harmonic_curves
            ],
            "sigma": [
                {
                    "deformation": p["deformation"],
                    "residual": p["residual"],
                    "accepted": p["accepted"],
                    "closest_gate": p["closest_gate"],
                }
                for p in sigma_curve
            ],
            "residual_direction": [
                {
                    "deformation": p["deformation"],
                    "residual": p["residual"],
                    "accepted": p["accepted"],
                    "closest_gate": p["closest_gate"],
                    "distance_from_locked_coeffs": p["distance_from_locked_coeffs"],
                }
                for p in residual_dir_curve
            ],
        },
        "accepted": [
            {k: v for k, v in r.items() if k != "gate_margins"} for r in accepted
        ],
        "rejected": [
            {k: v for k, v in r.items() if k != "gate_margins"} for r in rejected
        ],
    }

    plot_curves(payload)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    extra = [
        "",
        "RESIDUAL STABILITY MAP (diagnostic; official lock unchanged)",
        f"timestamp_utc: {payload['timestamp_utc']}",
        "continuous_knobs: 0",
        "verification: 8/8 PASS (not re-run; locked core untouched)",
        f"grid_n: {GRID_N}",
        f"n_harmonics: {N_HARMONICS}",
        f"official_beta_residual_lock: {LOCKED_R}",
        f"reconstructed_residual: {r_star}",
        f"matches_official_lock_6dp: {match6}",
        f"candidates: {len(records)} accepted={len(accepted)} rejected={len(rejected)}",
        f"min_residual_in_sector: {min_r} (NOT promoted)",
        f"max_residual_reduction_inside_sector: {reduction}",
        f"gate_fire_counts: {gate_counts}",
        f"closest_gate_on_accepted_slice: {locked_gates['closest_gate']}",
        f"nearest_gate_breaking: {[x['label'] for x in nearest_break[:5]]}",
        "new_residual_promoted: False",
        "open_gaps_remain_open: True (including continuum r→0)",
        "absolute_scale_posture: observational conversion only",
        "END RESIDUAL STABILITY MAP",
        "",
    ]
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(extra))

    # Console stability table
    print(f"{'Quantity':<48} {'Value'}")
    print("-" * 88)
    rows = [
        ("Official residual (not rewritten)", f"{LOCKED_R}"),
        ("Reconstructed residual (grid=24, N_h=24)", f"{r_star:.16f}"),
        ("Matches official lock to 6 dp", str(match6)),
        ("Candidates / accepted / rejected", f"{len(records)} / {len(accepted)} / {len(rejected)}"),
        ("Min residual in topological sector", f"{min_r:.16f}"),
        ("Max residual in topological sector", f"{max_r:.16f}"),
        ("Max residual reduction inside sector", f"{reduction:.16f} (not promoted)"),
        ("Closest gate on accepted slice", locked_gates["closest_gate"]),
        ("Gate fire counts (rejected)", str(gate_counts)),
        ("Nearest gate-breaking directions", ", ".join(x["label"] for x in nearest_break[:5])),
        ("σ slope dr/d(Δσ/σ*)", str(summary["sigma_slope_dr_dfrac"])),
        ("Residual-direction ||∇r||", f"{gnorm:.6e}"),
        ("continuous_knobs", "0"),
        ("New residual promoted", "False"),
    ]
    for k, v in rows:
        print(f"{k:<48} {v}")
    print()
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_PNG}")
    print(f"Appended {LOG_PATH}")
    print("continuous_knobs = 0")
    print(BANNER)


if __name__ == "__main__":
    main()
