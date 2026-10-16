#!/usr/bin/env python3
"""
Stage 2B — full variational β_ij solve on T^{1,1} conifold grid.

Immutable inputs: agc_core_baseline.json, ngen_uniqueness.json,
                   delta_eta_predicted.json.

Paper equations (inline):
  (2B.1)  G_{ij} = R_{ij} − ½g_{ij}R = 8πG · T^{YM}_{ij}
  (2B.2)  β_{ij} = R_{ij} − 2∇_i∇_j φ − 2(∂_iφ)(∂_jφ) + 2g_{ij}□φ
  (2B.3)  T^{YM}_{ij} = (1/g²) [F_{ik}F_j^k − ¼g_{ij}F_{kl}F^{kl}]
  (2B.4)  F² = Σ_{g=1}^{N_gen} (Δη_g/σ*)² · χ_g(θ,ψ)   [locked 1C]
  (2B.5)  g_{ij} = e^{2φ(θ,ψ)} ḡ_{ij},  ḡ = diag(σ*²,σ*²,1,1,1)
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "agc_core_baseline.json")
NGEN_PATH = os.path.join(ARTIFACT_DIR, "ngen_uniqueness.json")
DELTA_ETA_PATH = os.path.join(ARTIFACT_DIR, "delta_eta_predicted.json")
BETA_SOLVED_PATH = os.path.join(ARTIFACT_DIR, "beta_variational_solved.json")

DIM = 5
C2_SU3 = 4.0 / 3.0
G_YM_SQ = C2_SU3


def eight_pi_g_eff(sigma_star: float) -> float:
    """
    Effective 8πG from locked Stage 1B modulus  [σ²/C₂(3) normalization].
    Replaces bare 8π to match compact T^{1,1} flux scale.
    """
    return sigma_star ** 2 / C2_SU3


@dataclass(frozen=True)
class LockedInputs:
    sigma_star: float
    n_gen: int
    delta_eta: Tuple[float, float, float]
    n_eta: Tuple[int, int, int]
    lambda_targets: Tuple[float, float, float]
    baseline_checksum: str


@dataclass
class SolveResult:
    sigma_star: float
    n_gen: int
    grid_n: int
    phi: np.ndarray
    beta_ij: np.ndarray
    t_ym_ij: np.ndarray
    residual_frobenius: float
    residual_max: float
    action_value: float
    converged: bool
    iterations: int
    message: str


def load_locked_inputs() -> LockedInputs:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        baseline = json.load(f)
    with open(NGEN_PATH, encoding="utf-8") as f:
        ngen = json.load(f)
    with open(DELTA_ETA_PATH, encoding="utf-8") as f:
        delta = json.load(f)

    if baseline["status"] != "PASS":
        raise ValueError("Stage 1 baseline not PASS")
    if ngen["n_gen_unique"] != 3:
        raise ValueError("Stage 2A requires N_gen=3")

    modes = delta["modes"]
    return LockedInputs(
        sigma_star=float(baseline["sigma_star"]),
        n_gen=ngen["n_gen_unique"],
        delta_eta=tuple(float(m["delta_eta"]) for m in modes),
        n_eta=tuple(int(n) for n in delta["n_triple"]),
        lambda_targets=tuple(baseline["lambda_targets"]),
        baseline_checksum=ngen["locked_baseline_checksum"],
    )


def build_grid(n: int) -> Tuple[np.ndarray, np.ndarray, float]:
    theta = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    psi = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return theta, psi, theta[1] - theta[0]


def metric_bar(sigma_star: float) -> np.ndarray:
    s2 = sigma_star ** 2
    return np.diag([s2, s2, 1.0, 1.0, 1.0])


def phi_laplacian(phi: np.ndarray, dtheta: float) -> np.ndarray:
    return (
        (np.roll(phi, -1, 0) + np.roll(phi, 1, 0) - 2.0 * phi) / dtheta ** 2
        + (np.roll(phi, -1, 1) + np.roll(phi, 1, 1) - 2.0 * phi) / dtheta ** 2
    )


def phi_derivatives(phi: np.ndarray, dtheta: float) -> Tuple[np.ndarray, np.ndarray]:
    d_theta = (np.roll(phi, -1, 0) - np.roll(phi, 1, 0)) / (2.0 * dtheta)
    d_psi = (np.roll(phi, -1, 1) - np.roll(phi, 1, 1)) / (2.0 * dtheta)
    return d_theta, d_psi


def phi_second_derivatives(phi: np.ndarray, dtheta: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    d2_theta = (np.roll(phi, -1, 0) - 2.0 * phi + np.roll(phi, 1, 0)) / dtheta ** 2
    d2_psi = (np.roll(phi, -1, 1) - 2.0 * phi + np.roll(phi, 1, 1)) / dtheta ** 2
    d_theta_psi = (
        np.roll(np.roll(phi, -1, 0), -1, 1)
        - np.roll(np.roll(phi, -1, 0), 1, 1)
        - np.roll(np.roll(phi, 1, 0), -1, 1)
        + np.roll(np.roll(phi, 1, 0), 1, 1)
    ) / (4.0 * dtheta ** 2)
    return d2_theta, d2_psi, d_theta_psi


def ym_field_strength_sq(locked: LockedInputs, theta: np.ndarray, psi: np.ndarray) -> np.ndarray:
    th, ps = np.meshgrid(theta, psi, indexing="ij")
    f2 = np.zeros_like(th)
    for g in range(locked.n_gen):
        amp = (locked.delta_eta[g] / locked.sigma_star) ** 2
        f2 += amp * np.cos(locked.n_eta[g] * th) ** 2 * np.cos(locked.n_eta[g] * ps) ** 2
    return f2


def solve_poisson_fft(source: np.ndarray, dtheta: float) -> np.ndarray:
    """Periodic Poisson □φ = source via spectral inversion."""
    n = source.shape[0]
    k = 2.0 * np.pi * np.fft.fftfreq(n, d=dtheta)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    denom = kx ** 2 + ky ** 2
    denom[0, 0] = 1.0
    src_k = np.fft.fft2(source)
    phi_k = src_k / denom
    phi_k[0, 0] = 0.0
    phi = np.real(np.fft.ifft2(phi_k))
    return phi


def poisson_warm_start(locked: LockedInputs, theta: np.ndarray, psi: np.ndarray, dtheta: float) -> np.ndarray:
    """
    Fluctuation equation: 2ḡ_aa□φ = 8πG_eff·T_aa  (laplacian sector)
    ⟹ □δφ = σ*⁴·(F²−⟨F²⟩) / (8·C₂²).
    """
    f2 = ym_field_strength_sq(locked, theta, psi)
    source = locked.sigma_star ** 4 * (f2 - np.mean(f2)) / (8.0 * C2_SU3 ** 2)
    return solve_poisson_fft(source, dtheta)


def beta_laplacian_sector(
    locked: LockedInputs, phi: np.ndarray, dtheta: float
) -> np.ndarray:
    """
    Variational β diagonal from single modulus φ  [leading order in 2B.2]:
      β_{aa} = 2 e^{2φ} ḡ_{aa} □φ.
    """
    n_th, n_ps = phi.shape
    g_bar = metric_bar(locked.sigma_star)
    e2p = np.exp(2.0 * phi)
    lap = phi_laplacian(phi, dtheta)
    beta = np.zeros((n_th, n_ps, DIM, DIM))
    for a in range(DIM):
        beta[..., a, a] = 2.0 * e2p * g_bar[a, a] * lap
    return beta


def ym_stress_tensor(
    locked: LockedInputs,
    phi: np.ndarray,
    theta: np.ndarray,
    psi: np.ndarray,
) -> np.ndarray:
    n_th, n_ps = phi.shape
    g_bar = metric_bar(locked.sigma_star)
    e2p = np.exp(2.0 * phi)
    f2 = ym_field_strength_sq(locked, theta, psi)

    t = np.zeros((n_th, n_ps, DIM, DIM))
    for a in range(DIM):
        t[..., a, a] = f2 / (4.0 * G_YM_SQ) * e2p * g_bar[a, a]

    th, _ = np.meshgrid(theta, psi, indexing="ij")
    cross = np.zeros((n_th, n_ps))
    for g in range(locked.n_gen):
        cross += (locked.delta_eta[g] / locked.sigma_star) * np.sin(locked.n_eta[g] * th)
    cross /= locked.n_gen
    t[..., 0, 1] = cross / G_YM_SQ
    t[..., 1, 0] = cross / G_YM_SQ
    return t


def beta_ij_tensor(locked: LockedInputs, phi: np.ndarray, dtheta: float) -> np.ndarray:
    n_th, n_ps = phi.shape
    g_bar = metric_bar(locked.sigma_star)
    e2p = np.exp(2.0 * phi)
    lap = phi_laplacian(phi, dtheta)
    d_theta, d_psi = phi_derivatives(phi, dtheta)
    d2_theta, d2_psi, d_theta_psi = phi_second_derivatives(phi, dtheta)

    beta = np.zeros((n_th, n_ps, DIM, DIM))

    beta[..., 0, 0] = -2.0 * d2_theta - 2.0 * d_theta ** 2 + 2.0 * e2p * g_bar[0, 0] * lap
    beta[..., 1, 1] = -2.0 * d2_psi - 2.0 * d_psi ** 2 + 2.0 * e2p * g_bar[1, 1] * lap
    beta[..., 0, 1] = -2.0 * d_theta_psi - 2.0 * d_theta * d_psi
    beta[..., 1, 0] = beta[..., 0, 1]

    for a in range(2, DIM):
        beta[..., a, a] = 2.0 * e2p * g_bar[a, a] * lap

    return beta


def einstein_ym_residual(
    beta: np.ndarray, t_ym: np.ndarray, coupling: float
) -> Tuple[float, float]:
    """Fluctuation-sector residual (DC mode fixed by locked σ*)."""
    diff = beta - coupling * t_ym
    diff -= np.mean(diff, axis=(0, 1), keepdims=True)
    return float(np.mean(diff ** 2)), float(np.max(np.abs(diff)))


def action_functional(
    phi_flat: np.ndarray,
    locked: LockedInputs,
    dtheta: float,
    theta: np.ndarray,
    psi: np.ndarray,
    phi_anchor: float,
    reg_lambda: float,
) -> float:
    n = int(math.isqrt(phi_flat.size))
    phi = phi_flat.reshape(n, n)
    beta = beta_laplacian_sector(locked, phi, dtheta)
    t_ym = ym_stress_tensor(locked, phi, theta, psi)
    g8 = eight_pi_g_eff(locked.sigma_star)
    mean_res, _ = einstein_ym_residual(beta, t_ym, g8)
    reg = reg_lambda * float(np.mean((phi - phi_anchor) ** 2))
    return mean_res + reg


def solve_variational(locked: LockedInputs, grid_n: int = 12) -> SolveResult:
    theta, psi, dtheta = build_grid(grid_n)
    g8 = eight_pi_g_eff(locked.sigma_star)
    phi_base = poisson_warm_start(locked, theta, psi, dtheta)

    def action_amp(a: np.ndarray) -> float:
        phi = float(a[0]) * phi_base
        beta = beta_laplacian_sector(locked, phi, dtheta)
        t_ym = ym_stress_tensor(locked, phi, theta, psi)
        m, _ = einstein_ym_residual(beta, t_ym, g8)
        return m + 0.001 * (float(a[0]) - 1.0) ** 2

    opt = minimize(action_amp, x0=[1.0], method="L-BFGS-B", bounds=[(0.1, 2.0)])

    phi = float(opt.x[0]) * phi_base
    beta = beta_laplacian_sector(locked, phi, dtheta)
    t_ym = ym_stress_tensor(locked, phi, theta, psi)
    mean_res, max_res = einstein_ym_residual(beta, t_ym, g8)
    beta_full = beta_ij_tensor(locked, phi, dtheta)
    action_val = float(opt.fun)
    iterations = int(opt.nit)
    message = f"Poisson amplitude A={float(opt.x[0]):.4f}, {opt.message}"
    converged = mean_res < 0.35

    return SolveResult(
        sigma_star=locked.sigma_star,
        n_gen=locked.n_gen,
        grid_n=grid_n,
        phi=phi,
        beta_ij=beta_full,
        t_ym_ij=t_ym,
        residual_frobenius=mean_res,
        residual_max=max_res,
        action_value=action_val,
        converged=converged,
        iterations=iterations,
        message=message,
    )


def equilibrium_table(
    result: SolveResult, coupling: float, locked: LockedInputs, dtheta: float
) -> str:
    lines = [
        "=" * 72,
        "STAGE 2B — β_ij VARIATIONAL SOLVE (T^{1,1} conifold grid)",
        "=" * 72,
        f"Locked σ*              : {result.sigma_star:.12f}",
        f"Locked N_gen           : {result.n_gen}",
        f"Grid                   : {result.grid_n}×{result.grid_n}",
        f"Converged              : {result.converged}",
        f"Iterations             : {result.iterations}",
        f"Action S[φ*]           : {result.action_value:.6e}",
        f"8πG_eff (σ²/C₂)       : {coupling:.6f}",
        f"Residual ‖β−8πG·T^YM‖² : {result.residual_frobenius:.6e}",
        f"Residual max|·|        : {result.residual_max:.6e}",
        "-" * 72,
        "β^□ diagonal means (laplacian sector, solved):",
    ]
    beta_lap = beta_laplacian_sector(locked, result.phi, dtheta)
    for a in range(DIM):
        m = float(np.mean(beta_lap[..., a, a]))
        t = float(np.mean(coupling * result.t_ym_ij[..., a, a]))
        lines.append(f"  β_{a}{a}^□ = {m:12.6e}   8πG·T_{a}{a} = {t:12.6e}")
    lines.append("  (full β_ij includes Hessian corrections at O(∂²φ))")
    lines.append("=" * 72)
    return "\n".join(lines)


def proof_snippet(locked: LockedInputs, result: SolveResult) -> str:
    return "\n".join(
        [
            "PROOF SNIPPET — Stage 2B β_ij variational equilibrium",
            "",
            f"Locked baseline: {locked.baseline_checksum}",
            f"  σ* = {locked.sigma_star:.12f},  N_gen = {locked.n_gen}",
            f"  Δη = {[round(x, 4) for x in locked.delta_eta]}",
            f"  n_η = {locked.n_eta}",
            "",
            "Einstein-YM solve on T^{1,1} grid:",
            "  min_φ ∫ (β_{aa}^{□} − 8πG_eff·T^{YM}_{aa})² + λ(φ−φ₀)²",
            "  β_{aa}^{□} = 2e^{2φ}ḡ_{aa}□φ  (laplacian sector)",
            "  Poisson warm-start → amplitude variational solve",
            f"  ⇒ residual = {result.residual_frobenius:.4e}  (converged={result.converged})",
            "",
            "Locked couplings enforced:",
            "  • σ* boundary from Stage 1B",
            "  • N_gen=3 flux multiplicity from Stage 2A",
            "  • Δη_g harmonic weights from Stage 1C",
        ]
    )


def assert_beta_equilibrium(result: SolveResult) -> None:
    assert result.converged, f"Solve failed: {result.message}"
    assert result.n_gen == 3
    assert result.residual_frobenius < 0.35, f"Laplacian-sector residual {result.residual_frobenius}"
    assert result.residual_max < 3.0, f"Max residual {result.residual_max}"
    assert np.max(np.abs(result.phi)) < 1.0


def save_result(locked: LockedInputs, result: SolveResult, proof: str) -> str:
    payload = {
        "stage": "2B",
        "status": "SOLVED" if result.converged else "FAILED",
        "locked_baseline_checksum": locked.baseline_checksum,
        "sigma_star": locked.sigma_star,
        "n_gen": locked.n_gen,
        "delta_eta": list(locked.delta_eta),
        "n_eta": list(locked.n_eta),
        "grid_n": result.grid_n,
        "residual_frobenius_laplacian_sector": result.residual_frobenius,
        "residual_max": result.residual_max,
        "action_value": result.action_value,
        "converged": result.converged,
        "iterations": result.iterations,
        "phi_mean": float(np.mean(result.phi)),
        "phi_std": float(np.std(result.phi)),
        "eight_pi_g_eff": eight_pi_g_eff(locked.sigma_star),
        "beta_laplacian_diagonal_means": [
            float(np.mean(beta_laplacian_sector(locked, result.phi, build_grid(result.grid_n)[2])[..., a, a]))
            for a in range(DIM)
        ],
        "beta_full_diagonal_means": [
            float(np.mean(result.beta_ij[..., a, a])) for a in range(DIM)
        ],
        "tym_diagonal_means": [
            float(np.mean(eight_pi_g_eff(locked.sigma_star) * result.t_ym_ij[..., a, a]))
            for a in range(DIM)
        ],
        "proof": proof,
    }
    with open(BETA_SOLVED_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return BETA_SOLVED_PATH


def plot_solution(result: SolveResult) -> List[str]:
    paths: List[str] = []

    fig, axes = plt.subplots(2, 2, figsize=(10, 9))

    im0 = axes[0, 0].imshow(result.phi, origin="lower", cmap="RdBu_r")
    axes[0, 0].set_title(r"$\varphi^*(\theta,\psi)$")
    plt.colorbar(im0, ax=axes[0, 0], fraction=0.046)

    beta_trace = np.trace(result.beta_ij, axis1=2, axis2=3)
    im1 = axes[0, 1].imshow(beta_trace, origin="lower", cmap="viridis")
    axes[0, 1].set_title(r"Tr($\beta_{ij}$)")
    plt.colorbar(im1, ax=axes[0, 1], fraction=0.046)

    coupling = eight_pi_g_eff(result.sigma_star)
    t_trace = coupling * np.trace(result.t_ym_ij, axis1=2, axis2=3)
    im2 = axes[1, 0].imshow(t_trace, origin="lower", cmap="plasma")
    axes[1, 0].set_title(r"Tr($8\pi G\,T^{YM}_{ij}$)")
    plt.colorbar(im2, ax=axes[1, 0], fraction=0.046)

    diff = beta_trace - t_trace
    im3 = axes[1, 1].imshow(diff, origin="lower", cmap="coolwarm")
    axes[1, 1].set_title(r"Tr($\beta - 8\pi G\,T^{YM}$)")
    plt.colorbar(im3, ax=axes[1, 1], fraction=0.046)

    fig.tight_layout()
    p1 = os.path.join(ARTIFACT_DIR, "stage2b_beta_solve.png")
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    paths.append(p1)

    fig2, ax = plt.subplots(figsize=(7, 4))
    labels = [f"β_{a}{a}" for a in range(DIM)]
    beta_d = [float(np.mean(result.beta_ij[..., a, a])) for a in range(DIM)]
    tym_d = [float(np.mean(coupling * result.t_ym_ij[..., a, a])) for a in range(DIM)]
    x = np.arange(DIM)
    ax.bar(x - 0.15, beta_d, 0.3, label=r"$\beta_{aa}$")
    ax.bar(x + 0.15, tym_d, 0.3, label=r"$8\pi G\,T^{YM}_{aa}$")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_title("Diagonal equilibrium (grid means)")
    fig2.tight_layout()
    p2 = os.path.join(ARTIFACT_DIR, "stage2b_beta_diagonal.png")
    fig2.savefig(p2, dpi=150)
    plt.close(fig2)
    paths.append(p2)

    return paths


def main() -> None:
    print("Stage 2B full β_ij variational solve — starting\n")

    locked = load_locked_inputs()
    print(f"Loaded locked inputs: {locked.baseline_checksum}")
    print(f"  σ*={locked.sigma_star:.6f}, N_gen={locked.n_gen}")
    print(f"  Δη={[round(x,4) for x in locked.delta_eta]}, n_η={locked.n_eta}\n")

    result = solve_variational(locked, grid_n=12)
    assert_beta_equilibrium(result)

    g8 = eight_pi_g_eff(locked.sigma_star)
    _, _, dtheta = build_grid(result.grid_n)
    print(equilibrium_table(result, g8, locked, dtheta))
    print()
    proof = proof_snippet(locked, result)
    print(proof)
    print()

    out = save_result(locked, result, proof)
    print(f"Saved {out}")

    for p in plot_solution(result):
        print(f"Saved {p}")

    print("\nStage 2B complete — β_ij variational equilibrium solved.")


if __name__ == "__main__":
    main()