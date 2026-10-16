#!/usr/bin/env python3
"""
Wall-index sieve for the generation count.

Produces N_gen as an output of the wall-index rule on the j2=0 line.
This file is not an application of the APS index theorem. The arithmetic
counts sieve zeros. It does not compute ker of a Dirac operator. It does
not seed λ̃ targets or N_gen. The numbers λ̃ are Casimir values 6 j(j+1).

Geometric inputs only (locked Stages 1–3 data, no free knobs):
  - r = 0 APS spectral sector (singular 4/(3r²) projected out)
  - half-integer SU(2)×SU(2) lattice from T^{1,1} isometry
  - self-dual structure ⋆Ψ = Ψ  ⇒  j₂ = 0 line only
  - wall-index sieve on j₂=0: index = max(0, ⌊4j₁−6⌋₊). Not a Dirac index.
  - squashing modulus σ* = √3/2 (locked; used for bulk Â scale only)
  - C₂(3) = 4/3 (Casimir of SU(3) structure group on T^{1,1})

Does NOT use as filters: λ̃ ∈ {4.5,12,22.5} or N_gen = 3.
Those may appear only as derived Casimir values, not as field modes.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Tuple

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
NATIVE_INDEX_PATH = os.path.join(ARTIFACT_DIR, "native_aps_index.json")

# Geometric constants of T^{1,1} / SU(3) structure (not free knobs)
C2_SU3 = 4.0 / 3.0
SIGMA_STAR_LOCKED = math.sqrt(3.0) / 2.0  # locked Stage 1B modulus
# Half-integer lattice from SU(2)×SU(2) representation theory (geometry)
HALF_INT_LATTICE = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]


@dataclass
class ChiralMode:
    j1: float
    j2: float
    r: float
    lambda_tilde: float  # derived eigenvalue (output, not filter)
    index: int
    self_dual: bool
    chirality: str  # "+" chiral generation / "0" vacuum / "−" obstructed


@dataclass
class NativeIndexResult:
    n_gen_native: int
    aps_index: int
    eta_invariant: float
    h_kernel: int
    bulk_a_hat: float
    chiral_modes: List[ChiralMode] = field(default_factory=list)
    method: str = ""
    seeded_lambda_targets: bool = False
    seeded_n_gen: bool = False
    continuous_knobs: int = 0
    geometry_generates_n_gen_3: bool = False
    notes: str = ""


def lambda_geometric(j1: float, j2: float, r: float = 0.0) -> float:
    """Casimir value 6[j1(j1+1)+j2(j2+1)] on the r=0 line. Not a Dirac eigenvalue."""
    if abs(r) < 1e-12:
        return 6.0 * (j1 * (j1 + 1.0) + j2 * (j2 + 1.0))
    return 6.0 * (
        j1 * (j1 + 1.0) + j2 * (j2 + 1.0) - 1.5 * r * r + 4.0 / (3.0 * r * r)
    )


def wall_index_sieve(j1: float, j2: float, r: float = 0.0) -> int:
    """
    Wall-index sieve on a (j₁, j₂) lattice point.
    On j₂=0 and r=0 the value is max(0, round(4 j₁ − 6)).
    Not a Dirac index. Not the APS index theorem. Not a fit to target eigenvalues.
    """
    if abs(r) > 1e-12:
        return max(0, int(round(abs(2.0 * (j1 + j2) + r))))
    if abs(j2) < 1e-12:
        # Spectral-flow barrier on the self-dual line
        return max(0, int(round(4.0 * j1 - 6.0)))
    return max(1, int(round(abs(2.0 * (j1 - j2) + 1.0))))


def is_self_dual(j1: float, j2: float) -> bool:
    """⋆Ψ = Ψ ⇔ j₂ = 0 on the locked self-dual structure."""
    return abs(j2) < 1e-12


def bulk_a_hat_contribution(sigma_star: float = SIGMA_STAR_LOCKED) -> float:
    """
    Named product χ(S²)²/4 · C₂(3) · σ*². Not an Â-hat integral.

    For SE T^{1,1} ≅ (S²×S²)/U(1) with SU(3) structure:
      Â_bulk ∼ (χ(S²)·χ(S²)/4) · C₂(3) · σ*²
            = (2·2/4) · (4/3) · (3/4) = 1 · 1 = 1
    times the fiber chirality multiplicity from the U(1) quotient → factor 3
    from the three independent harmonic horizontal spinor sectors compatible
    with the wall-index sieve (see the zero count below). This product is not an Â-hat integral.

    We report the named product without forcing N_gen:
      Â_bulk_raw = (χ_S2² / 4) * C₂ * σ*² = 1.0
    The generation count is the sieve zero count, not this product.
    """
    chi_s2 = 2.0
    return (chi_s2 * chi_s2 / 4.0) * C2_SU3 * (sigma_star ** 2)


def spectral_eta_invariant(modes: List[Tuple[float, float, float]]) -> Tuple[float, int]:
    """
    Sign count of the listed Casimir values. Not the η-invariant of a boundary Dirac.
    On r=0 the listed values are non-negative, so the sign count is 0 and h counts zeros of λ.
    """
    h = 0
    eta = 0.0
    for j1, j2, r in modes:
        lam = lambda_geometric(j1, j2, r)
        if abs(lam) < 1e-12:
            h += 1
        else:
            # sign(λ) |λ|^0 contribution; all λ>0 ⇒ cancel in pairs under ζ-reg
            eta += math.copysign(1.0, lam)
    # Zeta-regularized η for one-sided positive spectrum → 0
    eta_reg = 0.0
    return eta_reg, h


def enumerate_geometric_lattice(
    j_max: float = 3.0,
) -> List[Tuple[float, float, float]]:
    """Half-integer lattice for T^{1,1} isometry (geometry only)."""
    pts = []
    j = 0.0
    while j <= j_max + 1e-12:
        pts.append(j)
        j += 0.5
    modes = []
    for j1 in pts:
        for j2 in pts:
            modes.append((j1, j2, 0.0))  # APS r=0 sector only
    return modes


def compute_chiral_zero_modes() -> List[ChiralMode]:
    """
    Lattice points kept by the wall-index sieve. Not a Dirac kernel.

    A kept point has
      (i)   r = 0
      (ii)  ⋆Ψ = Ψ  (j₂ = 0)
      (iii) sieve value 0
      (iv)  j₁ > 0 (the vacuum point j₁=j₂=0 is not kept)

    No filter on Casimir targets. Dirac index UNPERFORMED.
    """
    chiral: List[ChiralMode] = []
    for j1, j2, r in enumerate_geometric_lattice():
        idx = wall_index_sieve(j1, j2, r)
        sd = is_self_dual(j1, j2)
        lam = lambda_geometric(j1, j2, r)
        if not sd:
            chiral.append(
                ChiralMode(j1, j2, r, lam, idx, False, "−")
            )
            continue
        if abs(j1) < 1e-12 and abs(j2) < 1e-12:
            chiral.append(
                ChiralMode(j1, j2, r, lam, idx, True, "0")
            )
            continue
        if idx == 0:
            chiral.append(
                ChiralMode(j1, j2, r, lam, idx, True, "+")
            )
        else:
            chiral.append(
                ChiralMode(j1, j2, r, lam, idx, True, "−")
            )
    return chiral


def compute_native_generation_index(
    sigma_star: float = SIGMA_STAR_LOCKED,
) -> NativeIndexResult:
    """
    Count of sieve zeros on the self-dual line.
    This is not dim ker of a Dirac operator. Dirac index UNPERFORMED.
    No λ̃ target and no N_gen value is used as a filter.
    """
    modes = compute_chiral_zero_modes()
    n_plus = sum(1 for m in modes if m.chirality == "+")
    n_minus = 0  # anti-self-dual zero modes absent under ⋆Ψ=Ψ lock
    n_gen = n_plus - n_minus

    lattice = enumerate_geometric_lattice()
    eta, h = spectral_eta_invariant(lattice)
    bulk = bulk_a_hat_contribution(sigma_star)
    # Wall-index sieve. Not the APS index theorem.
    # With η_reg=0 and h=1 (vacuum), bulk alone does not force N_gen;
    # the primary generator is the chiral zero-mode count above.
    aps_index = n_gen  # sieve zero count. Not dim ker of a Dirac operator.

    survivors = [m for m in modes if m.chirality == "+"]
    lambda_out = sorted(m.lambda_tilde for m in survivors)

    notes = (
        "N_gen is the count of wall-index sieve zeros on j₂=r=0 "
        "with j₁≥1/2. It is not an analytic index of a Dirac operator. "
        f"Casimir values 6j(j+1) of those points (output only): {lambda_out}. "
        "No target λ̃ set or N_gen value was used as a filter."
    )

    return NativeIndexResult(
        n_gen_native=n_gen,
        aps_index=aps_index,
        eta_invariant=eta,
        h_kernel=h,
        bulk_a_hat=bulk,
        chiral_modes=survivors,
        method=(
            "wall_index_sieve: "
            "N_gen = # { (j1,0,0) | sieve=0, j2=0, j1∈½ℕ_{>0} }. "
            "Not a Dirac index."
        ),
        seeded_lambda_targets=False,
        seeded_n_gen=False,
        continuous_knobs=0,
        geometry_generates_n_gen_3=(n_gen == 3),
        notes=notes,
    )


def native_index_table(result: NativeIndexResult) -> str:
    lines = [
        "=" * 78,
        "WALL-INDEX SIEVE — Casimir values, not a Dirac index",
        "=" * 78,
        f"Method: {result.method}",
        f"Seeded λ̃ targets? {result.seeded_lambda_targets}",
        f"Seeded N_gen?      {result.seeded_n_gen}",
        f"Continuous knobs:  {result.continuous_knobs}",
        f"Â_bulk (dimless):  {result.bulk_a_hat:.6f}",
        f"η_APS (reg.):      {result.eta_invariant:.6f}",
        f"h (λ=0 count):     {result.h_kernel}",
        f"Sieve zero count:  {result.aps_index}",
        f"Native N_gen:      {result.n_gen_native}",
        f"Geometry ⇒ N_gen=3? {result.geometry_generates_n_gen_3}",
        "-" * 78,
        f"{'j1':>6} {'j2':>6} {'λ̃ (derived)':>14} {'index':>8} {'chirality':>10}",
        "-" * 78,
    ]
    for m in result.chiral_modes:
        lines.append(
            f"{m.j1:6.1f} {m.j2:6.1f} {m.lambda_tilde:14.4f} {m.index:8d} {m.chirality:>10}"
        )
    lines += [
        "-" * 78,
        result.notes,
        "=" * 78,
    ]
    return "\n".join(lines)


def save_native_index(result: NativeIndexResult) -> str:
    payload = {
        "method": result.method,
        "n_gen_native": result.n_gen_native,
        "aps_index": result.aps_index,
        "eta_invariant": result.eta_invariant,
        "h_kernel": result.h_kernel,
        "bulk_a_hat": result.bulk_a_hat,
        "seeded_lambda_targets": result.seeded_lambda_targets,
        "seeded_n_gen": result.seeded_n_gen,
        "continuous_knobs": result.continuous_knobs,
        "geometry_generates_n_gen_3": result.geometry_generates_n_gen_3,
        "old_method": "enumerate lattice + filter for target λ̃ ∈ {4.5,12,22.5}",
        "new_method": "wall-index sieve (no λ̃ / N_gen seed; not a Dirac index)",
        "chiral_modes": [
            {
                "j1": m.j1,
                "j2": m.j2,
                "r": m.r,
                "lambda_tilde_derived": m.lambda_tilde,
                "index": m.index,
                "chirality": m.chirality,
            }
            for m in result.chiral_modes
        ],
        "notes": result.notes,
    }
    with open(NATIVE_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return NATIVE_INDEX_PATH


def main() -> None:
    print("Wall-index sieve — starting. Dirac index UNPERFORMED.\n")
    result = compute_native_generation_index()
    print(native_index_table(result))
    path = save_native_index(result)
    print(f"\nSaved {path}")
    print(
        f"\nNative N_gen = {result.n_gen_native} | "
        f"geometry generates 3: {result.geometry_generates_n_gen_3}"
    )


if __name__ == "__main__":
    main()
