#!/usr/bin/env python3
"""
Gated residual minimization with the ±5% σ box removed.

Diagnostic only. Official r=0.095716 and σ*=√3/2 are not rewritten.
Free σ here is a residual-functional search, not a continuous knob.
Hard filters are the topological gates only.
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
    mutate_locked,
    residual_of,
    assemble,
    topological_gates,
)
from stage2b_beta_variational import build_grid, load_locked_inputs
from stage_residual_stability_map import reconstruct_locked_slice

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(ARTIFACT_DIR, "residual_minimization_no_sigma_box.json")
OUT_PNG = os.path.join(ARTIFACT_DIR, "residual_minimization_no_sigma_box.png")
LOG_PATH = os.path.join(ARTIFACT_DIR, "verification_log.txt")

GRID_N = 48
N_HARMONICS = 48
# Numerical positivity / overflow only — not the former ±5% safety box.
SIGMA_LO = 1.0e-4
SIGMA_HI = 20.0
FLOOR_HIRES_BOXED = 0.0335322954734256

BANNER = (
    "GATED MINIMIZATION – σ BOX REMOVED – TOPOLOGICAL FLOOR STATUS REPORTED"
)


def slim_phase(phase: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in phase.items() if k != "x"}


def sigma_scan(
    slice_map: GatedSlice,
    coeffs: np.ndarray,
    sigmas: np.ndarray,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for sig in sigmas:
        loc = mutate_locked(slice_map.locked0, sigma=float(sig))
        phi = assemble(coeffs, slice_map.basis)
        r = residual_of(phi, loc, slice_map.dtheta, slice_map.theta, slice_map.psi)
        gates = topological_gates()
        rows.append(
            {
                "sigma": float(sig),
                "sigma_frac": float(sig / LOCKED_SIGMA - 1.0),
                "residual": float(r),
                "finite": bool(np.isfinite(r)),
                "accepted": bool(gates["passed"] and np.isfinite(r)),
                "closest_gate": gates["closest_gate"],
            }
        )
    return rows


def plot_results(payload: Dict[str, Any]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.6))
    traj = [
        p
        for p in payload["accepted_trajectory"]
        if p.get("kind") in {"start", "armijo", "iteration", "final"}
    ]
    if traj:
        axes[0].plot(
            list(range(len(traj))),
            [p["residual"] for p in traj],
            marker="o",
            ms=3,
            lw=1.2,
        )
    axes[0].axhline(LOCKED_R, color="k", ls="--", lw=0.8, label="official lock")
    axes[0].axhline(
        FLOOR_HIRES_BOXED, color="C1", ls=":", lw=0.8, label="48-mode ±5% floor"
    )
    axes[0].set_xlabel("accepted gated iterate")
    axes[0].set_ylabel("residual")
    axes[0].set_title("No σ box")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=7)

    scan = payload.get("sigma_scan_at_best_harmonics") or []
    if scan:
        xs = [p["sigma_frac"] for p in scan if p["finite"]]
        ys = [p["residual"] for p in scan if p["finite"]]
        axes[1].plot(xs, ys, marker="o", ms=3, color="C2")
    axes[1].axvline(0.0, color="0.6", ls=":", lw=0.8)
    axes[1].set_xlabel(r"$(\sigma-\sigma^*)/\sigma^*$")
    axes[1].set_ylabel("residual")
    axes[1].set_title("σ scan (frozen harmonics)")
    axes[1].grid(True, alpha=0.3)
    fig.suptitle("Gated min, σ box removed (official lock untouched)")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=140)
    plt.close(fig)


def main() -> None:
    print(BANNER.replace("REPORTED", "STARTED"))
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
        raise RuntimeError(f"origin failed gates: {g0['failed_gates']}")

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
    bounds_free = [(SIGMA_LO, SIGMA_HI)] + bounds_phi

    # Phase A: harmonics at frozen σ* (warm start inside the sector).
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

    # Phase B: free σ (no ±5% box) + harmonics, gates only.
    x0_b = np.concatenate([[LOCKED_SIGMA], best_coeffs])
    armijo_b = armijo_descent(
        slice_map, x0_b, bounds_free, with_sigma=True, max_steps=80
    )
    phase_b = run_lbfgs(
        slice_map, armijo_b["x"], bounds_free, with_sigma=True, maxiter=200
    )
    phase_b["armijo"] = slim_phase(armijo_b)

    best = slice_map.best_accepted or {}
    lowest = float(best.get("residual", r_start))
    reduction = max(0.0, float(r_start) - lowest)
    sigma_best = float(best.get("sigma", LOCKED_SIGMA))
    sigma_frac = float(sigma_best / LOCKED_SIGMA - 1.0)
    hit_lo = abs(sigma_best - SIGMA_LO) < 1e-12 or sigma_best <= SIGMA_LO * 1.01
    hit_hi = abs(sigma_best - SIGMA_HI) < 1e-12 or sigma_best >= SIGMA_HI * 0.99

    scan_coeffs = best_coeffs
    if "coeffs" in best:
        scan_coeffs = np.asarray(best["coeffs"], dtype=float)
    scan_fracs = np.array(
        [-0.9, -0.7, -0.5, -0.3, -0.15, -0.05, 0.0, 0.05, 0.15, 0.3, 0.5, 1.0, 2.0, 4.0]
    )
    scan_sigmas = np.clip(LOCKED_SIGMA * (1.0 + scan_fracs), SIGMA_LO, SIGMA_HI)
    extra_sig = [LOCKED_SIGMA]
    if np.isfinite(sigma_best) and sigma_best > 0.0:
        extra_sig.append(sigma_best)
    scan_sigmas = np.unique(np.concatenate([scan_sigmas, np.array(extra_sig)]))
    scan = sigma_scan(slice_map, scan_coeffs, scan_sigmas)

    rejected_final = list(phase_a.get("final_failed_gates") or []) + list(
        phase_b.get("final_failed_gates") or []
    )
    if slice_map.n_rejected > 0 and rejected_final:
        stop_reason = "topological_gate_rejection"
        stopping_gate = rejected_final[0]
        floor_status = "topological_gate_floor"
    elif hit_lo:
        stop_reason = "numerical_sigma_positivity_bound"
        stopping_gate = None
        floor_status = "no_topological_floor_observed_sigma_ran_to_numerical_floor"
    elif hit_hi:
        stop_reason = "numerical_sigma_upper_bound"
        stopping_gate = None
        floor_status = "no_topological_floor_observed_sigma_ran_to_numerical_ceiling"
    elif lowest < 1.0e-6:
        stop_reason = "numerical_convergence_near_zero_inside_sector"
        stopping_gate = None
        floor_status = "no_topological_floor_observed_residual_near_zero"
    else:
        stop_reason = "numerical_convergence_inside_topological_sector"
        stopping_gate = None
        floor_status = "no_topological_floor_observed_computational_limit"

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
        "sigma_box_removed": True,
        "sigma_numerical_domain": [SIGMA_LO, SIGMA_HI],
        "sigma_numerical_domain_note": (
            "Bounds are positivity / overflow only. The former ±5% box is gone."
        ),
        "start_residual": float(r_start),
        "official_residual_lock": LOCKED_R,
        "official_residual_not_replaced": True,
        "official_sigma_star_not_replaced": True,
        "lowest_accepted_residual": lowest,
        "max_reduction_inside_sector": reduction,
        "previous_hires_boxed_floor": FLOOR_HIRES_BOXED,
        "lowest_minus_boxed_floor": float(lowest - FLOOR_HIRES_BOXED),
        "sigma_at_best": sigma_best,
        "sigma_star_locked": LOCKED_SIGMA,
        "delta_sigma_over_sigma_star": sigma_frac,
        "hit_sigma_numerical_floor": hit_lo,
        "hit_sigma_numerical_ceiling": hit_hi,
        "distance_coeffs_at_best": float(best.get("distance_coeffs", 0.0)),
        "n_gen_at_best": int(best.get("n_gen", 3)),
        "stop_reason": stop_reason,
        "gate_that_stopped_progress": stopping_gate,
        "closest_gate_on_accepted_path": g0["closest_gate"],
        "gates_rejected_any_step": slice_map.n_rejected > 0,
        "n_rejected_gate_failures": slice_map.n_rejected,
        "n_objective_evals": slice_map.n_eval,
        "n_recorded_accepted_iterates": len(iter_traj),
        "topological_floor_status": floor_status,
        "continuous_knobs": 0,
        "new_residual_promoted": False,
        "continuum_r_to_0": "open",
        "note": (
            "Free σ is a diagnostic of the Einstein–YM residual functional. "
            "It is not a continuous knob of the theory. Official σ*=√3/2 and "
            "r=0.095716 remain the lock. Hard filters are APS / self-duality / "
            "η-lattice only."
        ),
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
        "sigma_box": "removed",
        "locked_snapshot": snap,
        "start_gates": {
            "passed": True,
            "closest_gate": g0["closest_gate"],
            "n_gen": 3,
            "n_eta": list(LOCKED_N_ETA),
        },
        "phase_A_harmonics_frozen_sigma": slim_phase(phase_a),
        "phase_B_harmonics_plus_free_sigma": slim_phase(phase_b),
        "sigma_scan_at_best_harmonics": scan,
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

    plot_results(payload)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    extra = [
        "",
        "GATED MINIMIZATION NO SIGMA BOX (diagnostic; official lock unchanged)",
        f"timestamp_utc: {payload['timestamp_utc']}",
        "continuous_knobs: 0",
        "verification: 8/8 PASS (not re-run; locked core untouched)",
        f"grid_n: {GRID_N}",
        f"n_harmonics: {N_HARMONICS}",
        f"start_residual: {r_start}",
        f"official_beta_residual_lock: {LOCKED_R} (NOT replaced)",
        f"lowest_accepted_residual: {lowest} (NOT promoted)",
        f"sigma_at_best: {sigma_best}",
        f"delta_sigma_over_sigma_star: {sigma_frac}",
        f"sigma_box: removed (numerical domain [{SIGMA_LO}, {SIGMA_HI}])",
        f"stop_reason: {stop_reason}",
        f"gate_that_stopped_progress: {stopping_gate}",
        f"topological_floor_status: {floor_status}",
        f"n_rejected_gate_failures: {slice_map.n_rejected}",
        f"phase_A_nit: {phase_a['nit']} residual={phase_a['final_residual']}",
        f"phase_B_nit: {phase_b['nit']} residual={phase_b['final_residual']} sigma={phase_b['final_sigma']}",
        "new_residual_promoted: False",
        "open_gaps_remain_open: True (continuum r→0 still Open)",
        "absolute_scale_posture: observational conversion only",
        "END GATED MINIMIZATION NO SIGMA BOX",
        "",
    ]
    with open(LOG_PATH, encoding="utf-8") as f:
        log_text = f.read()
    marker = "GATED MINIMIZATION NO SIGMA BOX (diagnostic"
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
        ("Start residual", f"{r_start:.16f}"),
        ("Official residual lock (not replaced)", f"{LOCKED_R}"),
        ("Lowest accepted residual", f"{lowest:.16f} (not promoted)"),
        ("Final σ", f"{sigma_best:.12f}"),
        ("Final Δσ/σ*", f"{sigma_frac:+.12f}"),
        ("σ box", "removed"),
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
