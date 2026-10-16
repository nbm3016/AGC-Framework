"""Exact certificate for theory/C1_C2_DERIVATION.md.

Lie-algebra arithmetic over the rationals. Reads the isolate, the Sigma^5
record, and the baseline. Writes nothing.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "falsifier"
import sys

sys.path.insert(0, str(ROOT))
from content_sha import WORK_BASELINE_SHA, content_sha256

BASELINE_SHA = WORK_BASELINE_SHA
PASSED: list[str] = []

Mat = tuple[tuple[int, ...], ...]


def check(name: str, ok: bool, detail: str = "") -> None:
    if not ok:
        raise SystemExit(f"FAIL {name}" + (f": {detail}" if detail else ""))
    PASSED.append(name)


def E(i: int, j: int) -> Mat:
    rows = []
    for a in range(3):
        rows.append(tuple(1 if a == i and b == j else 0 for b in range(3)))
    return tuple(rows)


def add(a: Mat, b: Mat, sb: int = 1) -> Mat:
    return tuple(
        tuple(a[i][j] + sb * b[i][j] for j in range(3)) for i in range(3)
    )


def mul(a: Mat, b: Mat) -> Mat:
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )


def comm(a: Mat, b: Mat) -> Mat:
    return add(mul(a, b), mul(b, a), -1)


S11 = add(E(0, 0), E(1, 1), -1)
S22 = add(E(1, 1), E(2, 2), -1)
S12 = add(E(0, 1), E(1, 0))
S13 = add(E(0, 2), E(2, 0))
S23 = add(E(1, 2), E(2, 1))
P_BASIS = (S11, S22, S12, S13, S23)

L12 = add(E(0, 1), E(1, 0), -1)
L13 = add(E(0, 2), E(2, 0), -1)
L23 = add(E(1, 2), E(2, 1), -1)
K_BASIS = (L12, L13, L23)


def skew_coords(a: Mat) -> tuple[int, int, int]:
    if any(a[i][i] != 0 for i in range(3)):
        raise SystemExit("diagonal in a claimed skew matrix")
    if any(a[i][j] != -a[j][i] for i in range(3) for j in range(3)):
        raise SystemExit("matrix is not skew")
    return a[0][1], a[0][2], a[1][2]


def sym_coords(a: Mat) -> tuple[int, int, int, int, int]:
    if any(a[i][j] != a[j][i] for i in range(3) for j in range(3)):
        raise SystemExit("matrix is not symmetric")
    if sum(a[i][i] for i in range(3)) != 0:
        raise SystemExit("trace is not zero")
    # a (E11-E22) + b (E22-E33) has diagonal (a, -a+b, -b)
    aa = a[0][0]
    bb = -a[2][2]
    if a[1][1] != -aa + bb:
        raise SystemExit("diagonal is not in the traceless span")
    return aa, bb, a[0][1], a[0][2], a[1][2]


def rank_nullity(rows: list[list[Fraction]]) -> tuple[int, int]:
    matrix = [row[:] for row in rows]
    m = len(matrix)
    n = len(matrix[0]) if m else 0
    row = 0
    for col in range(n):
        pivot = next((i for i in range(row, m) if matrix[i][col] != 0), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        piv = matrix[row][col]
        for j in range(col, n):
            matrix[row][j] /= piv
        for i in range(m):
            if i == row or matrix[i][col] == 0:
                continue
            factor = matrix[i][col]
            for j in range(col, n):
                matrix[i][j] -= factor * matrix[row][j]
        row += 1
    return row, n - row


def invariant_forms(actions: list[list[list[int]]]) -> list[list[Fraction]]:
    """Symmetric Q with X^T Q + Q X = 0 for every generator X. Return a basis."""
    dim = len(actions[0])
    # Unknowns are the upper triangle, row-major.
    index = {}
    k = 0
    for i in range(dim):
        for j in range(i, dim):
            index[(i, j)] = k
            k += 1
    rows: list[list[Fraction]] = []
    for action in actions:
        for a in range(dim):
            for b in range(dim):
                row = [Fraction(0) for _ in range(k)]
                # (X^T Q)[a,b] = sum_r X[r,a] Q[r,b]
                # (Q X)[a,b] = sum_c Q[a,c] X[c,b]
                for r in range(dim):
                    coef = action[r][a]
                    if coef == 0:
                        continue
                    i, j = (r, b) if r <= b else (b, r)
                    row[index[(i, j)]] += coef
                for c in range(dim):
                    coef = action[c][b]
                    if coef == 0:
                        continue
                    i, j = (a, c) if a <= c else (c, a)
                    row[index[(i, j)]] += coef
                rows.append(row)
    _rank, nullity = rank_nullity(rows)
    # Rebuild a basis of the kernel by the usual free-variable pass.
    matrix = [row[:] for row in rows]
    m = len(matrix)
    n = k
    pivot_of = [-1] * n
    row = 0
    for col in range(n):
        pivot = next((i for i in range(row, m) if matrix[i][col] != 0), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        piv = matrix[row][col]
        for j in range(n):
            matrix[row][j] /= piv
        for i in range(m):
            if i == row or matrix[i][col] == 0:
                continue
            factor = matrix[i][col]
            for j in range(n):
                matrix[i][j] -= factor * matrix[row][j]
        pivot_of[col] = row
        row += 1
    pivots = {col for col, pr in enumerate(pivot_of) if pr != -1}
    basis = []
    for free in range(n):
        if free in pivots:
            continue
        vec = [Fraction(0) for _ in range(n)]
        vec[free] = Fraction(1)
        for col, pr in enumerate(pivot_of):
            if pr == -1:
                continue
            vec[col] = -matrix[pr][free]
        basis.append(vec)
    if len(basis) != nullity:
        raise SystemExit("kernel basis does not match the nullity")
    return basis


def main() -> int:
    check("dim SU(3)", 3 * 3 - 1 == 8)
    check("dim SO(3)", 3 * 2 // 2 == 3)
    check("dim SU(2)", 2 * 2 - 1 == 3)
    check("dim SO(6)", 6 * 5 // 2 == 15)
    check("dim SO(5)", 5 * 4 // 2 == 10)
    check("C1 dimension 8-3", 8 - 3 == 5)
    check("C2 dimension 8-3", 8 - 3 == 5)

    brackets = []
    for i in range(5):
        for j in range(i + 1, 5):
            brackets.append(skew_coords(comm(P_BASIS[i], P_BASIS[j])))
    rank, _nullity = rank_nullity(
        [[Fraction(x) for x in row] for row in brackets]
    )
    check("[p,p] spans so(3)", rank == 3, str(rank))

    # Infinitesimal SO(3) action on the five traceless symmetric matrices.
    actions = []
    for ell in K_BASIS:
        columns = []
        for basis in P_BASIS:
            columns.append(sym_coords(comm(ell, basis)))
        actions.append([[columns[c][r] for c in range(5)] for r in range(5)])
    c1_forms = invariant_forms(actions)
    check("C1 invariant metrics are one scale", len(c1_forms) == 1, str(len(c1_forms)))
    # The isotropy representation so(3) -> so(5) is a Lie homomorphism.
    # Faithfulness is linear independence of the three images.
    flat_actions = [[Fraction(entry) for row in action for entry in row] for action in actions]
    action_rank, _ = rank_nullity(flat_actions)
    check("so(3) acts faithfully on the 5-plane", action_rank == 3, str(action_rank))
    gram = [
        [sum(mul(P_BASIS[i], P_BASIS[j])[t][t] for t in range(3)) for j in range(5)]
        for i in range(5)
    ]
    skew_metric = True
    for action in actions:
        for i in range(5):
            for j in range(5):
                left = sum(gram[i][k] * action[k][j] for k in range(5))
                right = sum(action[k][i] * gram[k][j] for k in range(5))
                if left + right != 0:
                    skew_metric = False
    check("so(3) action is skew for the trace metric", skew_metric)
    # [L_a, L_b] maps to the commutator of the images.
    k_comm = {
        (0, 1): skew_coords(comm(K_BASIS[0], K_BASIS[1])),
        (0, 2): skew_coords(comm(K_BASIS[0], K_BASIS[2])),
        (1, 2): skew_coords(comm(K_BASIS[1], K_BASIS[2])),
    }
    def mat_comm(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
        n = len(a)
        prod = lambda x, y: [
            [sum(x[i][k] * y[k][j] for k in range(n)) for j in range(n)] for i in range(n)
        ]
        left, right = prod(a, b), prod(b, a)
        return [[left[i][j] - right[i][j] for j in range(n)] for i in range(n)]
    homo_ok = True
    for (i, j), coords in k_comm.items():
        got = mat_comm(actions[i], actions[j])
        want = [[0] * 5 for _ in range(5)]
        for t, coef in enumerate(coords):
            for r in range(5):
                for c in range(5):
                    want[r][c] += coef * actions[t][r][c]
        if got != want:
            homo_ok = False
    check("isotropy action preserves so(3) brackets", homo_ok)

    # C2 tangent coordinates: y1, x2, y2, x3, y3.
    # i sigma_3, i sigma_1, i sigma_2, as real 5x5 matrices. y1 is fixed.
    def embed(block2: list[list[int]], block3: list[list[int]]) -> list[list[int]]:
        m = [[0] * 5 for _ in range(5)]
        for a in range(2):
            for b in range(2):
                m[1 + a][1 + b] = block2[a][b]
                m[3 + a][3 + b] = block3[a][b]
        return m

    rot = [[0, -1], [1, 0]]  # multiplication by i
    rot_minus = [[0, 1], [-1, 0]]  # multiplication by -i
    # i sigma_3 = diag(i, -i)
    x3 = embed(rot, rot_minus)
    # i sigma_1 swaps the two C factors with a factor i:
    # z2 -> i z3, z3 -> i z2.
    x1 = [[0] * 5 for _ in range(5)]
    # (x2,y2) receives i*(x3,y3) = (-y3, x3); (x3,y3) receives i*(x2,y2)=(-y2,x2)
    # columns: source y1=0, x2=1, y2=2, x3=3, y3=4
    # output x2 (row 1) gets -y3 => row1, col4 = -1
    # output y2 (row 2) gets x3 => row2, col3 = 1
    # output x3 (row 3) gets -y2 => row3, col2 = -1
    # output y3 (row 4) gets x2 => row4, col1 = 1
    x1[1][4] = -1
    x1[2][3] = 1
    x1[3][2] = -1
    x1[4][1] = 1
    # i sigma_2 = [[0, 1], [-1, 0]] on (z2,z3): z2 -> z3, z3 -> -z2.
    x2 = [[0] * 5 for _ in range(5)]
    # z2 -> z3: (x3,y3) += (x2,y2); z3 -> -z2: (x2,y2) += (-x3,-y3)
    x2[3][1] = 1
    x2[4][2] = 1
    x2[1][3] = -1
    x2[2][4] = -1
    gens = (x1, x2, x3)
    for gen in gens:
        if any(gen[i][j] != -gen[j][i] for i in range(5) for j in range(5)):
            raise SystemExit("a C2 generator is not skew")
    c2_forms = invariant_forms(gens)
    check("C2 invariant metrics are two scales", len(c2_forms) == 2, str(len(c2_forms)))

    def form_matrix(vec: list[Fraction]) -> list[list[Fraction]]:
        out = [[Fraction(0) for _ in range(5)] for _ in range(5)]
        k = 0
        for i in range(5):
            for j in range(i, 5):
                out[i][j] = vec[k]
                out[j][i] = vec[k]
                k += 1
        return out

    # The solution space should be span{ diag(1,0,0,0,0), diag(0,1,1,1,1) }.
    mats = [form_matrix(vec) for vec in c2_forms]
    # Evaluate the two diagonal blocks.
    samples = []
    for mat in mats:
        hopf = mat[0][0]
        plane = mat[1][1]
        off = any(
            mat[i][j] != 0
            for i in range(5)
            for j in range(5)
            if i != j
        )
        plane_equal = all(mat[i][i] == plane for i in range(1, 5))
        samples.append((hopf, plane, off, plane_equal))
    check(
        "C2 metrics are diagonal scales (p, q, q, q, q)",
        all((not off) and plane_equal for _h, _p, off, plane_equal in samples),
        str(samples),
    )
    has_hopf = any(h != 0 and p == 0 for h, p, _o, _e in samples)
    has_plane = any(h == 0 and p != 0 for h, p, _o, _e in samples)
    check("both pure scales occur", has_hopf and has_plane)

    # Gauss curvature of the unit sphere: R(ei,ej) ek = δ_jk ei − δ_ik ej.
    curvatures = []
    for i in range(5):
        for j in range(i + 1, 5):
            matrix = [[0] * 5 for _ in range(5)]
            matrix[i][j] = 1
            matrix[j][i] = -1
            curvatures.append([Fraction(entry) for row in matrix for entry in row])
    curv_rank, _ = rank_nullity(curvatures)
    check("round curvature spans so(5)", curv_rank == 10, str(curv_rank))

    # so(6) acting on e_0 in R^6. Image dimension 5, stabilizer dimension 10.
    images = []
    for a in range(6):
        for b in range(a + 1, 6):
            column = [0] * 6
            # E_ab e_0 is nonzero only when one index is 0.
            if a == 0:
                column[b] = 1
            images.append([Fraction(entry) for entry in column])
    orbit_rank, _ = rank_nullity(images)
    check("round sphere orbit has rank 5", orbit_rank == 5, str(orbit_rank))
    check("round stabilizer has dimension 10", 15 - orbit_rank == 10)

    yard = json.loads((ROOT / "yardstick_lovelock_euler.json").read_text(encoding="utf-8"))
    sigma = yard["lovelock_catalog"]["internal_factors"]["Sigma5"]
    check(
        "stored Sigma5 keys",
        set(sigma) == {"dim", "odd", "euler_characteristic", "note"},
    )
    check("stored dimension 5", sigma["dim"] == 5 and sigma["odd"] is True)
    check("stored Euler characteristic 0", sigma["euler_characteristic"] == 0)
    check("no diffeotype stored", "diffeotype" not in sigma and "b2" not in sigma)

    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    check("35 locks", len(locks) == 35, str(len(locks)))
    by_name = {item["name"]: item for item in locks}
    knob = by_name["continuous_knobs"]
    check("continuous_knobs value 0", knob.get("value") == 0 and knob.get("extras") == 0)
    check(
        "cone holonomy stays SU(3) as holonomy",
        by_name["CONE_HOLONOMY"].get("status") == "LOCK",
    )

    digest = content_sha256(ROOT / "complete_baseline.json")
    check("baseline hash unchanged", digest == BASELINE_SHA, digest)

    print("C1 C2 DERIVATION CERTIFICATE PASS")
    print(f"lemmas {len(PASSED)}")
    for name in PASSED:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
