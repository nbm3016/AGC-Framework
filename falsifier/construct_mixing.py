"""Kaluza–Klein mixing for the locked isometry of T^{1,1}.

D_μ = ∂_μ + A_μ^a K_a, with [K_a, K_b] = −f_ab^c K_c on su(2)⊕su(2)⊕u(1).
A_μ^a(x) stays a coefficient. No sphere coordinates, no vacuum, no fiber trace.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "construct_mixing.json"
OUT_MD = ROOT / "CONSTRUCT_MIXING.md"

# L1,L2,L3 and R1,R2,R3 are the two su(2) factors. Z is the u(1) field ∂ψ.
GENERATORS = ("L1", "L2", "L3", "R1", "R2", "R3", "Z")
SU2_LEFT = ("L1", "L2", "L3")
SU2_RIGHT = ("R1", "R2", "R3")
T_MU, T_NU = sp.symbols("t_mu t_nu", real=True)


def structure(left: str, right: str) -> list[tuple[str, sp.Expr]]:
    """[K_a, K_b] as a list of (generator, coefficient). Direct sum, each su(2) with ε."""

    def su2(names: tuple[str, str, str]) -> list[tuple[str, sp.Expr]] | None:
        if left not in names or right not in names or left == right:
            return [] if left in names and right in names else None
        i = names.index(left)
        j = names.index(right)
        # (j − i) mod 3 = 1 is the positive cycle [E1,E2]=E3.
        epsilon = (j - i) % 3
        if epsilon == 1:
            target = names[(j + 1) % 3]
            return [(target, sp.Integer(1))]
        if epsilon == 2:
            target = names[(i + 1) % 3]
            return [(target, sp.Integer(-1))]
        return []

    for triple in (SU2_LEFT, SU2_RIGHT):
        piece = su2(triple)
        if piece is not None:
            return piece
    return []


def f_coeff(left: str, right: str, out: str) -> sp.Expr:
    """f_ab^c from [K_a, K_b] = −f_ab^c K_c."""
    total = sp.Integer(0)
    for name, coeff in structure(left, right):
        if name == out:
            total += -coeff
    return sp.simplify(total)


class Field:
    def __init__(self, partials: dict[str, sp.Expr] | None = None, vertical: dict[str, sp.Expr] | None = None):
        self.partials = {key: sp.sympify(value) for key, value in (partials or {}).items()}
        self.vertical = {key: sp.sympify(value) for key, value in (vertical or {}).items()}

    def bracket(self, other: "Field") -> "Field":
        partials: dict[str, sp.Expr] = {}
        vertical: dict[str, sp.Expr] = {name: sp.Integer(0) for name in GENERATORS}
        directions = {"mu": T_MU, "nu": T_NU}
        # [f ∂_i, g ∂_j]
        for i, fi in self.partials.items():
            for j, gj in other.partials.items():
                partials[j] = partials.get(j, 0) + fi * sp.diff(gj, directions[i])
                partials[i] = partials.get(i, 0) - gj * sp.diff(fi, directions[j])
        # [f ∂_i, h K] = f (∂_i h) K. Vertical fields annihilate base functions.
        for i, fi in self.partials.items():
            for name, coeff in other.vertical.items():
                vertical[name] += fi * sp.diff(coeff, directions[i])
        for i, gi in other.partials.items():
            for name, coeff in self.vertical.items():
                vertical[name] -= gi * sp.diff(coeff, directions[i])
        # [p K_a, q K_b] = p q [K_a, K_b]
        for left, p_coeff in self.vertical.items():
            for right, q_coeff in other.vertical.items():
                for name, coeff in structure(left, right):
                    vertical[name] += p_coeff * q_coeff * coeff
        partials = {key: sp.simplify(value) for key, value in partials.items() if sp.simplify(value) != 0}
        vertical = {key: sp.simplify(value) for key, value in vertical.items() if sp.simplify(value) != 0}
        return Field(partials, vertical)


def component_functions() -> tuple[dict[str, sp.Expr], dict[str, sp.Expr]]:
    a_mu = {name: sp.Function(f"Amu_{name}")(T_MU, T_NU) for name in GENERATORS}
    a_nu = {name: sp.Function(f"Anu_{name}")(T_MU, T_NU) for name in GENERATORS}
    return a_mu, a_nu


def sigma5_form(locks: list[dict]) -> list[str]:
    """A form on Σ^5 counts only when a lock with extras=0 stores one."""
    hits = []
    marks = ("Maurer", "wedge", "dpsi", "dψ", "dtheta", "dθ")
    for item in locks:
        if item.get("extras") != 0:
            continue
        blob = " ".join(str(item.get(key, "")) for key in ("name", "value", "reading"))
        names_sigma = ("Σ^5" in blob) or ("Sigma^5" in blob) or ("sigma5" in blob.lower())
        if names_sigma and any(mark in blob for mark in marks):
            hits.append(item["name"])
    return hits


def main() -> int:
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")
    iso = next(item for item in locks if item["name"] == "Iso_group")
    if iso.get("value") != "SU(2)×SU(2)×U(1)" or iso.get("extras") != 0:
        raise SystemExit("Iso_group is not the locked isometry with extras=0")

    # [L1,L2]=L3 and f_12^3 = −1, since [K_a,K_b] = −f K.
    if structure("L1", "L2") != [("L3", sp.Integer(1))]:
        raise SystemExit("su(2) bracket is not ε")
    if f_coeff("L1", "L2", "L3") != -1:
        raise SystemExit("f is not minus the structure coefficient")
    if structure("L1", "R2") or structure("L1", "Z") or structure("Z", "Z"):
        raise SystemExit("the direct sum has a cross bracket")

    a_mu, a_nu = component_functions()
    d_mu = Field({"mu": 1}, a_mu)
    d_nu = Field({"nu": 1}, a_nu)
    mixed = d_mu.bracket(d_nu)
    if mixed.partials:
        raise SystemExit(f"mixed bracket has a base piece: {mixed.partials}")

    curvature: dict[str, str] = {}
    split: dict[str, dict[str, str]] = {}
    for name in GENERATORS:
        da = sp.diff(a_nu[name], T_MU) - sp.diff(a_mu[name], T_NU)
        quadratic = sp.Integer(0)
        for left in GENERATORS:
            for right in GENERATORS:
                quadratic += a_mu[left] * a_nu[right] * (-f_coeff(left, right, name))
        expected = sp.simplify(da + quadratic)
        got = mixed.vertical.get(name, sp.Integer(0))
        if sp.simplify(got - expected) != 0:
            raise SystemExit(f"bracket disagrees with dA+A∧A on {name}")
        curvature[name] = sp.sstr(got)
        split[name] = {"dA": sp.sstr(sp.simplify(da)), "A_wedge_A": sp.sstr(sp.simplify(quadratic))}

    # θ(Z)=1, θ(other generators)=0. Evaluate dθ on the horizontal lifts.
    theta_mu = a_mu["Z"]
    theta_nu = a_nu["Z"]
    theta_of_bracket = mixed.vertical.get("Z", sp.Integer(0))
    pulled = sp.simplify(sp.diff(theta_nu, T_MU) - sp.diff(theta_mu, T_NU) - theta_of_bracket)
    if pulled != 0:
        raise SystemExit(f"pullback of dθ on the lifts did not cancel: {pulled}")

    for value in list(a_mu.values()) + list(a_nu.values()):
        if value.is_number:
            raise SystemExit("A was set to a number")

    sigma5 = sigma5_form(locks)
    curvature_text = "F_mu_nu^a = d_mu A_nu^a - d_nu A_mu^a - f_bc^a A_mu^b A_nu^c"
    matches = []
    for item in locks:
        if item.get("extras") != 0:
            continue
        if item.get("value") == curvature_text:
            matches.append(item["name"])
    moved = matches if len(matches) == 1 else []
    rescored = [
        {
            "name": item["name"],
            "prior": "LOCK",
            "bin": "RESOLVED" if item["name"] in moved else "LOCK",
            "changed": item["name"] in moved,
        }
        for item in locks
    ]

    payload = {
        "continuous_knobs": 0,
        "promoted": False,
        "ambient": "Y^14 → M^4",
        "factors": ["Σ^5", "T^{1,1}"],
        "fibration_class_picked": False,
        "A_is_numeric": False,
        "A_is_lock": False,
        "coordinate_killing_fields": False,
        "structure_group": "SU(2)×SU(2)×U(1)",
        "fundamental_field": "Z = ∂psi",
        "K_a": {
            "names": list(GENERATORS),
            "algebra": "su(2)⊕su(2)⊕u(1)",
            "bracket": "[K_a, K_b] = −f_ab^c K_c",
            "left_su2": "[L_i, L_j] = ε_ijk L_k",
            "right_su2": "[R_i, R_j] = ε_ijk R_k",
            "cross": "0",
            "u1": "Z commutes with every generator",
        },
        "mixing": "dy^m − A_μ^a K_a^m dx^μ",
        "A": "A_μ^a(x), one coefficient for each generator and each base direction",
        "D": "D_μ = ∂_μ + A_μ^a K_a",
        "F": {
            "formula": curvature_text,
            "components": curvature,
            "split": split,
            "dA_plus_A_wedge_A": "every component of [D_μ, D_ν]",
            "minus_dtheta_on_lifts": "∂_μ A_ν^Z − ∂_ν A_μ^Z − θ([D_μ, D_ν]) = 0",
            "minus_dtheta_internal_angles": "not substituted",
        },
        "sigma5_form": sigma5,
        "rows_changed": len(moved),
        "moved": moved,
        "rescored": rescored,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Kaluza–Klein mixing",
        "",
        "The locked isometry of T^{1,1} is SU(2)×SU(2)×U(1). Its Lie algebra is su(2)⊕su(2)⊕u(1), with generators L1, L2, L3, R1, R2, R3, and Z. The fundamental field is Z = ∂ψ. Cross brackets vanish, and Z commutes with every generator. Inside each su(2), [E_i, E_j] = ε_ijk E_k, so f_ij^k = −ε_ijk.",
        "",
        "The mixing coframe is dy^m − A_μ^a K_a^m dx^μ. The coefficient A_μ^a(x) is not a lock and is not a number.",
        "",
        "D_μ = ∂_μ + A_μ^a K_a.",
        "",
        "## Mixed bracket",
        "",
        "[D_μ, D_ν] = F_μν^a K_a,",
        "",
        "F_μν^a = ∂_μ A_ν^a − ∂_ν A_μ^a − f_bc^a A_μ^b A_ν^c.",
        "",
        "That expression is dA + A∧A. On each su(2) factor the quadratic piece is ε_ijk A_μ^i A_ν^j. On Z the quadratic piece is 0, so F_μν^Z = ∂_μ A_ν^Z − ∂_ν A_μ^Z.",
        "",
        "| generator | dA | A∧A |",
        "|-----------|----|-----|",
    ]
    for name in GENERATORS:
        lines.append(f"| {name} | {split[name]['dA']} | {split[name]['A_wedge_A']} |")
    lines += [
        "",
        "## −dθ on the lifts",
        "",
        "θ(Z) = 1 and θ vanishes on L_i and R_i, so θ(D_μ) = A_μ^Z. The contraction on the horizontal lifts is",
        "",
        "dθ(D_μ, D_ν) = ∂_μ A_ν^Z − ∂_ν A_μ^Z − θ([D_μ, D_ν]).",
        "",
        "The Lie bracket gives θ([D_μ, D_ν]) = F_μν^Z = ∂_μ A_ν^Z − ∂_ν A_μ^Z, so this contraction is 0. The internal-angle expression of −dθ is not substituted.",
        "",
        "## Σ^5",
        "",
        "Σ^5 stays a factor. "
        + (
            "A lock forces a form: " + ", ".join(sigma5) + "."
            if sigma5
            else "No lock with extras = 0 stores a differential form on Σ^5, so Σ^5 supplies no form."
        ),
        "",
        "## What moved",
        "",
        "Moved: " + (", ".join(moved) if moved else "none") + ".",
        f"Rows changed: {len(moved)}.",
        "The mixed curvature is an expression in A_μ^a. No stored lock equals that expression with extras = 0.",
        "",
        "MIXING CONSTRUCTED — F IS dA + A∧A — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
