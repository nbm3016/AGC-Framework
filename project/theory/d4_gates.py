"""Exact certificate for theory/4D_GATES.md.

Pauli arithmetic for the five-member sign family. Reads the isolate and both
baselines. Writes nothing. Does not fill dynamical_4d_eom.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pauli_proof as P

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "falsifier"
CORE = ROOT / "core" / "complete_baseline.json"
import sys

sys.path.insert(0, str(DATA))
from content_sha import CORE_BASELINE_SHA, WORK_BASELINE_SHA, content_sha256

WORK_SHA = WORK_BASELINE_SHA
CORE_SHA = CORE_BASELINE_SHA
PASSED: list[str] = []
PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
DISJOINT = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))


def check(name: str, ok: bool, detail: str = "") -> None:
    if not ok:
        raise SystemExit(f"FAIL {name}" + (f": {detail}" if detail else ""))
    PASSED.append(name)


def square_sign(op: P.Op) -> int:
    phase, letters = P.mul_op(op, op)
    if set(letters) != {"I"}:
        raise SystemExit(f"square left the scalars: {op}")
    if phase == 0:
        return 1
    if phase == 2:
        return -1
    raise SystemExit(f"square is not ±I: {op}")


def generators(timelike: int | None) -> list[P.Op]:
    gens = list(P.build_gammas(14)[10:14])
    if timelike is not None:
        gens[timelike] = P.scale(1, gens[timelike])
    return gens


def plane(gens: list[P.Op], a: int, b: int) -> P.Op:
    return P.mul_op(gens[a], gens[b])


def comm_sum(left: P.Op, right: P.Op) -> P.Sum:
    return P.from_op(P.mul_op(left, right)) - P.from_op(P.mul_op(right, left))


def sum_of(op: P.Op) -> P.Sum:
    return P.from_op(op)


def same(left: P.Sum, right: P.Sum) -> bool:
    return left.terms == right.terms


def symbol(gens: list[P.Op], momentum: tuple[int, int, int, int]) -> P.Sum:
    total = P.Sum()
    for coef, op in zip(momentum, gens, strict=True):
        if coef == 0:
            continue
        if coef != 1:
            raise SystemExit("this certificate only adds coefficients 0 and 1")
        total = total + P.from_op(op)
    return total


def expect_scalar(total: P.Sum, real: int, imag: int) -> bool:
    if len(total.terms) != 1:
        return False
    letters, coef = next(iter(total.terms.items()))
    return set(letters) == {"I"} and coef == P.G(real, imag)


def member_algebra(timelike: int | None) -> None:
    gens = generators(timelike)
    eta = [square_sign(op) for op in gens]
    label = "unmodified" if timelike is None else f"time {timelike}"
    if timelike is None:
        check(f"{label} signs", eta == [1, 1, 1, 1], str(eta))
    else:
        expect = [1, 1, 1, 1]
        expect[timelike] = -1
        check(f"{label} signs", eta == expect, str(eta))
    words = []
    for a, b in PAIRS:
        op = plane(gens, a, b)
        words.append(op[1])
        expect_sq = -eta[a] * eta[b]
        check(f"{label} L{a}{b} square", square_sign(op) == expect_sq)
    check(f"{label} six words", len(set(words)) == 6 and all(set(w) != {"I"} for w in words))
    for a in range(4):
        others = [n for n in range(4) if n != a]
        for i, b in enumerate(others):
            for c in others[i + 1 :]:
                left = plane(gens, a, b)
                right = plane(gens, a, c)
                got = comm_sum(left, right)
                target = sum_of(plane(gens, b, c)).scale(P.G(-2 * eta[a]))
                check(f"{label} bracket {a}:{b}{c}", same(got, target))
    for left_pair, right_pair in DISJOINT:
        got = comm_sum(plane(gens, *left_pair), plane(gens, *right_pair))
        check(f"{label} disjoint {left_pair}{right_pair}", got.is_zero())


def volumes() -> None:
    mj2 = (2, tuple("XXIIIII"))
    plain = generators(None)
    vol = (0, tuple("I" * 7))
    for op in plain:
        vol = P.mul_op(vol, op)
    check("unmodified volume is MJ2", vol == mj2)
    check("MJ2 squares to +I", square_sign(mj2) == 1)
    flipped = P.scale(1, mj2)
    for timelike in range(4):
        vol_t = (0, tuple("I" * 7))
        for op in generators(timelike):
            vol_t = P.mul_op(vol_t, op)
        check(f"time {timelike} volume is i MJ2", vol_t == flipped)
    check("i MJ2 squares to -I", square_sign(flipped) == -1)


def kernels() -> None:
    nulls = {
        0: (1, 1, 0, 0),
        1: (1, 1, 0, 0),
        2: (1, 0, 1, 0),
        3: (1, 0, 0, 1),
    }
    for timelike, momentum in nulls.items():
        gens = generators(timelike)
        total = symbol(gens, momentum)
        check(f"time {timelike} null square", (total * total).is_zero())
        anti = total * P.from_op(gens[timelike]) + P.from_op(gens[timelike]) * total
        check(f"time {timelike} null brace", expect_scalar(anti, -2, 0))
    eucl = symbol(generators(None), (1, 0, 0, 0))
    check("unmodified axis square", expect_scalar(eucl * eucl, 1, 0))
    off_cone = symbol(generators(0), (1, 0, 0, 0))
    check("time 0 at unit k0 squares to -I", expect_scalar(off_cone * off_cone, -1, 0))
    # 2 x_i = sum_j x_j has only the zero solution.
    matrix = [
        [Fraction(1 if i == j else -1) for j in range(4)]
        for i in range(4)
    ]
    rank = 0
    row = 0
    for col in range(4):
        pivot = next((i for i in range(row, 4) if matrix[i][col] != 0), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        scale = matrix[row][col]
        for j in range(col, 4):
            matrix[row][j] /= scale
        for i in range(4):
            if i == row or matrix[i][col] == 0:
                continue
            factor = matrix[i][col]
            for j in range(col, 4):
                matrix[i][j] -= factor * matrix[row][j]
        rank += 1
        row += 1
    check("only common null momentum is zero", rank == 4, str(rank))


def euclidean_copies() -> None:
    gens = generators(None)
    h = {pair: P.scale(1, plane(gens, *pair)) for pair in PAIRS}
    for pair, op in h.items():
        check(f"H{pair} squares to +I", square_sign(op) == 1)

    def add(pair: tuple[int, int], sign: int = 1) -> P.Sum:
        term = sum_of(h[pair])
        return term if sign == 1 else term.scale(P.G(-1))

    d1 = add((0, 1)) + add((2, 3))
    d2 = add((0, 2)) + add((1, 3), -1)
    d3 = add((0, 3)) + add((1, 2))
    e1 = add((0, 1)) + add((2, 3), -1)
    e2 = add((0, 2)) + add((1, 3))
    e3 = add((0, 3)) + add((1, 2), -1)
    cycles = (
        ((d1, d2, d3), -4, "A"),
        ((d2, d3, d1), -4, "A"),
        ((d3, d1, d2), -4, "A"),
        ((e1, e2, e3), 4, "B"),
        ((e2, e3, e1), 4, "B"),
        ((e3, e1, e2), 4, "B"),
    )
    for (left, mid, right), coef, name in cycles:
        got = left * mid - mid * left
        check(f"{name} doubled bracket", same(got, right.scale(P.G(0, coef))))
    for i, left in enumerate((d1, d2, d3)):
        for j, right in enumerate((e1, e2, e3)):
            check(f"A{i + 1} commutes with B{j + 1}", (left * right - right * left).is_zero())


def fibre_blind() -> None:
    gammas = P.build_gammas(14)
    blind = [i for i, op in enumerate(gammas) if set(op[1][2:]) == {"I"}]
    check("unique fibre-blind indices", blind == [10, 11, 12, 13], str(blind))
    words = ["".join(op[1][:2]) for op in gammas[10:14]]
    check("slow letters", words == ["XY", "XZ", "YI", "ZI"], str(words))


def locks_and_hashes() -> None:
    ratio = Fraction(9, 16)
    check("4 kappa = 9/4", 4 * ratio == Fraction(9, 4))
    check("4 kappa + 1 = 13/4", 4 * ratio + 1 == Fraction(13, 4))
    check("banned swap is false", 4 * ratio + 1 != Fraction(9, 4))
    isolate = json.loads((DATA / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    check("35 locks", len(locks) == 35, str(len(locks)))
    check("lock extras stay 0", all(item.get("extras") == 0 for item in locks))
    by_name = {item["name"]: item for item in locks}
    knob = by_name["continuous_knobs"]
    check("continuous_knobs is 0", knob.get("value") == 0 and knob.get("extras") == 0)
    iso = by_name["Iso_group"]
    check("isometry dimension 7", iso.get("dimension") == 7 and iso.get("stored_as") == "isometry")
    check("einstein is the 5-metric", by_name["EINSTEIN_SCALAR_G5"].get("value") == "Ric = 4 g; scalar = 20")
    check("triple is not a 4-metric", "Not a 4-metric" in by_name["TRIPLE_T11"].get("reading", ""))
    hol = by_name["CONE_HOLONOMY"]
    check("holonomy stays holonomy", hol.get("value") == "SU(3)" and hol.get("stored_as") == "holonomy")
    maps = {item["name"]: item for item in isolate["maps"]}
    slot = maps["dynamical_4d_eom"]
    check(
        "slot stays empty",
        slot.get("status") == "MAP" and slot.get("slot") == "empty" and slot.get("extras") == ["EOM"],
    )
    check("metric extra remains", maps["unique_g_mu_nu"].get("extras") == ["g_mu_nu"])
    work = content_sha256(DATA / "complete_baseline.json")
    core = content_sha256(CORE)
    check("working baseline hash", work == WORK_SHA, work)
    check("core baseline hash", core == CORE_SHA, core)


def main() -> int:
    fibre_blind()
    for timelike in (None, 0, 1, 2, 3):
        member_algebra(timelike)
    volumes()
    kernels()
    euclidean_copies()
    locks_and_hashes()
    print("D4 GATES CERTIFICATE PASS")
    print(f"lemmas {len(PASSED)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
