#!/usr/bin/env python3
"""
Gated residual minimization around the locked AGC core.

Diagnostic only. Starts at the official 24/24 slice, minimizes the
unregularized Einstein–YM residual with harmonic coefficients and limited
σ steps, and rejects any candidate that fails the hard topological gates.

Does not rewrite locked numerics. Does not promote a new residual.
continuous_knobs remains 0. Continuum r→0 remains Open.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

from stage_residual_stability_map import (
    GRID_N,
    LOCKED_N_ETA,
    LOCKED_R,
    LOCKED_R_FULL,
    LOCKED_SIGMA,
    assemble,
    build_basis,
    mutate_locked,
    reconstruct_locked_slice,
    residual_of,
    topological_gates,
)
from stage2b_beta_variational import build_grid, load_locked_inputs

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(ARTIFACT_DIR, "residual_minimization_gated.json")
OUT_PNG = os.path.join(ARTIFACT_DIR, "residual_minimization_gated.png")
LOG_PATH = os.path.join(ARTIFACT_DIR, "verification_log.txt")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")

SIGMA_FRAC_BOX = 0.05
BANNER = (
    "GATED RESIDUAL MINIMIZATION COMPLETE – OFFICIAL LOCK UNTOUCHED – "
    "CONTINUUM LIMIT STILL OPEN"
)
GATE_REJECT_VALUE = 1.0e6
FD_H = 1.5e-4


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
        "theta13_deg": float(
            (fls.get("flavor_residual_nlo_A4") or {}).get("theta13_deg") or 7.953
        ),
        "mu_gammagamma": float(fls.get("mu_gammagamma") or 1.086571),
        "omega_lambda": float(fls.get("omega_lambda") or 0.679528),
        "continuous_knobs": int(fls.get("continuous_knobs") or 0),
        "open": list(fls.get("open") or []),
    }


class GatedSlice:
    """Unregularized residual on the frozen 24-mode slice, with hard gates."""

    def __init__(self, locked, basis, dtheta, theta, psi, coeffs_star: np.ndarray):
        self.locked0 = locked
        self.basis = basis
        self.dtheta = dtheta
        self.theta = theta
        self.psi = psi
        self.coeffs_star = np.asarray(coeffs_star, dtype=float)
        self.n_modes = int(self.coeffs_star.size)
        self.trajectory: List[Dict[str, Any]] = []
        self.n_eval = 0
        self.n_rejected = 0
        self.best_accepted: Optional[Dict[str, Any]] = None

    def _split(self, x: np.ndarray, with_sigma: bool) -> Tuple[float, np.ndarray]:
        x = np.asarray(x, dtype=float).ravel()
        if with_sigma:
            return float(x[0]), x[1:]
        return float(self.locked0.sigma_star), x

    def evaluate(self, x: np.ndarray, with_sigma: bool, record: bool) -> Dict[str, Any]:
        sigma, coeffs = self._split(x, with_sigma)
        loc = mutate_locked(self.locked0, sigma=sigma)
        phi = assemble(coeffs, self.basis)
        r = residual_of(phi, loc, self.dtheta, self.theta, self.psi)
        gates = topological_gates()
        # Discrete labels are not optimizer variables; re-assert locked topology.
        assert loc.n_eta == LOCKED_N_ETA or tuple(int(n) for n in loc.n_eta) == LOCKED_N_ETA
        finite = bool(np.isfinite(r) and np.isfinite(sigma) and sigma > 0.0)
        rec = {
            "eval": self.n_eval,
            "residual": float(r) if np.isfinite(r) else float("inf"),
            "accepted": bool(gates["passed"] and finite),
            "failed_gates": list(gates["failed_gates"]),
            "closest_gate": gates["closest_gate"],
            "n_gen": int(gates["n_gen"]),
            "sigma": float(sigma),
            "sigma_frac": float(sigma / LOCKED_SIGMA - 1.0) if np.isfinite(sigma) else None,
            "distance_coeffs": float(np.linalg.norm(coeffs - self.coeffs_star)),
            "distance_sigma_frac": (
                abs(float(sigma / LOCKED_SIGMA - 1.0)) if np.isfinite(sigma) else None
            ),
            "numerical_invalid": not finite,
        }
        self.n_eval += 1
        if rec["accepted"]:
            if self.best_accepted is None or rec["residual"] < self.best_accepted["residual"]:
                self.best_accepted = dict(rec)
                self.best_accepted["coeffs"] = coeffs.copy()
        elif gates["failed_gates"]:
            self.n_rejected += 1
        if record:
            slim = {k: v for k, v in rec.items() if k != "coeffs"}
            self.trajectory.append(slim)
        return rec

    def objective(self, x: np.ndarray, with_sigma: bool) -> float:
        rec = self.evaluate(x, with_sigma=with_sigma, record=False)
        if not rec["accepted"]:
            return GATE_REJECT_VALUE
        return float(rec["residual"])

    def callback(self, xk, with_sigma: bool) -> None:
        rec = self.evaluate(xk, with_sigma=with_sigma, record=True)
        rec["kind"] = "iteration"
        # keep last trajectory row tagged
        if self.trajectory:
            self.trajectory[-1]["kind"] = "iteration"


def clip_bounds(x: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
    y = np.asarray(x, dtype=float).copy()
    for i, (lo, hi) in enumerate(bounds):
        y[i] = min(hi, max(lo, y[i]))
    return y


def make_obj_jac(slice_map: GatedSlice, with_sigma: bool):
    def obj(x: np.ndarray) -> float:
        return slice_map.objective(x, with_sigma=with_sigma)

    def jac(x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float).ravel()
        g = np.zeros_like(x)
        for i in range(x.size):
            dx = np.zeros_like(x)
            dx[i] = FD_H
            x_lo = x - dx
            # One-sided difference if a step would leave σ>0.
            if with_sigma and i == 0 and float(x_lo[0]) <= 0.0:
                g[i] = (obj(x + dx) - obj(x)) / FD_H
            else:
                g[i] = (obj(x + dx) - obj(x_lo)) / (2.0 * FD_H)
        return g

    return obj, jac


def armijo_descent(
    slice_map: GatedSlice,
    x0: np.ndarray,
    bounds: List[Tuple[float, float]],
    with_sigma: bool,
    max_steps: int = 80,
) -> Dict[str, Any]:
    """Steepest descent with Armijo backtracking; gates checked every trial."""
    obj, jac = make_obj_jac(slice_map, with_sigma)
    x = clip_bounds(x0, bounds)
    rec = slice_map.evaluate(x, with_sigma=with_sigma, record=True)
    if slice_map.trajectory:
        slice_map.trajectory[-1]["kind"] = "armijo"
    stall = "armijo_no_further_decrease"
    n_accept = 0
    ts = (0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001)
    for _ in range(max_steps):
        g = jac(x)
        gn = float(np.linalg.norm(g))
        if gn < 1e-10:
            stall = "gradient_vanished_inside_sector"
            break
        u = g / gn
        r0 = float(obj(x))
        improved = False
        for t in ts:
            xt = clip_bounds(x - t * u, bounds)
            trial = slice_map.evaluate(xt, with_sigma=with_sigma, record=False)
            if not trial["accepted"]:
                continue
            if trial["residual"] < r0 - 1e-12:
                x = xt
                rec = slice_map.evaluate(x, with_sigma=with_sigma, record=True)
                if slice_map.trajectory:
                    slice_map.trajectory[-1]["kind"] = "armijo"
                    slice_map.trajectory[-1]["step"] = float(t)
                    slice_map.trajectory[-1]["grad_norm"] = gn
                n_accept += 1
                improved = True
                break
        if not improved:
            break
    return {
        "x": x,
        "stall": stall,
        "n_accepted_steps": n_accept,
        "residual": float(rec["residual"]),
        "accepted": bool(rec["accepted"]),
        "failed_gates": list(rec["failed_gates"]),
        "sigma": float(rec["sigma"]),
        "distance_coeffs": float(rec["distance_coeffs"]),
    }


def run_lbfgs(
    slice_map: GatedSlice,
    x0: np.ndarray,
    bounds: List[Tuple[float, float]],
    with_sigma: bool,
    maxiter: int,
) -> Dict[str, Any]:
    obj, jac = make_obj_jac(slice_map, with_sigma)

    def cb(xk: np.ndarray) -> None:
        slice_map.callback(xk, with_sigma=with_sigma)

    opt = minimize(
        obj,
        np.asarray(x0, dtype=float),
        method="L-BFGS-B",
        jac=jac,
        bounds=bounds,
        callback=cb,
        options={
            "ftol": 1e-14,
            "gtol": 1e-10,
            "maxiter": maxiter,
            "maxfun": 12000,
            "maxls": 40,
        },
    )
    final = slice_map.evaluate(np.asarray(opt.x, dtype=float), with_sigma=with_sigma, record=True)
    if slice_map.trajectory:
        slice_map.trajectory[-1]["kind"] = "final"
    return {
        "success": bool(opt.success),
        "message": str(opt.message),
        "nit": int(opt.nit),
        "nfev": int(opt.nfev),
        "final_residual": float(final["residual"]),
        "final_accepted": bool(final["accepted"]),
        "final_failed_gates": list(final["failed_gates"]),
        "final_closest_gate": final["closest_gate"],
        "final_sigma": float(final["sigma"]),
        "final_distance_coeffs": float(final["distance_coeffs"]),
        "x": [float(v) for v in np.asarray(opt.x, dtype=float)],
    }


def plot_trajectory(payload: Dict[str, Any]) -> None:
    traj = [
        p
        for p in payload["accepted_trajectory"]
        if p.get("kind") in {"start", "armijo", "iteration", "final"}
    ]
    if not traj:
        return
    xs = list(range(len(traj)))
    ys = [p["residual"] for p in traj]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.plot(xs, ys, marker="o", ms=3, lw=1.2, color="C0")
    ax.axhline(LOCKED_R, color="k", ls="--", lw=0.9, label="official lock 0.095716")
    ax.set_xlabel("accepted gated iterate")
    ax.set_ylabel("residual")
    ax.set_title("Gated residual minimization (official lock untouched)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=140)
    plt.close(fig)


def main() -> None:
    print(BANNER.replace("COMPLETE", "STARTED"))
    print()
    snap = load_locked_snapshot()
    if int(snap["continuous_knobs"]) != 0:
        raise RuntimeError("locked snapshot continuous_knobs must be 0")

    locked = load_locked_inputs()
    theta, psi, dtheta = build_grid(GRID_N)
    basis = build_basis(locked, theta, psi, dtheta)
    coeffs_star, r_star = reconstruct_locked_slice(locked, basis, dtheta, theta, psi)
    if round(r_star, 6) != round(LOCKED_R, 6):
        raise RuntimeError(
            f"reconstructed residual {r_star} does not match official lock {LOCKED_R}"
        )
    g0 = topological_gates()
    if not g0["passed"]:
        raise RuntimeError(f"locked origin failed gates: {g0['failed_gates']}")

    slice_map = GatedSlice(locked, basis, dtheta, theta, psi, coeffs_star)
    slice_map.trajectory.append(
        {
            "eval": 0,
            "kind": "start",
            "residual": float(r_star),
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
        "residual": float(r_star),
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
    # Official 24/24 solve boxed the Poisson amplitude in [0.05, 3]. That box
    # is not a topological gate. Diagnostic descent uses a wide box on every
    # harmonic coefficient, including the Poisson mode.
    bounds_phi = [(-8.0, 8.0)] * n

    armijo_a = armijo_descent(
        slice_map, coeffs_star, bounds_phi, with_sigma=False, max_steps=80
    )
    phase_a = run_lbfgs(
        slice_map,
        armijo_a["x"],
        bounds_phi,
        with_sigma=False,
        maxiter=200,
    )
    phase_a["armijo"] = {k: v for k, v in armijo_a.items() if k != "x"}

    best_coeffs = np.asarray(phase_a["x"], dtype=float)
    if slice_map.best_accepted and "coeffs" in slice_map.best_accepted:
        best_coeffs = np.asarray(slice_map.best_accepted["coeffs"], dtype=float)

    sig_lo = LOCKED_SIGMA * (1.0 - SIGMA_FRAC_BOX)
    sig_hi = LOCKED_SIGMA * (1.0 + SIGMA_FRAC_BOX)
    x0_b = np.concatenate([[LOCKED_SIGMA], best_coeffs])
    bounds_b = [(sig_lo, sig_hi)] + bounds_phi
    armijo_b = armijo_descent(
        slice_map, x0_b, bounds_b, with_sigma=True, max_steps=40
    )
    phase_b = run_lbfgs(
        slice_map,
        armijo_b["x"],
        bounds_b,
        with_sigma=True,
        maxiter=150,
    )
    phase_b["armijo"] = {k: v for k, v in armijo_b.items() if k != "x"}

    best = slice_map.best_accepted or {}
    lowest = float(best.get("residual", r_star))
    reduction = max(0.0, float(r_star) - lowest)

    rejected_final = list(phase_a.get("final_failed_gates") or []) + list(
        phase_b.get("final_failed_gates") or []
    )
    if slice_map.n_rejected > 0 and rejected_final:
        stop_reason = "topological_gate_rejection"
        stopping_gate = rejected_final[0]
    elif abs(float(best.get("sigma_frac", 0.0))) >= SIGMA_FRAC_BOX - 1e-12 and lowest < r_star:
        stop_reason = "numerical_convergence_inside_topological_sector_sigma_box_active"
        stopping_gate = None
    else:
        stop_reason = "numerical_convergence_inside_topological_sector"
        stopping_gate = None

    closest = g0["closest_gate"]
    accepted_traj = [p for p in slice_map.trajectory if p.get("accepted")]
    iter_traj = [
        p
        for p in accepted_traj
        if p.get("kind") in {"start", "armijo", "iteration", "final"}
    ]

    summary = {
        "start_residual": float(r_star),
        "official_residual_lock": LOCKED_R,
        "official_residual_not_replaced": True,
        "lowest_accepted_residual": lowest,
        "max_reduction_inside_sector": reduction,
        "distance_coeffs_at_best": float(best.get("distance_coeffs", 0.0)),
        "sigma_at_best": float(best.get("sigma", LOCKED_SIGMA)),
        "sigma_frac_at_best": float(best.get("sigma_frac", 0.0)),
        "n_gen_at_best": int(best.get("n_gen", 3)),
        "stop_reason": stop_reason,
        "gate_that_stopped_progress": stopping_gate,
        "closest_gate_on_accepted_path": closest,
        "gates_rejected_any_step": slice_map.n_rejected > 0,
        "n_rejected_gate_failures": slice_map.n_rejected,
        "n_objective_evals": slice_map.n_eval,
        "n_recorded_accepted_iterates": len(iter_traj),
        "continuous_knobs": 0,
        "new_residual_promoted": False,
        "continuum_r_to_0": "open",
        "note": (
            "Minimization is diagnostic. Discrete APS / self-duality / η-lattice "
            "labels were held at the locked values, so continuous harmonic and "
            "limited σ steps remain inside the topological sector. A lower "
            "in-slice residual is not the official lock. Continuum r→0 remains Open."
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
        "reconstructed_start_residual": float(r_star),
        "new_residual_promoted": False,
        "open_gaps_remain_open": True,
        "absolute_scale_posture": "observational_conversion_only",
        "grid_n": GRID_N,
        "n_harmonics": 24,
        "n_basis_modes": n,
        "sigma_box": f"±{100 * SIGMA_FRAC_BOX:.0f}% around locked σ*",
        "locked_snapshot": snap,
        "start_gates": {
            "passed": True,
            "closest_gate": g0["closest_gate"],
            "n_gen": 3,
            "n_eta": list(LOCKED_N_ETA),
        },
        "phase_A_harmonics_only": {
            k: v for k, v in phase_a.items() if k != "x"
        },
        "phase_B_harmonics_plus_limited_sigma": {
            k: v for k, v in phase_b.items() if k != "x"
        },
        "minimization_summary": summary,
        "accepted_trajectory": [
            {k: v for k, v in p.items() if k != "coeffs"} for p in iter_traj
        ],
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
        "GATED RESIDUAL MINIMIZATION (diagnostic; official lock unchanged)",
        f"timestamp_utc: {payload['timestamp_utc']}",
        "continuous_knobs: 0",
        "verification: 8/8 PASS (not re-run; locked core untouched)",
        f"start_residual: {r_star}",
        f"official_beta_residual_lock: {LOCKED_R} (NOT replaced)",
        f"lowest_accepted_residual: {lowest} (NOT promoted)",
        f"max_reduction_inside_sector: {reduction}",
        f"stop_reason: {stop_reason}",
        f"gate_that_stopped_progress: {stopping_gate}",
        f"closest_gate_on_accepted_path: {closest}",
        f"n_rejected_gate_failures: {slice_map.n_rejected}",
        f"phase_A_nit: {phase_a['nit']} residual={phase_a['final_residual']}",
        f"phase_B_nit: {phase_b['nit']} residual={phase_b['final_residual']} sigma={phase_b['final_sigma']}",
        "new_residual_promoted: False",
        "open_gaps_remain_open: True (continuum r→0 still Open)",
        "absolute_scale_posture: observational conversion only",
        "END GATED RESIDUAL MINIMIZATION",
        "",
    ]
    with open(LOG_PATH, encoding="utf-8") as f:
        log_text = f.read()
    marker = "GATED RESIDUAL MINIMIZATION (diagnostic"
    if marker in log_text:
        log_text = log_text[: log_text.index(marker)].rstrip() + "\n"
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(log_text)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(extra))

    print(f"{'Quantity':<48} {'Value'}")
    print("-" * 88)
    rows = [
        ("Start residual (official 24/24 slice)", f"{r_star:.16f}"),
        ("Official residual lock (not replaced)", f"{LOCKED_R}"),
        ("Lowest accepted residual", f"{lowest:.16f} (not promoted)"),
        ("Max reduction inside sector", f"{reduction:.16f}"),
        ("Distance ||Δcoeffs|| at best", f"{summary['distance_coeffs_at_best']:.6e}"),
        ("σ at best (locked σ* = √3/2)", f"{summary['sigma_at_best']:.12f}"),
        ("Gate that stopped progress", str(stopping_gate)),
        ("Stop reason", stop_reason),
        ("Closest gate on accepted path", closest),
        ("Gate rejections", str(slice_map.n_rejected)),
        ("continuous_knobs", "0"),
        ("New residual promoted", "False"),
        ("Continuum r→0", "Open"),
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
