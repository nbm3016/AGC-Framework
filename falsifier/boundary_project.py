"""On-shell image of the ambient bracket on M^4.

The 128-dimensional module is V4 ⊗ V32, spacetime Dirac tensor the
10-dimensional fiber. E4 = Tr_fiber(E) / 32. Nothing is promoted.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import triality_build as tb

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "boundary_project.json"
OUT_MD = ROOT / "BOUNDARY_PROJECT.md"
FIBER = 32
SPACETIME = 4


def ambient_exhaust() -> tuple[np.ndarray, list[np.ndarray]]:
    """Same cyclic bracket as triality_build.build(14)."""
    gs = tb.gammas(14)
    star4 = np.eye(gs[0].shape[0], dtype=np.complex128)
    for g in gs[:4]:
        star4 = star4 @ g
    if not np.allclose(star4, star4.conj().T):
        star4 = -1j * star4
    chir = np.eye(gs[0].shape[0], dtype=np.complex128)
    for g in gs:
        chir = chir @ g
    if not np.allclose(chir, chir.conj().T):
        chir = -1j * chir
    reality, _sign = tb.charge_conjugation(gs)
    eye = np.eye(gs[0].shape[0], dtype=np.complex128)
    volume_is_scalar = bool(np.allclose(chir, eye) or np.allclose(chir, -eye))
    star = star4 if volume_is_scalar else chir
    mode = 0.5 * (eye + star)
    exhaust = tb.bracket(mode, star, reality)
    return exhaust, gs


def partial_trace_fiber(op: np.ndarray) -> np.ndarray:
    """Normalized partial trace over the fast factor of V4 ⊗ V32."""
    if op.shape != (SPACETIME * FIBER, SPACETIME * FIBER):
        raise SystemExit(f"expected 128x128, got {op.shape}")
    reshaped = op.reshape(SPACETIME, FIBER, SPACETIME, FIBER)
    traced = np.einsum("abcb->ac", reshaped)
    return traced / FIBER


def exact_term(z: complex) -> str:
    scale = 32
    re = int(round(z.real * scale))
    im = int(round(z.imag * scale))
    if abs(z.real - re / scale) > 1e-8 or abs(z.imag - im / scale) > 1e-8:
        return f"{z.real}+{z.imag}i"

    def piece(num: int) -> str:
        if num == 0:
            return "0"
        sign = "-" if num < 0 else ""
        num = abs(num)
        g = int(np.gcd(num, scale))
        return f"{sign}{num // g}/{scale // g}" if g != scale else f"{sign}{num // g}"

    re_s = piece(re)
    im_s = piece(im)
    if im == 0:
        return re_s
    if re == 0:
        return f"{im_s}i"
    joiner = "+" if im > 0 else ""
    return f"{re_s}{joiner}{im_s}i"


def matrix_records(op: np.ndarray) -> list[list[str]]:
    return [[exact_term(complex(z)) for z in row] for row in op]


def kernel_of(op: np.ndarray) -> tuple[int, list[list[str]], list[float]]:
    _u, singular, vh = np.linalg.svd(op)
    values = [float(s) for s in singular]
    mask = singular < 1e-8
    basis = vh[mask]
    # Orthonormal rows of vh. Snap for the report.
    recorded = []
    for vector in basis:
        recorded.append([exact_term(complex(z)) for z in vector])
    return int(mask.sum()), recorded, values


def main() -> int:
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")

    exhaust, gammas = ambient_exhaust()
    eye128 = np.eye(128, dtype=np.complex128)
    if not np.allclose(partial_trace_fiber(eye128), np.eye(SPACETIME)):
        raise SystemExit("partial trace of the identity is not the 4D identity")
    probe = np.arange(16, dtype=np.complex128).reshape(4, 4)
    if not np.allclose(partial_trace_fiber(np.kron(probe, np.eye(FIBER))), probe):
        raise SystemExit("partial trace does not invert A ⊗ I_32")

    for index, gamma in enumerate(gammas):
        reduced = partial_trace_fiber(gamma)
        pure = np.allclose(gamma, np.kron(reduced, np.eye(FIBER)))
        if index >= 10 and not pure:
            raise SystemExit(f"gamma {index} is not an operator on V4 tensor I_32")

    norm = float(np.linalg.norm(exhaust))
    rank = int(np.linalg.matrix_rank(exhaust, tol=1e-8))
    if abs(norm - float(np.sqrt(128))) > 1e-6 or rank != 128:
        raise SystemExit(f"ambient bracket is not the stored rank-128 exhaust: norm {norm}, rank {rank}")

    reshaped = exhaust.reshape(SPACETIME, FIBER, SPACETIME, FIBER)
    tensor = reshaped.transpose(0, 2, 1, 3).reshape(SPACETIME * SPACETIME, FIBER * FIBER)
    tensor_singular = np.linalg.svd(tensor, compute_uv=False)
    pure_tensor = bool(tensor_singular[0] > 1e-8 and tensor_singular[1] < 1e-8)
    projected = partial_trace_fiber(exhaust)
    kernel_dim, kernel_basis, singular = kernel_of(projected)
    projected_rank = int(np.linalg.matrix_rank(projected, tol=1e-8))
    # A lock moves only when this endomorphism equals that lock's value,
    # the match is unique, and extras = 0. No stored lock is an element of End(V4).
    matches = []
    for item in locks:
        if item.get("extras") != 0:
            continue
        value = item.get("value")
        if isinstance(value, list) and matrix_records(projected) == value:
            matches.append(item["name"])
    moved = matches if len(matches) == 1 else []
    rescored = [
        {
            "name": item["name"],
            "prior": "LOCK",
            "bin": "LOCK",
            "changed": item["name"] in moved,
        }
        for item in locks
    ]
    for row in rescored:
        if row["changed"]:
            row["bin"] = "RESOLVED"

    payload = {
        "continuous_knobs": 0,
        "promoted": False,
        "ambient": "Y^14 → M^4",
        "factors": ["Σ^5", "T^{1,1}"],
        "factorization": "V4 ⊗ V32",
        "fiber": "Cl(10) module of the 10D factor, dimension 32",
        "projection": "E4 = Tr_fiber(E) / 32",
        "generator": "cyclic bracket on the 128-dimensional Clifford module",
        "module_rank": rank,
        "module_norm": norm,
        "time_ambient": "EMERGENT",
        "mass": {
            "spacetime_dirac": SPACETIME,
            "fiber": FIBER,
            "ambient": 128,
            "kilogram": False,
        },
        "pure_tensor": pure_tensor,
        "projected_operator": matrix_records(projected),
        "projected_norm": float(np.linalg.norm(projected)),
        "projected_rank": projected_rank,
        "singular_values": singular,
        "kernel_dimension": kernel_dim,
        "kernel_basis": kernel_basis,
        "rows_changed": len(moved),
        "moved": moved,
        "rescored": rescored,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# On-shell projection",
        "",
        "The ambient generator is the cyclic bracket on the 128-dimensional Clifford module. Its rank is the rank of that operator on the module. The on-shell image on M^4 is the normalized partial trace over the fiber.",
        "",
        "Factorization: V4 ⊗ V32. V4 is the 4D spacetime Dirac module, the outer two Pauli lifts. V32 is the Cl(10) module of the internal factor. Σ^5 and T^{1,1} stay the factors of that 10-dimensional fiber.",
        "",
        "Projection: E4 = Tr_fiber(E) / 32.",
        "",
        f"Module norm: {norm}",
        f"Module rank: {rank}",
        f"Projected norm: {payload['projected_norm']}",
        f"Projected rank: {projected_rank}",
        f"Kernel dimension: {kernel_dim}",
        "",
        "## Projected operator",
        "",
    ]
    for row in payload["projected_operator"]:
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "E is a pure tensor on V4 ⊗ V32." if pure_tensor else "E is not a pure tensor.",
        (
            "The normalized fiber trace is the zero operator. The kernel is all of V4."
            if projected_rank == 0
            else "The normalized fiber trace is the operator below."
        ),
        "",
        "## Kernel",
        "",
    ]
    if kernel_dim == 0:
        lines.append("The kernel is {0}.")
    elif kernel_dim == SPACETIME and projected_rank == 0:
        lines.append("Kernel dimension 4. The kernel is V4. One orthonormal basis is the computational basis:")
        for vector in kernel_basis:
            lines.append("- (" + ", ".join(vector) + ")")
    else:
        lines.append(f"Kernel dimension {kernel_dim}. Orthonormal basis:")
        for vector in kernel_basis:
            lines.append("- (" + ", ".join(vector) + ")")
    lines += [
        "",
        "## What moved",
        "",
        "Moved: " + (", ".join(moved) if moved else "none") + ".",
        f"Rows changed: {len(moved)}.",
        (
            "Each of the 35 locks stays LOCK. The projected operator has type End(V4). No stored lock equals that matrix with extras = 0."
            if not moved
            else "Resolved: " + ", ".join(moved) + "."
        ),
        "",
        "Time on the ambient is the exhaust E. Mass is the module data: 4, 32, and 128. It is not a kilogram.",
        "",
        "ON-SHELL PROJECTION — FIBER TRACE — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
