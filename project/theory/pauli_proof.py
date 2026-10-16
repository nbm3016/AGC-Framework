"""Exact certificate for theory/PAULI_PROOF.md.

Pauli arithmetic in the ring Z[i], then Gaussian rationals. No float is used
for a lemma. The last block compares the same operators to
triality_build.gammas(14), charge_conjugation, and boundary_project.ambient_exhaust.

This file reads the isolate and the baseline. It writes nothing.
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "falsifier"
sys.path.insert(0, str(ROOT))
from content_sha import WORK_BASELINE_SHA, content_sha256

BASELINE_SHA = WORK_BASELINE_SHA
PASSED: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    if not ok:
        raise SystemExit(f"FAIL {name}" + (f": {detail}" if detail else ""))
    PASSED.append(name)


class G:
    """Gaussian rational."""

    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = re if isinstance(re, Fraction) else Fraction(re)
        self.im = im if isinstance(im, Fraction) else Fraction(im)

    def __add__(self, other: G) -> G:
        return G(self.re + other.re, self.im + other.im)

    def __sub__(self, other: G) -> G:
        return G(self.re - other.re, self.im - other.im)

    def __neg__(self) -> G:
        return G(-self.re, -self.im)

    def __mul__(self, other: G) -> G:
        return G(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )

    def __truediv__(self, other: G) -> G:
        den = other.re * other.re + other.im * other.im
        return G(
            (self.re * other.re + self.im * other.im) / den,
            (self.im * other.re - self.re * other.im) / den,
        )

    def is_zero(self) -> bool:
        return self.re == 0 and self.im == 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, G) and self.re == other.re and self.im == other.im

    def __repr__(self) -> str:
        return f"{self.re}+{self.im}i"


PHASE = (G(1), G(0, 1), G(-1), G(0, -1))  # 1, i, -1, -i


def mul_letter(a: str, b: str) -> tuple[int, str]:
    if a == "I":
        return 0, b
    if b == "I":
        return 0, a
    if a == b:
        return 0, "I"
    cyc = {"X": 0, "Y": 1, "Z": 2}
    order = "XYZ"
    if (cyc[b] - cyc[a]) % 3 == 1:
        return 1, order[(cyc[a] + 2) % 3]
    return 3, order[(cyc[a] + 1) % 3]


Op = tuple[int, tuple[str, ...]]


def mul_op(a: Op, b: Op) -> Op:
    phase = (a[0] + b[0]) % 4
    letters = []
    for x, y in zip(a[1], b[1], strict=True):
        extra, letter = mul_letter(x, y)
        phase = (phase + extra) % 4
        letters.append(letter)
    return phase, tuple(letters)


def ident(n: int) -> Op:
    return 0, tuple("I" * n)


def kron_left(letter: str, op: Op) -> Op:
    return op[0], (letter,) + op[1]


def scale(phase: int, op: Op) -> Op:
    return (op[0] + phase) % 4, op[1]


def smul_int(phase: int, re: int, im: int) -> tuple[int, int]:
    if phase == 0:
        return re, im
    if phase == 1:
        return -im, re
    if phase == 2:
        return -re, -im
    return im, -re


def act_index(letters: tuple[str, ...], phase: int, index: int, nq: int) -> tuple[int, int]:
    out = index
    ph = phase
    for q, letter in enumerate(letters):
        shift = nq - 1 - q
        bit = (index >> shift) & 1
        if letter == "I":
            continue
        if letter == "Z":
            if bit:
                ph = (ph + 2) % 4
        elif letter == "X":
            out ^= 1 << shift
        else:
            out ^= 1 << shift
            ph = (ph + (1 if bit == 0 else 3)) % 4
    return out, ph


def apply_int(op: Op, vec: list[tuple[int, int]], nq: int) -> list[tuple[int, int]]:
    dim = 1 << nq
    out = [(0, 0)] * dim
    phase, letters = op
    for i, (re, im) in enumerate(vec):
        if re == 0 and im == 0:
            continue
        j, ph = act_index(letters, phase, i, nq)
        cre, cim = smul_int(ph, re, im)
        out[j] = (out[j][0] + cre, out[j][1] + cim)
    return out


def comm_sign(a: Op, b: Op) -> int:
    ab = mul_op(a, b)
    ba = mul_op(b, a)
    if ab[1] != ba[1]:
        raise SystemExit("product of Pauli strings left the Pauli group")
    diff = (ab[0] - ba[0]) % 4
    if diff == 0:
        return 1
    if diff == 2:
        return -1
    raise SystemExit(f"neither commute nor anticommute: {a} {b}")


def squares_to(op: Op, phase: int) -> bool:
    sq = mul_op(op, op)
    return sq[0] == phase and set(sq[1]) == {"I"}


def build_gammas(n: int) -> list[Op]:
    """Same recursion as triality_build.gammas, in exact Pauli form. n even."""
    if n % 2:
        raise SystemExit("certificate builds the even lift only")
    gs = [(0, ("X",)), (0, ("Y",))]
    while len(gs) < n:
        eye = ident(len(gs[0][1]))
        lifted = [kron_left("X", g) for g in gs]
        lifted.append(kron_left("Y", eye))
        lifted.append(kron_left("Z", eye))
        gs = lifted
    return gs


def build_charge(nq: int) -> tuple[Op, int]:
    """Same recursion as triality_build.charge_conjugation on 2^nq."""
    c: Op = (0, ("X",))
    eps = 1
    while len(c[1]) < nq:
        if eps == 1:
            c = kron_left("Y", c)
            eps = -1
        else:
            c = kron_left("Z", c)
            eps = 1
    return c, eps


def closed_gamma(k: int) -> Op:
    if k == 0:
        return 0, tuple("X" * 7)
    if k == 1:
        return 0, tuple("X" * 6) + ("Y",)
    if k % 2 == 0:
        t, letter = k // 2, "Y"
    else:
        t, letter = (k - 1) // 2, "Z"
    q = 6 - t
    letters = ["I"] * 7
    for j in range(q):
        letters[j] = "X"
    letters[q] = letter
    return 0, tuple(letters)


def y_count(op: Op) -> int:
    return sum(letter == "Y" for letter in op[1])


class Sum:
    def __init__(self, terms: dict[tuple[str, ...], G] | None = None):
        self.terms = dict(terms or {})

    def add_op(self, op: Op, coef: G | None = None) -> None:
        coef = PHASE[op[0]] if coef is None else coef * PHASE[op[0]]
        self.terms[op[1]] = self.terms.get(op[1], G()) + coef
        if self.terms[op[1]].is_zero():
            del self.terms[op[1]]

    def __add__(self, other: Sum) -> Sum:
        out = Sum(self.terms)
        for key, coef in other.terms.items():
            out.terms[key] = out.terms.get(key, G()) + coef
            if out.terms[key].is_zero():
                del out.terms[key]
        return out

    def __sub__(self, other: Sum) -> Sum:
        return self + Sum({key: -coef for key, coef in other.terms.items()})

    def __mul__(self, other: Sum) -> Sum:
        out = Sum()
        for ka, ca in self.terms.items():
            for kb, cb in other.terms.items():
                phase, letters = mul_op((0, ka), (0, kb))
                out.terms[letters] = out.terms.get(letters, G()) + (ca * cb * PHASE[phase])
                if out.terms[letters].is_zero():
                    del out.terms[letters]
        return out

    def scale(self, coef: G) -> Sum:
        return Sum({key: coef * val for key, val in self.terms.items()})

    def is_zero(self) -> bool:
        return not self.terms


def from_op(op: Op) -> Sum:
    s = Sum()
    s.add_op(op)
    return s


def rank_of(rows: list[list[G]]) -> int:
    if not rows:
        return 0
    matrix = [row[:] for row in rows]
    m = len(matrix)
    n = len(matrix[0])
    row = 0
    pivots = 0
    for col in range(n):
        pivot = next((i for i in range(row, m) if not matrix[i][col].is_zero()), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        piv = matrix[row][col]
        for j in range(col, n):
            matrix[row][j] = matrix[row][j] / piv
        for i in range(m):
            if i == row or matrix[i][col].is_zero():
                continue
            factor = matrix[i][col]
            for j in range(col, n):
                matrix[i][j] = matrix[i][j] - factor * matrix[row][j]
        pivots += 1
        row += 1
        if row == m:
            break
    return pivots


def op_matrix(op: Op) -> list[list[G]]:
    nq = len(op[1])
    dim = 1 << nq
    cols = []
    for i in range(dim):
        basis = [(0, 0)] * dim
        basis[i] = (1, 0)
        image = apply_int(op, basis, nq)
        cols.append([G(re, im) for re, im in image])
    # matrix[row][col]
    return [[cols[c][r] for c in range(dim)] for r in range(dim)]


def anticommutant_nullity(generators: list[list[list[G]]]) -> int:
    dim = len(generators[0])
    rows: list[list[G]] = []
    for gen in generators:
        for a in range(dim):
            for b in range(dim):
                row = [G() for _ in range(dim * dim)]
                for k in range(dim):
                    # (TG + GT)[a,b] = sum_k T[a,k] G[k,b] + G[a,k] T[k,b]
                    row[a * dim + k] = row[a * dim + k] + gen[k][b]
                    row[k * dim + b] = row[k * dim + b] + gen[a][k]
                rows.append(row)
    rank = rank_of(rows)
    return dim * dim - rank


def commutant_nullity(generators: list[list[list[G]]]) -> int:
    dim = len(generators[0])
    rows = []
    for gen in generators:
        for a in range(dim):
            for b in range(dim):
                row = [G() for _ in range(dim * dim)]
                for k in range(dim):
                    # (TG - GT)[a,b]
                    row[a * dim + k] = row[a * dim + k] + gen[k][b]
                    row[k * dim + b] = row[k * dim + b] - gen[a][k]
                rows.append(row)
    return dim * dim - rank_of(rows)


def mat_vec_entries(matrix: list[list[G]]) -> list[G]:
    return [value for row in matrix for value in row]


def mul_matrix(a: list[list[G]], b: list[list[G]]) -> list[list[G]]:
    n = len(a)
    out = [[G() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k].is_zero():
                continue
            for j in range(n):
                out[i][j] = out[i][j] + a[i][k] * b[k][j]
    return out


def normalize(vec: list[tuple[int, int]]) -> list[G]:
    scale = next((G(re, im) for re, im in vec if re or im), None)
    if scale is None:
        raise SystemExit("zero vector")
    return [G() if re == 0 and im == 0 else G(re, im) / scale for re, im in vec]


def joint_vector(ops: list[Op], signs: tuple[int, ...]) -> list[G]:
    nq = len(ops[0][1])
    dim = 1 << nq
    for start in range(dim):
        vec = [(0, 0)] * dim
        vec[start] = (1, 0)
        for op, sign in zip(ops, signs, strict=True):
            image = apply_int(op, vec, nq)
            if sign == 1:
                vec = [(vec[i][0] + image[i][0], vec[i][1] + image[i][1]) for i in range(dim)]
            else:
                vec = [(vec[i][0] - image[i][0], vec[i][1] - image[i][1]) for i in range(dim)]
        if any(re or im for re, im in vec):
            return normalize(vec)
    raise SystemExit(f"no joint line for {signs}")


def apply_g(op: Op, vec: list[G]) -> list[G]:
    nq = len(op[1])
    dim = 1 << nq
    raw = [(0, 0)] * dim
    for i, value in enumerate(vec):
        if value.is_zero():
            continue
        # clear this coordinate to an integer by using a common denominator later
        raw[i] = (value.re.numerator, value.im.numerator)  # placeholder, replaced below
    # Exact path: write every coordinate over a common denominator.
    den = 1
    for value in vec:
        den = np.lcm(den, int(value.re.denominator))
        den = np.lcm(den, int(value.im.denominator))
    ints = []
    for value in vec:
        ints.append(
            (
                int(value.re * den),
                int(value.im * den),
            )
        )
    image = apply_int(op, ints, nq)
    return [G(Fraction(re, den), Fraction(im, den)) for re, im in image]


def image_rank(vectors: list[list[tuple[int, int]]]) -> int:
    if not vectors:
        return 0
    rows = [[G(re, im) for re, im in vec] for vec in vectors]
    # drop exact zero rows
    rows = [row for row in rows if any(not value.is_zero() for value in row)]
    return rank_of(rows)


def span_images(op_list: list[Op], nq: int) -> list[list[tuple[int, int]]]:
    """Images of (product of ops) on every basis vector. Used as a spanning set."""
    dim = 1 << nq
    rows = []
    for start in range(dim):
        vec = [(0, 0)] * dim
        vec[start] = (1, 0)
        for op in op_list:
            vec = apply_int(op, vec, nq)
        rows.append(vec)
    return rows


def main() -> int:
    gammas = build_gammas(14)
    check("lift length", len(gammas) == 14 and all(len(g[1]) == 7 for g in gammas))
    check(
        "closed form",
        all(gammas[k] == closed_gamma(k) for k in range(14)),
        str([(k, gammas[k][1]) for k in range(14) if gammas[k] != closed_gamma(k)]),
    )

    hermitian = all(g[0] % 2 == 0 for g in gammas)
    square = all(squares_to(g, 0) for g in gammas)
    anti = all(comm_sign(gammas[i], gammas[j]) == -1 for i in range(14) for j in range(i))
    check("clifford relations", hermitian and square and anti)

    # Distinct nonempty subset products are traceless, hence independent:
    # checked structurally by the square/anticommutation hypotheses above,
    # and directly for the full product below. Independence of all 2^14
    # monomials is the trace argument in the proof; here the generators'
    # relations are the hypotheses of that argument.
    check("fourteen generators square to +I and anticommute", square and anti)

    m = (0, ("Y", "Z"))
    b11 = (0, ("X", "Z"))
    b13 = (0, ("Z", "I"))
    j1 = (0, ("Z", "X"))
    j2 = (2, ("Z", "Y"))  # - Z Y
    j3 = (2, ("I", "Z"))  # - I Z
    product = mul_op(mul_op(m, b11), b13)
    check("M B11 B13 = -i I", product == (3, ("I", "I")))
    check(
        "face squares and anticommutes",
        all(squares_to(op, 0) for op in (m, b11, b13))
        and comm_sign(m, b11) == -1
        and comm_sign(m, b13) == -1
        and comm_sign(b11, b13) == -1,
    )
    check(
        "flow triple",
        all(squares_to(op, 0) for op in (j1, j2, j3))
        and mul_op(j1, j2) == scale(1, j3)
        and all(comm_sign(j, f) == 1 for j in (j1, j2, j3) for f in (m, b11, b13))
        and comm_sign(j1, j2) == -1
        and comm_sign(j2, j3) == -1
        and comm_sign(j3, j1) == -1,
    )
    mats = [op_matrix(op) for op in (m, b11, b13)]
    check("anticommutant is 0", anticommutant_nullity(mats) == 0)
    check("commutant dimension is 4", commutant_nullity(mats) == 4)

    face = [ident(2), m, b11, b13]
    flow = [ident(2), j1, j2, j3]
    products = [mul_matrix(op_matrix(a), op_matrix(b)) for a in face for b in flow]
    check("face times flow spans M4", rank_of([mat_vec_entries(p) for p in products]) == 16)

    expected_slow = {
        (1, 1): [G(1), G(0, -1), G(0, 1), G(-1)],
        (1, -1): [G(1), G(0, 1), G(0, 1), G(1)],
        (-1, 1): [G(1), G(0, -1), G(0, -1), G(1)],
        (-1, -1): [G(1), G(0, 1), G(0, -1), G(-1)],
    }
    check(
        "four slow lines",
        all(joint_vector([m, j2], sig) == vals for sig, vals in expected_slow.items()),
    )

    mj2 = mul_op(m, j2)
    check("M J2 = -XX", mj2 == (2, ("X", "X")))
    mj1 = mul_op(m, j1)
    mj3 = mul_op(m, j3)
    check("M J1 = -XY", mj1 == (2, ("X", "Y")))
    check("M J3 = -YI", mj3 == (2, ("Y", "I")))

    def split(op: Op) -> tuple[Op, Op]:
        return (op[0], op[1][:2]), (0, op[1][2:])

    for k in (0, 3, 5, 7, 9):
        slow, fast = split(gammas[k])
        check(
            f"gamma {k} slow is -M J2",
            slow == (0, ("X", "X")) and fast[0] == 0,
        )
    for k in (1, 2, 4, 6, 8):
        slow, fast = split(gammas[k])
        # Γ = XX ⊗ (Y-string) = (i M J2) ⊗ (i Y-string)
        # XX = - M J2, so i M J2 = -i XX, phase of -i XX is 3 on XX.
        check(
            f"gamma {k} has slow letters XX",
            slow == (0, ("X", "X")) and "Y" in fast[1],
        )
        i_mj2 = scale(1, mj2)  # i * (-XX) = -i XX, phase 3
        i_fast = (1, fast[1])
        rebuilt = ( (i_mj2[0] + i_fast[0]) % 4, i_mj2[1] + i_fast[1] )
        check(f"gamma {k} phase rebuild", rebuilt == gammas[k])
    check(
        "gamma 10 is -(M J1) tensor I",
        scale(2, mj1) == (0, ("X", "Y")) and gammas[10] == (0, ("X", "Y") + ("I",) * 5),
    )
    check("gamma 11 is B11 tensor I", gammas[11] == (b11[0], b11[1] + ("I",) * 5))
    check(
        "gamma 12 is -(M J3) tensor I",
        scale(2, mj3) == (0, ("Y", "I")) and gammas[12] == (0, ("Y", "I") + ("I",) * 5),
    )
    check("gamma 13 is B13 tensor I", gammas[13] == (b13[0], b13[1] + ("I",) * 5))

    check(
        "fast +I strings",
        (0, gammas[0][1][2:]) == (0, tuple("XXXXX"))
        and (0, gammas[3][1][2:]) == (0, tuple("XXXZI"))
        and (0, gammas[5][1][2:]) == (0, tuple("XXZII"))
        and (0, gammas[7][1][2:]) == (0, tuple("XZIII"))
        and (0, gammas[9][1][2:]) == (0, tuple("ZIIII")),
    )
    check(
        "fast -I strings",
        all((1, gammas[k][1][2:])[1] == expected for k, expected in (
            (1, tuple("XXXXY")),
            (2, tuple("XXXYI")),
            (4, tuple("XXYII")),
            (6, tuple("XYIII")),
            (8, tuple("YIIII")),
        )),
    )
    check(
        "fast spectators are I",
        all(gammas[k][1][2:] == tuple("IIIII") for k in (10, 11, 12, 13)),
    )

    f_plus = [(0, gammas[k][1][2:]) for k in (0, 3, 5, 7, 9)]
    f_minus = [(1, gammas[k][1][2:]) for k in (1, 2, 4, 6, 8)]
    check("five +I square and anticommute", all(squares_to(op, 0) for op in f_plus) and all(
        comm_sign(f_plus[i], f_plus[j]) == -1 for i in range(5) for j in range(i)
    ))
    check("five -I square to -I and anticommute with everyone in the ten", all(
        squares_to(op, 2) for op in f_minus
    ) and all(comm_sign(a, b) == -1 for a in f_minus for b in f_minus + f_plus if a != b))

    def subset_supports(gens: list[Op]) -> int:
        current = [ident(len(gens[0][1]))]
        for gen in gens:
            current = current + [mul_op(word, gen) for word in current]
        return len({word[1] for word in current})

    check("fourteen monomials basis M128", subset_supports(gammas) == 16384)
    check("ten fast monomials basis M32", subset_supports(f_plus + f_minus) == 1024)

    # Volume, C, E.
    prod = ident(7)
    for g in gammas:
        prod = mul_op(prod, g)
    check("ordered product is -i XXXXXXZ", prod == (3, tuple("XXXXXXZ")))
    # Not Hermitian (phase odd). Hermitianize by -i, phase +3.
    omega = scale(3, prod)
    check("Omega is -XXXXXXZ", omega == (2, tuple("XXXXXXZ")))
    charge, eps = build_charge(7)
    check("C is ZYZYZYX and eps is +1", charge == (0, tuple("ZYZYZYX")) and eps == 1)
    check("C squared is I", squares_to(charge, 0))
    check("Omega squared is I", squares_to(omega, 0))
    transpose_ok = True
    for g in gammas:
        sign = comm_sign(charge, g)
        want = 1 if y_count(g) % 2 == 0 else -1
        # C G C = sign * G, and G^T = want * G.
        if sign != want:
            transpose_ok = False
    check("C intertwines transpose with one sign", transpose_ok)

    exhaust_op = mul_op(omega, charge)
    check("E = Omega C = -i YZYZYZY", exhaust_op == (3, tuple("YZYZYZY")))
    check("E squared is -I", squares_to(exhaust_op, 2))
    check("Omega and C anticommute", comm_sign(omega, charge) == -1)

    eye = from_op(ident(7))
    omega_s = from_op(omega)
    charge_s = from_op(charge)
    mode = (eye + omega_s).scale(G(Fraction(1, 2)))
    bracket = (mode * omega_s - omega_s * mode) + (omega_s * charge_s - charge_s * omega_s) + (
        charge_s * mode - mode * charge_s
    )
    check("ambient bracket equals E", (bracket - from_op(exhaust_op)).is_zero())

    e_s = from_op(exhaust_op)
    check(
        "triple table",
        (omega_s * charge_s - e_s).is_zero()
        and (charge_s * omega_s + e_s).is_zero()
        and (omega_s * e_s - charge_s).is_zero()
        and (e_s * omega_s + charge_s).is_zero()
        and (e_s * charge_s - omega_s).is_zero()
        and (charge_s * e_s + omega_s).is_zero()
        and (omega_s * omega_s - eye).is_zero()
        and (charge_s * charge_s - eye).is_zero()
        and (e_s * e_s + eye).is_zero(),
    )
    # Four strings independent: distinct Pauli supports.
    supports = {ident(7)[1], omega[1], charge[1], exhaust_op[1]}
    check("span of I, Omega, C, E has four supports", len(supports) == 4)

    # Address.
    addr_m = (0, tuple("YZIIIII"))
    addr_j = (2, tuple("ZYIIIII"))
    addr_d = (0, tuple("IIIYZII"))
    addr_b = (0, tuple("IIIZYII"))
    sigma = (2, tuple("IIYZYZY"))
    addr_a = (0, tuple("IIIIIZY"))
    addr_c = (0, tuple("IIIIIYX"))
    address = [addr_m, addr_j, addr_a, addr_b, addr_c, addr_d, sigma]
    check("address squares to I", all(squares_to(op, 0) for op in address))
    check(
        "address bits commute",
        all(comm_sign(address[i], address[j]) == 1 for i in range(7) for j in range(i)),
    )
    check("M J2 = -XXIIIII", mul_op(addr_m, addr_j) == (2, tuple("XXIIIII")))
    check("D B = IIIXXII", mul_op(addr_d, addr_b) == (0, tuple("IIIXXII")))
    check("A C = -IIIIIXZ", mul_op(addr_a, addr_c) == (2, tuple("IIIIIXZ")))
    check(
        "three local products commute with Sigma and each other",
        all(
            comm_sign(prod_op, sigma) == 1
            for prod_op in (
                mul_op(addr_m, addr_j),
                mul_op(addr_d, addr_b),
                mul_op(addr_a, addr_c),
            )
        ),
    )
    # No nonempty product of the seven is scalar.
    independent = True
    for mask in range(1, 128):
        acc = ident(7)
        for bit in range(7):
            if mask & (1 << bit):
                acc = mul_op(acc, address[bit])
        if set(acc[1]) == {"I"}:
            independent = False
            break
    check("128 address characters are independent", independent)

    check("E equals i times M times Sigma", scale(1, mul_op(addr_m, sigma)) == exhaust_op)

    # Gamma 8 is the product of five address bits.
    g8_prod = addr_m
    for extra in (addr_j, addr_a, addr_b, sigma):
        g8_prod = mul_op(g8_prod, extra)
    check("Gamma 8 = M J2 A B Sigma", g8_prod == gammas[8])

    flips = {
        0: {4, 6},
        1: {2},
        2: {2},
        3: {4, 6},
        4: {3},
        5: {5, 6},
        6: {3},
        7: {5, 6},
        8: set(),
        9: {6},
        10: {1},
        11: {0},
        12: {1},
        13: {0},
    }
    # address index: M J A B C D Sigma = 0..6
    flip_ok = True
    for k in range(14):
        got = {i for i in range(7) if comm_sign(gammas[k], address[i]) == -1}
        if got != flips[k]:
            flip_ok = False
            break
    check("flip table", flip_ok)

    twins = {
        (11, 13): scale(3, addr_m),  # -i M
        (10, 12): scale(3, addr_j),
        (1, 2): scale(1, addr_a),
        (4, 6): scale(1, addr_b),
        (0, 3): scale(3, addr_c),
        (5, 7): scale(3, addr_d),
    }
    check(
        "twin products",
        all(mul_op(gammas[i], gammas[j]) == expect for (i, j), expect in twins.items()),
    )

    one_qubit = [
        (12, 13, 1, 0),  # i X on qubit 0
        (10, 11, 1, 1),
        (8, 9, 1, 2),
        (6, 7, 1, 3),
        (4, 5, 1, 4),
        (2, 3, 1, 5),
        (0, 1, 3, 6),  # i Z is phase 1 on Z? X*Y=iZ so phase 1, letter Z. NOT phase 3.
    ]
    built = []
    for i, j, _ph, qubit in one_qubit:
        built.append((mul_op(gammas[i], gammas[j]), qubit))
    expect_letters = []
    for qubit, letter in enumerate("XXXXXXZ"):
        letters = ["I"] * 7
        letters[qubit] = letter
        expect_letters.append((1, tuple(letters)))  # all of them are i times that letter
    check(
        "one-qubit operators",
        all(got == exp for (got, _q), exp in zip(built, expect_letters, strict=True)),
    )
    sheet_comm = []
    for (op, _q), qubit in zip(built, range(7)):
        sheet_comm.append(comm_sign(op, sigma))
    check(
        "sheet commutes on qubits 1-2 and anticommutes from qubit 3",
        sheet_comm == [1, 1, -1, -1, -1, -1, -1],
    )

    # Orders.
    check(
        "orders 2, 2, 2, 4",
        all(squares_to(g, 0) for g in gammas)
        and squares_to(omega, 0)
        and squares_to(charge, 0)
        and squares_to(exhaust_op, 2)
        and mul_op(mul_op(exhaust_op, exhaust_op), mul_op(exhaust_op, exhaust_op)) == ident(7),
    )

    # Phases in the first-nonzero-amplitude = 1 gauge.
    def ledger_phase(k: int, signs: tuple[int, ...]) -> G:
        s_m, s_j, s_a, s_b, s_c, s_d, s = signs
        real = {
            0: s_m * s_j * s_a * s_b * s_c * s,
            2: -s_m * s_j * s_b * s_c * s,
            4: s_m * s_j * s_d,
            5: s_m * s_j,
            8: s_m * s_j * s_a * s_b * s,
            9: s_m * s_j * s_b * s_d,
            12: 1,
            13: -s_j,
        }
        imag = {
            1: s_m * s_j * s_a * s_b * s_c * s,
            3: -s_m * s_j * s_a * s_b * s,
            6: s_m * s_j * s_b * s_d,
            7: -s_m * s_j * s_d,
            10: s_j,
            11: -s_m * s_j,
        }
        if k in real:
            return G(real[k])
        return G(0, imag[k])

    lines: dict[tuple[int, ...], list[G]] = {}
    for mask in range(128):
        signs = tuple(-1 if mask & (1 << bit) else 1 for bit in range(7))
        lines[signs] = joint_vector(address, signs)

    def measured_phase(k: int, signs: tuple[int, ...]) -> G:
        image = apply_g(gammas[k], lines[signs])
        target_signs = tuple(-signs[i] if i in flips[k] else signs[i] for i in range(7))
        target = lines[target_signs]
        ratio = None
        for left, right in zip(image, target, strict=True):
            if right.is_zero():
                if not left.is_zero():
                    raise SystemExit(f"gamma {k} missed the flipped line at {signs}")
                continue
            got = left / right
            if ratio is None:
                ratio = got
            elif got != ratio:
                raise SystemExit(f"gamma {k} is not a scalar on {signs}")
        if ratio is None:
            raise SystemExit("empty line")
        return ratio

    # Canonical gauge: each line is scaled so its first nonzero amplitude is 1.
    # A phase is a constant fourth root times a product of source signs.
    monomial_ok = True
    monomial_detail = ""
    canonical: dict[int, tuple[G, tuple[int, ...]]] = {}
    all_plus = (1, 1, 1, 1, 1, 1, 1)
    for k in range(14):
        const = measured_phase(k, all_plus)
        mask_bits = []
        for bit in range(7):
            flipped = list(all_plus)
            flipped[bit] = -1
            other = measured_phase(k, tuple(flipped))
            # If the phase contains this source sign, flipping it flips the phase.
            if other != const:
                if other != -const and other != const:
                    # fourth-root constants can pick up only a sign from a ±1 character
                    monomial_ok = False
                    monomial_detail = f"k={k} bit={bit} const={const} other={other}"
                    break
                if other == -const:
                    mask_bits.append(bit)
        if not monomial_ok:
            break
        canonical[k] = (const, tuple(mask_bits))
        for mask in range(128):
            signs = tuple(-1 if mask & (1 << bit) else 1 for bit in range(7))
            predict = const
            for bit in mask_bits:
                if signs[bit] == -1:
                    predict = -predict
            if measured_phase(k, signs) != predict:
                monomial_ok = False
                monomial_detail = f"k={k} signs={signs}"
                break
        if not monomial_ok:
            break
    check("canonical phases are monomials", monomial_ok, monomial_detail)

    # The ledger table is the same projective action if a rephasing of the
    # lines carries one table onto the other.
    alpha: dict[tuple[int, ...], G] = {all_plus: G(1)}
    coboundary = True
    coboundary_detail = ""
    stack = [all_plus]
    while stack and coboundary:
        signs = stack.pop()
        for k in range(14):
            target = tuple(-signs[i] if i in flips[k] else signs[i] for i in range(7))
            ratio = measured_phase(k, signs) / ledger_phase(k, signs)
            predicted = alpha[signs] * ratio
            if target in alpha:
                if alpha[target] != predicted:
                    coboundary = False
                    coboundary_detail = f"k={k} {signs} -> {target}"
                    break
            else:
                alpha[target] = predicted
                stack.append(target)
    check(
        "ledger phases match the canonical gauge up to line rephasing",
        coboundary and len(alpha) == 128,
        coboundary_detail or f"reached {len(alpha)}",
    )
    def quadratic_sign(signs: tuple[int, ...]) -> G:
        x = tuple(0 if sign == 1 else 1 for sign in signs)
        quad = (
            x[0] + x[5] + x[6] + x[0] * x[1] + x[2] * x[3] + x[2] * x[5] + x[3] * x[6] + x[5] * x[6]
        ) % 2
        return G(1) if quad == 0 else G(-1)

    check(
        "line rephasing is the quadratic sign",
        all(alpha[signs] == quadratic_sign(signs) for signs in alpha),
    )

    # Eigenvalue of E.
    e_ok = True
    for signs, vec in lines.items():
        image = apply_g(exhaust_op, vec)
        want = G(0, signs[0] * signs[6])  # i * sM * S
        if any(image[i] != want * vec[i] for i in range(128)):
            e_ok = False
            break
    check("E acts by i sM S", e_ok)

    # Fast geometry on 5 qubits.
    f1, f2, f4, f6, f8 = f_minus
    f0, f3, f5, f7, f9 = f_plus
    a_fast = scale(1, mul_op(f1, f2))
    b_fast = scale(1, mul_op(f4, f6))
    c_fast = scale(1, mul_op(f0, f3))
    d_fast = scale(1, mul_op(f5, f7))
    check("A,B,C,D square to +I", all(squares_to(op, 0) for op in (a_fast, b_fast, c_fast, d_fast)))
    e32 = f1
    for extra in (f2, f4, f6, f8):
        e32 = mul_op(e32, extra)
    check("E32 squared is -I", squares_to(e32, 2))
    # Sigma_fast = -i E32, string -YZYZY.
    sigma_fast = scale(3, e32)
    check("Sigma fast is -YZYZY", sigma_fast == (2, tuple("YZYZY")))

    def plus_i_basis() -> list[list[G]]:
        # Image of (E32 + i I). Rank 16.
        nq = 5
        rows = []
        plus = scale(1, ident(5))
        for start in range(32):
            vec = [(0, 0)] * 32
            vec[start] = (1, 0)
            image = apply_int(e32, vec, nq)
            eye_image = apply_int(plus, vec, nq)
            rows.append(
                [
                    G(image[i][0] + eye_image[i][0], image[i][1] + eye_image[i][1])
                    for i in range(32)
                ]
            )
        # Row-reduce and keep pivot rows as a basis, but the raw rows already
        # span. Reduce to independent rows.
        return independent_rows(rows)

    def independent_rows(rows: list[list[G]]) -> list[list[G]]:
        matrix = [row[:] for row in rows]
        m = len(matrix)
        n = len(matrix[0])
        row = 0
        kept = []
        for col in range(n):
            pivot = next((i for i in range(row, m) if not matrix[i][col].is_zero()), None)
            if pivot is None:
                continue
            matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
            piv = matrix[row][col]
            for j in range(n):
                matrix[row][j] = matrix[row][j] / piv
            for i in range(m):
                if i == row or matrix[i][col].is_zero():
                    continue
                factor = matrix[i][col]
                for j in range(n):
                    matrix[i][j] = matrix[i][j] - factor * matrix[row][j]
            kept.append(matrix[row][:])
            row += 1
            if row == m:
                break
        return kept

    plus_basis = plus_i_basis()
    check("+i space of E32 has dimension 16", len(plus_basis) == 16)
    f8_ok = True
    ab = mul_op(a_fast, b_fast)
    minus_i_ab = scale(3, ab)  # -i A B
    for vec_g in plus_basis:
        # compare F8 v and -i A B v
        raw = []
        den = 1
        for value in vec_g:
            den = int(np.lcm(den, int(value.re.denominator)))
            den = int(np.lcm(den, int(value.im.denominator)))
        ints = [(int(value.re * den), int(value.im * den)) for value in vec_g]
        left = apply_int(f8, ints, 5)
        right = apply_int(minus_i_ab, ints, 5)
        if left != right:
            f8_ok = False
            break
    check("F8 = -i A B on the +i space", f8_ok)

    # Ten-step walk from the first +i basis vector.
    seed_g = plus_basis[0]
    den = 1
    for value in seed_g:
        den = int(np.lcm(den, int(value.re.denominator)))
        den = int(np.lcm(den, int(value.im.denominator)))
    walk_ops = [f0, f3, f5, f7, f9, f1, f2, f4, f6, f8]
    current = [(int(value.re * den), int(value.im * den)) for value in seed_g]
    positions = []
    for op in walk_ops:
        current = apply_int(op, current, 5)
        positions.append(current)
    ten_rank = image_rank(positions)
    check("ten position vectors have rank 7", ten_rank == 7, str(ten_rank))

    def subset_orbit_rank(ops: list[Op], seed: list[tuple[int, int]]) -> int:
        rows = []
        for mask in range(1 << len(ops)):
            vec = seed
            for bit, op in enumerate(ops):
                if mask & (1 << bit):
                    vec = apply_int(op, vec, 5)
            rows.append(vec)
        return image_rank(rows)

    seed_int = [(int(value.re * den), int(value.im * den)) for value in seed_g]
    orbit_ranks = [subset_orbit_rank(walk_ops[:r], seed_int) for r in range(1, 11)]
    check(
        "subset orbit doubles through 32 at the fifth generator",
        orbit_ranks == [2, 4, 8, 16, 32, 32, 32, 32, 32, 32],
        str(orbit_ranks),
    )

    # Four rooms: joint signs of A and B inside +i, dimension 4 each.
    room_dims = []
    for s_a in (1, -1):
        for s_b in (1, -1):
            rows = []
            for start in range(32):
                vec = [(1, 0) if i == start else (0, 0) for i in range(32)]
                for op, sign in ((a_fast, s_a), (b_fast, s_b), (e32, None)):
                    image = apply_int(op, vec, 5)
                    if sign is None:
                        # E32 - i I = 0 on the kernel we want. Use E32 + i I? 
                        # Eigenvalue +i means (E32 - i I)v=0, projector proportional
                        # to (E32 + i I) only if we solve (E32 - i)(E32 + i)=E32^2+I=0.
                        # (E32 + i I) v = 2 i v on +i, and 0 on -i.
                        plus = apply_int(scale(1, ident(5)), vec, 5)
                        vec = [
                            (image[i][0] + plus[i][0], image[i][1] + plus[i][1]) for i in range(32)
                        ]
                    else:
                        vec = [
                            (vec[i][0] + sign * image[i][0], vec[i][1] + sign * image[i][1])
                            for i in range(32)
                        ]
                rows.append(vec)
            room_dims.append(image_rank(rows))
    check("four rooms have dimension 4", room_dims == [4, 4, 4, 4], str(room_dims))

    # Sixteen lines of the +i space, and the F9 / C32 identity.
    c32 = f0
    for extra in (f3, f5, f7, f9):
        c32 = mul_op(c32, extra)
    check("C32 = -ZYZYX", c32 == (2, tuple("ZYZYX")))
    line_ok = True
    line_count = 0
    for mask in range(16):
        signs4 = tuple(-1 if mask & (1 << bit) else 1 for bit in range(4))
        # Joint of A,B,C,D and +i of E32. Build by projectors on 5 qubits.
        found = None
        for start in range(32):
            vec = [(1, 0) if i == start else (0, 0) for i in range(32)]
            for op, sign in (
                (a_fast, signs4[0]),
                (b_fast, signs4[1]),
                (c_fast, signs4[2]),
                (d_fast, signs4[3]),
            ):
                image = apply_int(op, vec, 5)
                vec = [
                    (vec[i][0] + sign * image[i][0], vec[i][1] + sign * image[i][1])
                    for i in range(32)
                ]
            image = apply_int(e32, vec, 5)
            plus = apply_int(scale(1, ident(5)), vec, 5)
            vec = [(image[i][0] + plus[i][0], image[i][1] + plus[i][1]) for i in range(32)]
            if any(re or im for re, im in vec):
                found = vec
                break
        if found is None:
            line_ok = False
            break
        line_count += 1
        # C32 v + (sC sD) F9 v = 0.
        left = apply_int(c32, found, 5)
        right = apply_int(f9, found, 5)
        coef = signs4[2] * signs4[3]
        if any(left[i][0] != -coef * right[i][0] or left[i][1] != -coef * right[i][1] for i in range(32)):
            line_ok = False
            break
        # F9 expectation: image is orthogonal to the line. Since we are in
        # integers, the Hermitian product with F9 v should vanish because F9
        # anticommutes with Sigma. Checked as an operator next.
    check("sixteen +i lines and C32 = -(sC sD) F9", line_ok and line_count == 16)
    check("F9 anticommutes with Sigma fast", comm_sign(f9, sigma_fast) == -1)

    # Numpy bridge. Imports do not write.
    import boundary_project as bp
    import triality_build as tb

    def to_matrix(op: Op) -> np.ndarray:
        nq = len(op[1])
        dim = 1 << nq
        matrix = np.zeros((dim, dim), dtype=np.complex128)
        phase, letters = op
        base = (1, 1j, -1, -1j)[phase]
        for i in range(dim):
            j, ph = act_index(letters, 0, i, nq)
            matrix[j, i] = base * (1, 1j, -1, -1j)[ph]
        return matrix

    numeric = tb.gammas(14)
    gamma_match = all(np.array_equal(np.round(to_matrix(gammas[k]) - numeric[k], 10), 0) or np.allclose(to_matrix(gammas[k]), numeric[k]) for k in range(14))
    # allclose is the real test; entries are Gaussian integers so the gap is 0.
    gamma_match = all(np.allclose(to_matrix(gammas[k]), numeric[k]) for k in range(14))
    check("bridge: strings equal gammas(14)", gamma_match)
    c_num, eps_num = tb.charge_conjugation(numeric)
    check(
        "bridge: C equals charge_conjugation",
        eps_num == 1 and np.allclose(to_matrix(charge), c_num),
    )
    exhaust_num, _gs = bp.ambient_exhaust()
    check("bridge: bracket equals the Pauli exhaust", np.allclose(to_matrix(exhaust_op), exhaust_num))

    # Baseline and locks, read only.
    digest = content_sha256(ROOT / "complete_baseline.json")
    check("baseline hash unchanged", digest == BASELINE_SHA, digest)
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    n_lock = sum(1 for item in isolate["locks"] if item.get("status") == "LOCK")
    check("35 locks", n_lock == 35, str(n_lock))
    # Re-read baseline to prove this process did not rewrite it.
    digest2 = content_sha256(ROOT / "complete_baseline.json")
    check("baseline still unread-as-write", digest2 == BASELINE_SHA)

    print("PAULI PROOF CERTIFICATE PASS")
    print(f"lemmas {len(PASSED)}")
    for name in PASSED:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
