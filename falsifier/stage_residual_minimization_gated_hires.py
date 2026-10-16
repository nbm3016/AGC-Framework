#!/usr/bin/env python3
"""
Higher-resolution gated residual minimization (grid=48, N_h=48).

Diagnostic only. Does not rewrite the official 24/24 lock r=0.095716.
Does not promote a new residual. continuous_knobs remains 0.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from stage_residual_minimization_gated import (
    FD_H,
    SIGMA_FRAC_BOX,
    GatedSlice,
    armijo_descent,
    load_locked_snapshot,
    run_lbfgs,
)
from stage_residual_stability_map import (
    LOCKED_N_ETA,
    LOCKED_R,
    LOCKED_R_FULL,
    LOCKED_SIGMA,
    build_basis,
    reconstruct_locked_slice,
    topological_gates,
)
from stage2b_beta_variational import build_grid, load_locked_inputs

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(ARTIFACT_DIR, "residual_minimization_gated_hires.json")
OUT_PNG = os.path.join(ARTIFACT_DIR, "residual_minimization_gated_hires.png")
LOG_PATH = os.path.join(ARTIFACT_DIR, "verification_log.txt")

GRID_N = 48
N_HARMONICS = 48
FLOOR_24 = 0.0343597987969034

BANNER = (
    "HIGHER-RESOLUTION GATED MINIMIZATION COMPLETE – OFFICIAL LOCK UNTOUCHED – "
    "TOPOLOGICAL FLOOR STATUS REPORTED"
)


def plot_trajectory(payload: Dict[str, Any]) -> None:
    traj = [
        p
        for p in payload["accepted_trajectory"]
        if p.get("kind") in {"start", "armijo", "iteration", "final"}
    ]
    if not traj:
        return
    ys = [p["residual"] for p in traj]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.plot(list(range(len(traj))), ys, marker="o", ms=3, lw=1.2, color="C0")
    ax.axhline(LOCKED_R, color="k", ls="--", lw=0.9, label="official lock 0.095716")
    ax.axhline(FLOOR_24, color="C1", ls=":", lw=0.9, label="24-mode floor 0.034360")
    ax.set_xlabel("accepted gated iterate")
    ax.set_ylabel("residual")
    ax.set_title("Higher-res gated minimization (grid=48, N_h=48; lock untouched)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=140)
    plt.close(fig)


def slim_phase(phase: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in phase.items() if k != "x"}


def main() -> None:
    print(BANNER.replace("COMPLETE", "STARTED"))
    print()
    snap = load_locked_snapshot()
    if int(snap["continuous_knobs"]) != 0:
        raise RuntimeError("locked snapshot continuous_knobs must be 0")

    locked = load_locked_inputs()
    theta, psi, dtheta = build_grid(GRID_N)
    basis = build_basis(locked, theta, psi, dtheta, n_harmonics=N_HARMONICS)
    coeffs_star, r_start = reconstruct_locked_slice(locked, basis, dtheta, theta, psi)
    g0 = topological_gates()
    if not g0["passed"]:
        raise RuntimeError(f"hires origin failed gates: {g0['failed_gates']}")

    slice_map = GatedSlice(locked, basis, dtheta, theta, psi, coeffs_star)
    slice_map.trajectory.append(
        {
            "eval": 0,
            "kind": "start",
            "residual": float(r_start),
            "accepted": True,
            "failed_gates": [],
            "closest_gate": g0["closest_gate"],
            "n_gen": 3,
            "sigma": float(LOCKED_SIGMA),
            "sigma_frac": 0.0,
            "distance_coeffs": 0.0,
            "distance_sigma_frac": 0.0,
        }
    )
    slice_map.best_accepted = {
        "residual": float(r_start),
        "accepted": True,
        "failed_gates": [],
        "closest_gate": g0["closest_gate"],
        "n_gen": 3,
        "sigma": float(LOCKED_SIGMA),
        "sigma_frac": 0.0,
        "distance_coeffs": 0.0,
        "distance_sigma_frac": 0.0,
        "coeffs": coeffs_star.copy(),
        "kind": "start",
    }

    n = coeffs_star.size
    bounds_phi = [(-8.0, 8.0)] * n

    armijo_a = armijo_descent(
        slice_map, coeffs_star, bounds_phi, with_sigma=False, max_steps=60
    )
    phase_a = run_lbfgs(
        slice_map, armijo_a["x"], bounds_phi, with_sigma=False, maxiter=120
    )
    phase_a["armijo"] = slim_phase(armijo_a)

    best_coeffs = np.asarray(phase_a["x"], dtype=float)
    if slice_map.best_accepted and "coeffs" in slice_map.best_accepted:
        best_coeffs = np.asarray(slice_map.best_accepted["coeffs"], dtype=float)

    sig_lo = LOCKED_SIGMA * (1.0 - SIGMA_FRAC_BOX)
    sig_hi = LOCKED_SIGMA * (1.0 + SIGMA_FRAC_BOX)
    x0_b = np.concatenate([[LOCKED_SIGMA], best_coeffs])
    bounds_b = [(sig_lo, sig_hi)] + bounds_phi
    armijo_b = armijo_descent(
        slice_map, x0_b, bounds_b, with_sigma=True, max_steps=30
    )
    phase_b = run_lbfgs(
        slice_map, armijo_b["x"], bounds_b, with_sigma=True, maxiter=80
    )
    phase_b["armijo"] = slim_phase(armijo_b)

    best = slice_map.best_accepted or {}
    lowest = float(best.get("residual", r_start))
    reduction = max(0.0, float(r_start) - lowest)
    vs_24 = float(lowest - FLOOR_24)

    rejected_final = list(phase_a.get("final_failed_gates") or []) + list(
        phase_b.get("final_failed_gates") or []
    )
    if slice_map.n_rejected > 0 and rejected_final:
        stop_reason = "topological_gate_rejection"
        stopping_gate = rejected_final[0]
        floor_status = "topological_gate_floor"
    elif lowest < 1.0e-6:
        stop_reason = "numerical_convergence_near_zero_inside_sector"
        stopping_gate = None
        floor_status = "no_topological_floor_observed_residual_near_zero"
    elif abs(float(best.get("sigma_frac", 0.0))) >= SIGMA_FRAC_BOX - 1e-12:
        stop_reason = "numerical_convergence_inside_topological_sector_sigma_box_active"
        stopping_gate = None
        floor_status = "no_topological_floor_observed_computational_or_box_limit"
    else:
        stop_reason = "numerical_convergence_inside_topological_sector"
        stopping_gate = None
        floor_status = "no_topological_floor_observed_computational_or_resolution_limit"

    if stopping_gate is None:
        floor_status_note = (
            "Hard gates (N_gen=3, ⋆Ψ=Ψ, n_η=(3,8,15)) did not reject any "
            "continuous step. No topological residual floor was encountered "
            "at grid=48, N_h=48. Remaining residual is a computational / "
            "limited-σ / finite-basis limit, not a gate. Continuum r→0 stays Open."
        )
    else:
        floor_status_note = (
            f"Progress was stopped by topological gate {stopping_gate}."
        )

    iter_traj: List[Dict[str, Any]] = [
        p
        for p in slice_map.trajectory
        if p.get("accepted")
        and p.get("kind") in {"start", "armijo", "iteration", "final"}
    ]

    summary = {
        "grid_n": GRID_N,
        "n_harmonics": N_HARMONICS,
        "n_basis_modes": n,
        "fd_step": FD_H,
        "start_residual_at_new_resolution": float(r_start),
        "official_residual_lock": LOCKED_R,
        "official_residual_not_replaced": True,
        "lowest_accepted_residual": lowest,
        "max_reduction_inside_sector": reduction,
        "previous_24_mode_floor": FLOOR_24,
        "lowest_minus_24_mode_floor": vs_24,
        "went_below_24_mode_floor": bool(lowest < FLOOR_24 - 1e-12),
        "distance_coeffs_at_best": float(best.get("distance_coeffs", 0.0)),
        "sigma_at_best": float(best.get("sigma", LOCKED_SIGMA)),
        "sigma_frac_at_best": float(best.get("sigma_frac", 0.0)),
        "n_gen_at_best": int(best.get("n_gen", 3)),
        "stop_reason": stop_reason,
        "gate_that_stopped_progress": stopping_gate,
        "closest_gate_on_accepted_path": g0["closest_gate"],
        "gates_rejected_any_step": slice_map.n_rejected > 0,
        "n_rejected_gate_failures": slice_map.n_rejected,
        "n_objective_evals": slice_map.n_eval,
        "n_recorded_accepted_iterates": len(iter_traj),
        "topological_floor_status": floor_status,
        "topological_floor_note": floor_status_note,
        "continuous_knobs": 0,
        "new_residual_promoted": False,
        "continuum_r_to_0": "open",
    }

    payload = {
        "banner": BANNER,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "official_lock_unchanged": True,
        "official_beta_residual": LOCKED_R,
        "official_beta_residual_full": LOCKED_R_FULL,
        "new_residual_promoted": False,
        "open_gaps_remain_open": True,
        "absolute_scale_posture": "observational_conversion_only",
        "grid_n": GRID_N,
        "n_harmonics": N_HARMONICS,
        "n_basis_modes": n,
        "sigma_box": f"±{100 * SIGMA_FRAC_BOX:.0f}% around locked σ*",
        "locked_snapshot": snap,
        "start_gates": {
            "passed": True,
            "closest_gate": g0["closest_gate"],
            "n_gen": 3,
            "n_eta": list(LOCKED_N_ETA),
        },
        "phase_A_harmonics_only": slim_phase(phase_a),
        "phase_B_harmonics_plus_limited_sigma": slim_phase(phase_b),
        "minimization_summary": summary,
        "accepted_trajectory": iter_traj,
        "locked_core": {
            "n_gen": 3,
            "sigma_star": LOCKED_SIGMA,
            "lambda_tilde": [4.5, 12.0, 22.5],
            "beta_residual_official": LOCKED_R,
            "continuous_knobs": 0,
        },
    }

    plot_trajectory(payload)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    extra = [
        "",
        "HIGHER-RESOLUTION GATED MINIMIZATION (diagnostic; official lock unchanged)",
        f"timestamp_utc: {payload['timestamp_utc']}",
        "continuous_knobs: 0",
        "verification: 8/8 PASS (not re-run; locked core untouched)",
        f"grid_n: {GRID_N}",
        f"n_harmonics: {N_HARMONICS}",
        f"n_basis_modes: {n}",
        f"start_residual_at_new_resolution: {r_start}",
        f"official_beta_residual_lock: {LOCKED_R} (NOT replaced)",
        f"lowest_accepted_residual: {lowest} (NOT promoted)",
        f"previous_24_mode_floor: {FLOOR_24}",
        f"lowest_minus_24_mode_floor: {vs_24}",
        f"stop_reason: {stop_reason}",
        f"gate_that_stopped_progress: {stopping_gate}",
        f"topological_floor_status: {floor_status}",
        f"n_rejected_gate_failures: {slice_map.n_rejected}",
        f"phase_A_nit: {phase_a['nit']} residual={phase_a['final_residual']}",
        f"phase_B_nit: {phase_b['nit']} residual={phase_b['final_residual']} sigma={phase_b['final_sigma']}",
        "new_residual_promoted: False",
        "open_gaps_remain_open: True (continuum r→0 still Open)",
        "absolute_scale_posture: observational conversion only",
        "END HIGHER-RESOLUTION GATED MINIMIZATION",
        "",
    ]
    with open(LOG_PATH, encoding="utf-8") as f:
        log_text = f.read()
    marker = "HIGHER-RESOLUTION GATED MINIMIZATION (diagnostic"
    if marker in log_text:
        log_text = log_text[: log_text.index(marker)].rstrip() + "\n"
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(log_text)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(extra))

    print(f"{'Quantity':<52} {'Value'}")
    print("-" * 96)
    rows = [
        ("Resolution", f"grid={GRID_N}, N_h={N_HARMONICS}, n_modes={n}"),
        ("Start residual at this resolution", f"{r_start:.16f}"),
        ("Official residual lock (not replaced)", f"{LOCKED_R}"),
        ("Lowest accepted residual", f"{lowest:.16f} (not promoted)"),
        ("Previous 24-mode floor", f"{FLOOR_24:.16f}"),
        ("Δ vs 24-mode floor (hires − 24)", f"{vs_24:+.16f}"),
        ("Below 24-mode floor?", str(lowest < FLOOR_24 - 1e-12)),
        ("Gate that stopped progress", str(stopping_gate)),
        ("Topological floor status", floor_status),
        ("Stop reason", stop_reason),
        ("Gate rejections", str(slice_map.n_rejected)),
        ("continuous_knobs", "0"),
        ("New residual promoted", "False"),
        ("Continuum r→0", "Open"),
    ]
    for k, v in rows:
        print(f"{k:<52} {v}")
    print()
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_PNG}")
    print(f"Appended {LOG_PATH}")
    print("continuous_knobs = 0")
    print(BANNER)


if __name__ == "__main__":
    main()
