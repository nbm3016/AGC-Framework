"""Ambient 128x128 commutators of exhaust E with gammas(14)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import boundary_project as bp
import triality_build as tb

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "test_cone_spinor.json"
OUT_MD = ROOT / "TEST_CONE_SPINOR.md"
BASELINE = ROOT / "complete_baseline.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def frobenius(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def is_exact_zero(matrix: np.ndarray, scale: float) -> bool:
    norm = frobenius(matrix)
    if norm <= 1e-6:
        return True
    if norm < 1e-2 * max(scale, 1.0):
        raise SystemExit(f"ambiguous bracket norm {norm}")
    return False


def fiber_action(gamma: np.ndarray) -> str:
    block = gamma.reshape(4, 32, 4, 32)
    diagonal = 0.0
    off_diagonal = 0.0
    for a in range(32):
        for b in range(32):
            weight = float(np.linalg.norm(block[:, a, :, b])) ** 2
            if a == b:
                diagonal += weight
            else:
                off_diagonal += weight
    diagonal_hit = diagonal > 1e-12
    off_hit = off_diagonal > 1e-12
    if diagonal_hit and not off_hit:
        return "Diagonal"
    if off_hit and not diagonal_hit:
        return "Off-diagonal"
    if diagonal_hit and off_hit:
        return "Mixed"
    return "Zero"


def square_label(gamma: np.ndarray) -> str:
    eye = np.eye(gamma.shape[0], dtype=np.complex128)
    if np.allclose(gamma @ gamma, eye, atol=1e-8):
        return "+I128"
    if np.allclose(gamma @ gamma, -eye, atol=1e-8):
        return "-I128"
    return "neither ±I128"


def main() -> int:
    baseline_hash = sha256(BASELINE)
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")

    gammas = tb.gammas(14)
    exhaust, exhaust_gammas = bp.ambient_exhaust()
    if exhaust.shape != (128, 128):
        raise SystemExit(f"exhaust shape {exhaust.shape}")
    if len(gammas) != 14 or len(exhaust_gammas) != 14:
        raise SystemExit("expected 14 ambient gammas")
    for index, (left, right) in enumerate(zip(gammas, exhaust_gammas)):
        if left.shape != (128, 128) or not np.allclose(left, right):
            raise SystemExit(f"gamma {index} from gammas(14) and ambient_exhaust disagree")

    exhaust_norm = frobenius(exhaust)
    anticommute: list[int] = []
    commute: list[int] = []
    anticommutator_norms: list[float] = []
    commutator_norms: list[float] = []
    for index, gamma in enumerate(gammas):
        gamma_norm = frobenius(gamma)
        scale = exhaust_norm * gamma_norm
        anticommutator = exhaust @ gamma + gamma @ exhaust
        commutator = exhaust @ gamma - gamma @ exhaust
        anticommutator_norms.append(frobenius(anticommutator))
        commutator_norms.append(frobenius(commutator))
        if is_exact_zero(anticommutator, scale):
            anticommute.append(index)
        if is_exact_zero(commutator, scale):
            commute.append(index)

    index_11_in = 11 in anticommute
    index_13_in = 13 in anticommute
    time_indices: list[int] = []
    time_squares: dict[str, str] = {}
    pair_norms: dict[str, list[float]] = {}
    fiber_by_index: dict[str, str] = {}
    for index in anticommute:
        gamma = gammas[index]
        with_11 = gamma @ gammas[11] + gammas[11] @ gamma
        with_13 = gamma @ gammas[13] + gammas[13] @ gamma
        pair_norms[str(index)] = [frobenius(with_11), frobenius(with_13)]
        scale = frobenius(gamma) * frobenius(gammas[11])
        if is_exact_zero(with_11, scale) and is_exact_zero(with_13, scale):
            time_indices.append(index)
            time_squares[str(index)] = square_label(gamma)
            fiber_by_index[str(index)] = fiber_action(gamma)

    identified = len(time_indices) > 0
    pair_zero = identified
    if not identified:
        fiber_word = "n/a"
    else:
        grouped: dict[str, list[int]] = {}
        for index in time_indices:
            grouped.setdefault(fiber_by_index[str(index)], []).append(index)
        fiber_word = "; ".join(
            f"{kind} ({', '.join(str(index) for index in grouped[kind])})"
            for kind in ("Diagonal", "Off-diagonal", "Mixed")
            if kind in grouped
        )

    eye = np.eye(128, dtype=np.complex128)
    omega = eye.copy()
    for gamma in gammas:
        omega = omega @ gamma
    if not np.allclose(omega, omega.conj().T):
        omega = -1j * omega
    reality, reality_sign = tb.charge_conjugation(gammas)
    if reality_sign != 1 or frobenius(reality @ reality - eye) > 1e-8:
        raise SystemExit("C is not the +I intertwiner")
    if frobenius(omega @ omega - eye) > 1e-8:
        raise SystemExit("the Clifford volume does not square to +I")
    if frobenius(exhaust - omega @ reality) > 1e-8:
        raise SystemExit("E is not Ω C")
    symmetric: list[int] = []
    antisymmetric: list[int] = []
    for index, gamma in enumerate(gammas):
        if frobenius(gamma - gamma.T) <= 1e-8:
            symmetric.append(index)
        elif frobenius(gamma + gamma.T) <= 1e-8:
            antisymmetric.append(index)
        else:
            raise SystemExit(f"gamma {index} is neither symmetric nor antisymmetric")
    if symmetric != anticommute or antisymmetric != commute:
        raise SystemExit("symmetry sets do not match the brackets with E")
    five = [index for index in symmetric if index not in (11, 13)]
    if five != time_indices:
        raise SystemExit("the five-index list does not match the pair test")

    lines = [
        "# Ambient exhaust algebra",
        "",
        "AMBIENT 128D EXHAUST ALGEBRA - GAMMAS(14) - ZERO KNOBS",
        "",
        f"Number of ambient gammas anticommuting with E: {len(anticommute)}",
        "",
        f"Number of ambient gammas commuting with E: {len(commute)}",
        "",
        f"Ambient time candidate Γ_t identified? {'Yes' if identified else 'No'}",
        "",
        f"{{Γ_t, Γ_11}} = 0 and {{Γ_t, Γ_13}} = 0 in 128D? {'Yes' if pair_zero else 'No'}",
        "",
        f"Fiber action of Γ_t: {fiber_word}",
        "",
        "Rows promoted: 0",
        "",
        f"A_anticommute = {anticommute}",
        "",
        f"A_commute = {commute}",
        "",
        f"Index 11 is in A_anticommute: {'Yes' if index_11_in else 'No'}",
        "",
        f"Index 13 is in A_anticommute: {'Yes' if index_13_in else 'No'}",
        "",
        "E is the 128×128 matrix returned by ambient_exhaust(). The generators are triality_build.gammas(14). A bracket is counted as exact when its Frobenius norm is at most 1e-6.",
        "",
    ]
    if identified:
        lines.append(f"Indices t in A_anticommute with {{Γ_t, Γ_11}} = {{Γ_t, Γ_13}} = 0: {time_indices}")
        lines.append("")
        lines.append("Five generators meet the test. No unique generator is selected.")
        lines.append("")
        lines.append("AMBIENT GAMMA SOLVE - FIVE INDICES - ZERO KNOBS")
        lines.append("")
        lines.append("E = Ω C exactly. Ω is the Hermitian Clifford volume, Ω² = +I128. C² = +I128 and C Γ C⁻¹ = Γᵀ.")
        lines.append("")
        lines.append(f"Real-symmetric generators: {symmetric}. Imaginary-antisymmetric generators: {antisymmetric}.")
        lines.append("")
        lines.append(f"Solved list: {five}. Unique generator: No. Promotion candidate: No.")
        lines.append("")
        for index in time_indices:
            lines.append(
                f"Γ_{index}² = {time_squares[str(index)]}. "
                f"{{Γ_{index}, Γ_11}} = 0 and {{Γ_{index}, Γ_13}} = 0. "
                f"Fiber action on the (4, 32, 4, 32) decomposition: {fiber_by_index[str(index)]}."
            )
            lines.append("")
    else:
        lines += [
            "No ambient generator in A_anticommute anticommutes with both Γ_11 and Γ_13.",
            "",
        ]
    lines += [
        "M^4, Σ^5, and the cone add to 15. The fiber is Σ^5×T^{1,1}.",
        "",
        "C1 and C2 stay UNKNOWN. No coset is selected.",
        "",
        f"Baseline sha256: {baseline_hash}",
        "",
    ]
    payload = {
        "continuous_knobs": 0,
        "promoted": 0,
        "rows_promoted": 0,
        "baseline_sha256": baseline_hash,
        "locks_changed": 0,
        "exhaust_shape": [128, 128],
        "exhaust_frobenius_norm": exhaust_norm,
        "A_anticommute": anticommute,
        "A_commute": commute,
        "anticommutator_norms": anticommutator_norms,
        "commutator_norms": commutator_norms,
        "index_11_in_A_anticommute": index_11_in,
        "index_13_in_A_anticommute": index_13_in,
        "E_equals_omega_C": True,
        "omega_square": "+I128",
        "C_square": "+I128",
        "C_sign": reality_sign,
        "symmetric_indices": symmetric,
        "antisymmetric_indices": antisymmetric,
        "solved_indices": five,
        "unique_generator": False,
        "promotion_candidate": False,
        "time_candidate_indices": time_indices,
        "time_candidate_identified": identified,
        "pair_anticommutators_zero": pair_zero,
        "gamma_t_square": time_squares,
        "pair_norms": pair_norms,
        "fiber_action_by_index": fiber_by_index,
        "fiber_action": fiber_word,
        "C1": "UNKNOWN",
        "C2": "UNKNOWN",
        "coset_selected": None,
        "fiber": "Sigma5 x T^(1,1)",
        "sum_M4_Sigma5_cone": 15,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:28]))
    if sha256(BASELINE) != baseline_hash:
        raise SystemExit("baseline changed during the search")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
