"""Trinodal exhaust. Psi-star is charge conjugation, not elementwise conj.

Writes triality_build.json and TRIALITY_BUILD.md only.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "triality_build.json"
OUT_MD = ROOT / "TRIALITY_BUILD.md"


def paul() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    s1 = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    s2 = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
    s3 = np.array([[1, 0], [0, -1]], dtype=np.complex128)
    eye = np.eye(2, dtype=np.complex128)
    return s1, s2, s3, eye


def gammas(n: int) -> list[np.ndarray]:
    """Hermitian Euclidean generators. Even dimension first, then the volume if n is odd."""
    s1, s2, s3, _ = paul()
    gs = [s1, s2]
    while len(gs) < n - (n % 2):
        eye = np.eye(gs[0].shape[0], dtype=np.complex128)
        lifted = [np.kron(s1, g) for g in gs]
        lifted.append(np.kron(s2, eye))
        lifted.append(np.kron(s3, eye))
        gs = lifted
    if n % 2 == 1:
        vol = np.eye(gs[0].shape[0], dtype=np.complex128)
        for g in gs:
            vol = vol @ g
        # The even volume element is unitary; Hermitianize by a fixed phase, not a free one.
        phase = 1.0 if np.allclose(vol, vol.conj().T) else -1j
        gs.append(np.array(phase * vol, dtype=np.complex128))
    out = gs[:n]
    for i, g in enumerate(out):
        if not np.allclose(g @ g, np.eye(g.shape[0])):
            raise SystemExit(f"gamma {i} in d={n} does not square to 1")
        if not np.allclose(g, g.conj().T):
            raise SystemExit(f"gamma {i} in d={n} is not Hermitian")
        for j in range(i):
            if not np.allclose(g @ out[j] + out[j] @ g, 0):
                raise SystemExit(f"gammas {i},{j} in d={n} do not anticommute")
    return out


def charge_conjugation(gs: list[np.ndarray]) -> tuple[np.ndarray, int]:
    """C gamma C^{-1} = ± gamma^T by the same Pauli lift that builds the gammas.

    Not elementwise conjugation. In odd dimension the last generator is the
    Hermitian volume element; if its transpose sign disagrees, C is multiplied
    by that generator so every sign agrees.
    """
    s1, s2, s3, _ = paul()
    c = s1.copy()
    eps = 1
    target = gs[0].shape[0]
    while c.shape[0] < target:
        if eps == 1:
            c = np.kron(s2, c)
            eps = -1
        else:
            c = np.kron(s3, c)
            eps = 1
    if c.shape[0] != target:
        raise SystemExit("charge conjugation size does not match the spinor space")
    if len(gs) % 2 == 1:
        inv = np.linalg.inv(c)
        last = gs[-1]
        image = c @ last @ inv
        if np.allclose(image, -eps * last.T):
            c = c @ last
            eps = -eps
        elif not np.allclose(image, eps * last.T):
            raise SystemExit("volume gamma is not a transpose intertwiner")
    inv = np.linalg.inv(c)
    for g in gs:
        image = c @ g @ inv
        if not (np.allclose(image, eps * g.T)):
            raise SystemExit("C is not a uniform transpose intertwiner")
    eye = np.eye(c.shape[0], dtype=np.complex128)
    square = c @ c
    if not (np.allclose(square, eye) or np.allclose(square, -eye)):
        raise SystemExit("C^2 is not ±I")
    return c, eps


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def bracket(psi: np.ndarray, star: np.ndarray, reality: np.ndarray) -> np.ndarray:
    return comm(psi, star) + comm(star, reality) + comm(reality, psi)


def build(n: int) -> dict:
    gs = gammas(n)
    # Transverse Hodge star: product of the first four generators when n>=4.
    # Ambient chirality: product of every generator.
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
    reality, c_sign = charge_conjugation(gs)
    eye = np.eye(gs[0].shape[0], dtype=np.complex128)
    # Odd-dimensional volume is ±I, so it is not a second observer. Use the
    # transverse 4-volume there. On an even ambient the volume is the Hodge star.
    volume_is_scalar = bool(np.allclose(chir, eye) or np.allclose(chir, -eye))
    star = star4 if volume_is_scalar else chir
    star_name = "transverse 4-volume" if volume_is_scalar else "Clifford volume"
    mode4 = 0.5 * (eye + star4)
    mode = 0.5 * (eye + star)
    exhaust_transverse = bracket(mode4, star4, reality)
    exhaust = bracket(mode, star, reality)
    norm = float(np.linalg.norm(exhaust))
    return {
        "dimension": n,
        "state_dim": int(gs[0].shape[0]),
        "generator": "Pauli-lift charge conjugation C",
        "C_sign": int(c_sign),
        "C_square": "I" if np.allclose(reality @ reality, eye) else "-I",
        "star": star_name,
        "star_square": "I" if np.allclose(star @ star, eye) else "-I",
        "volume_is_scalar": volume_is_scalar,
        "exhaust_norm": norm,
        "exhaust_is_zero": bool(norm < 1e-8),
        "exhaust_rank": int(np.linalg.matrix_rank(exhaust, tol=1e-8)),
        "transverse_exhaust_norm": float(np.linalg.norm(exhaust_transverse)),
    }


def main() -> int:
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item["name"] for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")
    factor = build(5)
    ambient = build(14)
    time_bin = "TRIVIAL" if factor["exhaust_is_zero"] else "EMERGENT"
    ambient_bin = "TRIVIAL" if ambient["exhaust_is_zero"] else "EMERGENT"
    rescored = [
        {"name": name, "prior": "LOCK", "bin": "LOCK", "changed": False}
        for name in locks
    ]
    rows = [
        {
            "id": "R1",
            "object": "possibility set",
            "seat": "shared",
            "data": 35,
            "exhaust": "",
            "bin": "FORCED",
            "why": "35 locks, one list. Psi-star is charge conjugation C, not the left star and not elementwise conj.",
        },
        {
            "id": "R2",
            "object": "observers",
            "seat": "Psi, star Psi, Psi-star",
            "data": factor["state_dim"],
            "exhaust": "",
            "bin": "FORCED",
            "why": "Three seats are occupied. Each is an observer. The binding is not the only observer.",
        },
        {
            "id": "R3",
            "object": "trinodal state",
            "seat": "3/3",
            "data": factor["state_dim"],
            "exhaust": "",
            "bin": "FORCED",
            "why": "Psi is (I+star)/2. On the factor the 5-volume is I, so star Psi is the transverse 4-volume. Psi-star is C.",
        },
        {
            "id": "R4",
            "object": "mass candidate",
            "seat": "three",
            "data": factor["state_dim"],
            "exhaust": "",
            "bin": "FORCED",
            "why": "The three seats act together on the rank-4 spinor space of Dirac(g_5). The data count is 4. It is not a kilogram.",
        },
        {
            "id": "R5",
            "object": "time",
            "seat": "three",
            "data": factor["state_dim"],
            "exhaust": factor["exhaust_norm"],
            "bin": time_bin,
            "why": "The cyclic bracket was computed. A zero bracket is TRIVIAL. A non-zero bracket is EMERGENT. The two-seat defect was not used.",
        },
        {
            "id": "R6",
            "object": "35 rows",
            "seat": "shared",
            "data": 35,
            "exhaust": factor["exhaust_norm"],
            "bin": "LOCK",
            "why": "The exhaust is an operator on the spinor space. It does not assign any of the 35 atoms. No row moves.",
        },
        {
            "id": "R7",
            "object": "c2, holonomy, 9/16, 13/2",
            "seat": "shared",
            "data": factor["state_dim"],
            "exhaust": factor["exhaust_norm"],
            "bin": "LOCK",
            "why": "The bracket does not force c2. Hol(g_C)=SU(3) stays holonomy. 9/16 stays a number. T_wall stays 13/2.",
        },
        {
            "id": "R8",
            "object": "14D ambient",
            "seat": "same three",
            "data": ambient["state_dim"],
            "exhaust": ambient["exhaust_norm"],
            "bin": ambient_bin,
            "why": "Same three seats on Cl(14): mode (I+star)/2, star = Clifford volume, Psi-star = C. Cyclic bracket on that module. Not an on-shell boundary condition.",
        },
    ]
    payload = {
        "continuous_knobs": 0,
        "promoted": False,
        "psi_star": "charge conjugation C",
        "generator": "Pauli-lift charge conjugation C; exhaust is [Psi, star Psi] + [star Psi, Psi-star] + [Psi-star, Psi]",
        "not": "elementwise conj",
        "factor_5d": factor,
        "ambient_14d": ambient,
        "time_factor": time_bin,
        "time_ambient": ambient_bin,
        "mass_candidate": factor["state_dim"],
        "rows_changed": 0,
        "rows": rows,
        "rescored": rescored,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Trinodal exhaust",
        "",
        "Psi-star is the charge conjugation operator C. The exhaust is the cyclic bracket. Nothing promoted.",
        "",
        "| id | object | seat | data | exhaust | bin | why |",
        "|----|--------|------|------|---------|-----|-----|",
    ]
    for item in rows:
        lines.append(
            f"| {item['id']} | {item['object']} | {item['seat']} | {item['data']} | {item['exhaust']} | {item['bin']} | {item['why']} |"
        )
    lines += [
        "",
        "Generator: Pauli-lift charge conjugation C. Exhaust: [Psi, star Psi] + [star Psi, Psi-star] + [Psi-star, Psi].",
        f"C on the 5D factor: sign {factor['C_sign']}, C^2 = {factor['C_square']}.",
        f"C on the 14D ambient: sign {ambient['C_sign']}, C^2 = {ambient['C_square']}.",
        "Observers scored: 3",
        "Trinodal seats occupied: 3/3",
        f"Mass candidate: {factor['state_dim']}",
        f"Time on the factor: {time_bin}",
        f"Time on the ambient: {ambient_bin}",
        "Rows changed: 0",
        "Moved: none",
        f"Factor star: {factor['star']}. Factor exhaust norm: {factor['exhaust_norm']}",
        f"Ambient star: {ambient['star']}. Ambient exhaust norm: {ambient['exhaust_norm']}",
        f"Ambient transverse exhaust norm: {ambient['transverse_exhaust_norm']}",
        "",
        "TRIALITY APPLIED — TIME IS EXHAUST — MASS IS DATA — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print("FACTOR", json.dumps(factor))
    print("AMBIENT", json.dumps(ambient))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
