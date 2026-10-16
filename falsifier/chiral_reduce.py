"""Chirality-weighted reduction of the ambient bracket.

E4 = Tr_fiber((I4 ⊗ Γ10) E) / 32. Γ10 is the Clifford volume of the
10D fiber. The module order is V4 outer, V32 inner. Nothing is promoted.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import boundary_project as bp
import triality_build as tb

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "chiral_reduce.json"
OUT_MD = ROOT / "CHIRAL_REDUCE.md"


def hermitian_volume(gammas: list[np.ndarray]) -> np.ndarray:
    raw = np.eye(gammas[0].shape[0], dtype=np.complex128)
    for gamma in gammas:
        raw = raw @ gamma
    if np.allclose(raw, raw.conj().T):
        return raw
    return np.array(-1j * raw, dtype=np.complex128)


def fiber_chirality(gammas14: list[np.ndarray]) -> np.ndarray:
    """Clifford volume on the inner Cl(10) factor, phase fixed by hermiticity."""
    fiber_gammas = tb.gammas(10)
    if fiber_gammas[0].shape != (bp.FIBER, bp.FIBER):
        raise SystemExit("Cl(10) module is not 32-dimensional")
    raw10 = np.eye(bp.FIBER, dtype=np.complex128)
    for gamma in fiber_gammas:
        raw10 = raw10 @ gamma
    raw14 = np.eye(bp.SPACETIME * bp.FIBER, dtype=np.complex128)
    for gamma in gammas14[:10]:
        raw14 = raw14 @ gamma
    if not np.allclose(raw14, np.kron(np.eye(bp.SPACETIME), raw10)):
        raise SystemExit("fiber volume is not I4 tensor the inner Cl(10) volume")
    gamma10 = hermitian_volume(fiber_gammas)
    eye = np.eye(bp.FIBER, dtype=np.complex128)
    if not (np.allclose(gamma10 @ gamma10, eye) or np.allclose(gamma10 @ gamma10, -eye)):
        raise SystemExit("Γ10 does not square to ±I")
    if not np.allclose(gamma10, gamma10.conj().T):
        raise SystemExit("Γ10 is not Hermitian")
    return gamma10


def eigenspace_dims(gamma10: np.ndarray) -> dict[str, int]:
    evals = np.linalg.eigvalsh(gamma10)
    return {
        "+1": int(np.sum(np.abs(evals - 1) < 1e-8)),
        "-1": int(np.sum(np.abs(evals + 1) < 1e-8)),
    }


def singlet_obstruction(locks: list[dict], spaces: dict[str, int]) -> dict:
    """A fiber singlet is a 1-dimensional subspace of this V32 with extras=0."""
    rays = []
    for item in locks:
        if item.get("extras") != 0:
            continue
        value = item.get("value")
        if isinstance(value, list) and len(value) == bp.FIBER:
            rays.append(item["name"])
    by_name = {item["name"]: item for item in locks}
    dirac = by_name.get("DIRAC_T11", {})
    wall = by_name.get("wall_zero_count", {})
    reasons = [
        f"Γ10 eigenspaces on V32 have dimensions +1:{spaces['+1']} and -1:{spaces['-1']}.",
        "PARALLEL_SPINORS_CONE locks one complex line of parallel spinors on the cone of T^{1,1}. "
        "The phase is the Iso U(1). No lock places that line in V32.",
        "DIRAC_T11 locks " + str(dirac.get("value")) + ".",
        "wall_zero_count locks " + str(wall.get("value")) + ", the count of the harmonics 2⊕3⊕4.",
        "Σ^5 has no parallel-spinor lock. The locked product Σ^5 × T^{1,1} names no ray in V32.",
        "No lock with extras=0 stores a vector in this 32-dimensional module.",
    ]
    return {
        "forced": len(rays) == 1,
        "ray_name": rays[0] if len(rays) == 1 else None,
        "reasons": reasons,
    }


def _fiber_factor(op: np.ndarray) -> np.ndarray | None:
    matrix = op.reshape(bp.SPACETIME, bp.FIBER, bp.SPACETIME, bp.FIBER)
    flat = matrix.transpose(0, 2, 1, 3).reshape(bp.SPACETIME * bp.SPACETIME, bp.FIBER * bp.FIBER)
    _u, singular, vh = np.linalg.svd(flat, full_matrices=False)
    if singular[1] > 1e-8:
        return None
    return vh[0].reshape(bp.FIBER, bp.FIBER)


def _same_line(left: np.ndarray | None, right: np.ndarray | None) -> bool:
    if left is None or right is None:
        return False
    left_n = left / np.linalg.norm(left)
    right_n = right / np.linalg.norm(right)
    overlap = np.vdot(right_n, left_n)
    return bool(np.allclose(left_n, overlap * right_n))


def fiber_expectation(exhaust: np.ndarray, ray: np.ndarray) -> np.ndarray:
    vector = np.array(ray, dtype=np.complex128)
    norm = np.linalg.norm(vector)
    if norm < 1e-12:
        raise SystemExit("fiber ray has norm zero")
    vector = vector / norm
    reshaped = exhaust.reshape(bp.SPACETIME, bp.FIBER, bp.SPACETIME, bp.FIBER)
    return np.einsum("b,abcd,d->ac", vector.conj(), reshaped, vector)


def resolves(op: np.ndarray, locks: list[dict]) -> list[str]:
    recorded = bp.matrix_records(op)
    matches = []
    for item in locks:
        if item.get("extras") != 0:
            continue
        if item.get("value") == recorded:
            matches.append(item["name"])
    return matches if len(matches) == 1 else []


def main() -> int:
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")

    exhaust, gammas14 = bp.ambient_exhaust()
    rank = int(np.linalg.matrix_rank(exhaust, tol=1e-8))
    if rank != 128:
        raise SystemExit(f"ambient bracket rank is {rank}")

    gamma10 = fiber_chirality(gammas14)
    spaces = eigenspace_dims(gamma10)
    weighted = np.kron(np.eye(bp.SPACETIME, dtype=np.complex128), gamma10) @ exhaust
    projected = bp.partial_trace_fiber(weighted)
    kernel_dim, kernel_basis, singular = bp.kernel_of(projected)
    projected_rank = int(np.linalg.matrix_rank(projected, tol=1e-8))
    square = "I" if np.allclose(gamma10 @ gamma10, np.eye(bp.FIBER)) else "-I"
    chirality = np.eye(exhaust.shape[0], dtype=np.complex128)
    for gamma in gammas14:
        chirality = chirality @ gamma
    if not np.allclose(chirality, chirality.conj().T):
        chirality = -1j * chirality
    reality, _sign = tb.charge_conjugation(gammas14)
    fiber_of_volume = _fiber_factor(chirality)
    fiber_of_c = _fiber_factor(reality)
    fiber_of_weighted = _fiber_factor(weighted)
    volume_is_gamma10 = _same_line(fiber_of_volume, gamma10)
    weighted_is_c = _same_line(fiber_of_weighted, fiber_of_c)
    exhaust_is_volume_c = bool(np.allclose(exhaust, chirality @ reality))
    fiber_trace_zero = fiber_of_c is not None and abs(np.trace(fiber_of_c)) < 1e-8

    obstruction = singlet_obstruction(locks, spaces)
    if obstruction["forced"]:
        source = next(item for item in locks if item["name"] == obstruction["ray_name"])
        expected = fiber_expectation(exhaust, np.array(source["value"], dtype=np.complex128))
        exp_kernel, exp_basis, exp_singular = bp.kernel_of(expected)
        singlet = {
            "computed": True,
            "label": source["name"],
            "operator": bp.matrix_records(expected),
            "norm": float(np.linalg.norm(expected)),
            "rank": int(np.linalg.matrix_rank(expected, tol=1e-8)),
            "kernel_dimension": exp_kernel,
            "kernel_basis": exp_basis,
            "singular_values": exp_singular,
            "obstruction": [],
        }
    else:
        singlet = {
            "computed": False,
            "label": None,
            "operator": None,
            "kernel_dimension": None,
            "kernel_basis": None,
            "obstruction": obstruction["reasons"],
        }

    moved = resolves(projected, locks)
    if singlet["computed"]:
        also = resolves(expected, locks)
        if len(also) == 1 and also[0] not in moved:
            moved = moved + also
    rescored = [
        {
            "name": item["name"],
            "prior": "LOCK",
            "bin": "RESOLVED" if item["name"] in moved else "LOCK",
            "changed": item["name"] in moved,
        }
        for item in locks
    ]
    operator = {
        "name": "E4",
        "formula": "Tr_fiber((I4 ⊗ Γ10) E) / 32",
        "matrix": bp.matrix_records(projected),
        "norm": float(np.linalg.norm(projected)),
        "rank": projected_rank,
        "kernel_dimension": kernel_dim,
        "kernel_basis": kernel_basis,
        "singular_values": singular,
    }
    payload = {
        "continuous_knobs": 0,
        "promoted": False,
        "ambient": "Y^14 → M^4",
        "factors": ["Σ^5", "T^{1,1}"],
        "factorization": "V4 ⊗ V32",
        "gamma10": {
            "definition": "Hermitian Clifford volume of the inner Cl(10), phase -i on the raw product",
            "square": square,
            "eigenspaces": spaces,
            "volume_fiber_is_gamma10": bool(volume_is_gamma10),
            "exhaust_is_volume_times_C": bool(exhaust_is_volume_c),
            "weighted_fiber_is_C": bool(weighted_is_c),
            "C_fiber_trace_zero": bool(fiber_trace_zero),
        },
        "chiral_operator": operator,
        "singlet_operator": singlet,
        "rows_changed": len(moved),
        "moved": moved,
        "rescored": rescored,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Chiral reduction",
        "",
        "Γ10 is the Hermitian Clifford volume of the 10D fiber. The module order is V4 outer and V32 inner, the same order as the boundary projection. The reduction is",
        "",
        "E4 = Tr_fiber((I4 ⊗ Γ10) E) / 32.",
        "",
        f"Γ10 squares to {square}. Eigenspaces: +1 has dimension {spaces['+1']}, -1 has dimension {spaces['-1']}.",
        (
            "The 14D volume has fiber factor Γ10. E = ★ C, so (I4 ⊗ Γ10) E has the fiber factor of C. That factor has trace zero, and E4 is the zero operator."
            if volume_is_gamma10 and exhaust_is_volume_c and weighted_is_c and fiber_trace_zero and projected_rank == 0
            else "The chiral trace was computed from (I4 ⊗ Γ10) E."
        ),
        f"Projected norm: {operator['norm']}",
        f"Projected rank: {projected_rank}",
        f"Kernel dimension: {kernel_dim}",
        "",
        "## Chiral operator",
        "",
    ]
    for row in operator["matrix"]:
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Kernel of the chiral operator", ""]
    if kernel_dim == bp.SPACETIME and projected_rank == 0:
        lines.append("The kernel is V4. One orthonormal basis is the computational basis:")
    elif kernel_dim == 0:
        lines.append("The kernel is {0}.")
    else:
        lines.append(f"Kernel dimension {kernel_dim}. Orthonormal basis:")
    for vector in kernel_basis:
        lines.append("- (" + ", ".join(vector) + ")")
    lines += [
        "",
        "## Singlet operator",
        "",
    ]
    if singlet["computed"]:
        lines.append(f"⟨0|E|0⟩ is labeled by {singlet['label']}.")
        lines.append("")
        for row in singlet["operator"]:
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
        lines.append(f"Kernel dimension: {singlet['kernel_dimension']}.")
        for vector in singlet["kernel_basis"]:
            lines.append("- (" + ", ".join(vector) + ")")
    else:
        lines.append("⟨0|E|0⟩ was not computed. No state was picked.")
        lines.append("")
        lines.append("Obstruction:")
        for reason in singlet["obstruction"]:
            lines.append(f"- {reason}")
    lines += [
        "",
        "## What moved",
        "",
        "Moved: " + (", ".join(moved) if moved else "none") + ".",
        f"Rows changed: {len(moved)}.",
        "The chiral operator has type End(V4). No stored lock equals that matrix with extras = 0.",
        "",
        "CHIRAL REDUCTION — FIBER VOLUME — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
