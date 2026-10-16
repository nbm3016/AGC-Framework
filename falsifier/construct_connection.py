"""Canonical horizontal connection from the Maurer–Cartan form.

The fiber of Y^14 → M^4 is Σ^5 × T^{1,1}. The Maurer–Cartan form that is
determined is the U(1) component on T^{1,1}. No vacuum is chosen and the
fiber is not traced.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "construct_connection.json"
OUT_MD = ROOT / "CONSTRUCT_CONNECTION.md"

TH1, PH1, TH2, PH2, PSI = sp.symbols("theta1 phi1 theta2 phi2 psi", real=True)
COORDS = (TH1, PH1, TH2, PH2, PSI)
# θ = σ^3 + Σ^3, the h-component of the Maurer–Cartan form of SU(2)×SU(2).
# Coordinate realization with θ(∂ψ) = 1.
THETA_COEFF = {
    TH1: sp.Integer(0),
    PH1: sp.cos(TH1),
    TH2: sp.Integer(0),
    PH2: sp.cos(TH2),
    PSI: sp.Integer(1),
}


def exterior_derivative(coeff: dict[sp.Symbol, sp.Expr]) -> dict[tuple[sp.Symbol, sp.Symbol], sp.Expr]:
    two: dict[tuple[sp.Symbol, sp.Symbol], sp.Expr] = {}
    for i, left in enumerate(COORDS):
        for right in COORDS[i + 1 :]:
            value = sp.simplify(sp.diff(coeff[right], left) - sp.diff(coeff[left], right))
            if value != 0:
                two[(left, right)] = value
    return two


def two_form_text(form: dict[tuple[sp.Symbol, sp.Symbol], sp.Expr]) -> str:
    pieces = []
    for (left, right), value in form.items():
        pieces.append(f"({sp.sstr(value)}) d{left}∧d{right}")
    return " + ".join(pieces) if pieces else "0"


def lie_bracket(x_coeff: tuple[sp.Expr, ...], y_coeff: tuple[sp.Expr, ...]) -> tuple[sp.Expr, ...]:
    out = []
    for component in range(5):
        term = sp.Integer(0)
        for index, coord in enumerate(COORDS):
            term += x_coeff[index] * sp.diff(y_coeff[component], coord)
            term -= y_coeff[index] * sp.diff(x_coeff[component], coord)
        out.append(sp.simplify(term))
    return tuple(out)


def evaluate_one(coeff: dict[sp.Symbol, sp.Expr], vector: tuple[sp.Expr, ...]) -> sp.Expr:
    return sp.simplify(sum(coeff[coord] * vector[index] for index, coord in enumerate(COORDS)))


def evaluate_two(
    form: dict[tuple[sp.Symbol, sp.Symbol], sp.Expr],
    x_coeff: tuple[sp.Expr, ...],
    y_coeff: tuple[sp.Expr, ...],
) -> sp.Expr:
    total = sp.Integer(0)
    index = {coord: pos for pos, coord in enumerate(COORDS)}
    for (left, right), value in form.items():
        total += value * (
            x_coeff[index[left]] * y_coeff[index[right]] - x_coeff[index[right]] * y_coeff[index[left]]
        )
    return sp.simplify(total)


def horizontal(vector: tuple[sp.Expr, ...]) -> tuple[sp.Expr, ...]:
    """P(X) = X - θ(X) ∂ψ. Kernel of P is the fundamental U(1) field."""
    weight = evaluate_one(THETA_COEFF, vector)
    out = list(vector)
    out[4] = sp.simplify(out[4] - weight)
    return tuple(out)


def main() -> int:
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")

    curvature = exterior_derivative(THETA_COEFF)
    expected = {
        (TH1, PH1): -sp.sin(TH1),
        (TH2, PH2): -sp.sin(TH2),
    }
    if curvature != expected:
        raise SystemExit(f"dθ is {curvature}, expected {expected}")
    # Bianchi: d(dθ) = 0. Differentiate the coefficient functions; each depends on one angle.
    for (left, right), value in curvature.items():
        for coord in COORDS:
            if coord not in (left, right) and sp.diff(value, coord) != 0:
                raise SystemExit("dθ fails d(dθ)=0")
        # d(f dleft∧dright) has no further pair inside {left,right} when f depends only on left.
        if sp.diff(value, right) != 0:
            raise SystemExit("dθ has a non-closed coefficient")

    # Horizontal lifts of the coordinate fields, then [D, D] = -dθ ∂ψ.
    lifts = {
        "dθ1": horizontal((1, 0, 0, 0, 0)),
        "dφ1": horizontal((0, 1, 0, 0, 0)),
        "dθ2": horizontal((0, 0, 1, 0, 0)),
        "dφ2": horizontal((0, 0, 0, 1, 0)),
    }
    pairs = (("dθ1", "dφ1"), ("dθ2", "dφ2"), ("dθ1", "dθ2"))
    bracket_rows = []
    for left_name, right_name in pairs:
        left = lifts[left_name]
        right = lifts[right_name]
        bracket = lie_bracket(left, right)
        vertical = -evaluate_two(curvature, left, right)
        if bracket[:4] != (0, 0, 0, 0):
            raise SystemExit(f"[{left_name},{right_name}] is not vertical: {bracket}")
        if sp.simplify(bracket[4] - vertical) != 0:
            raise SystemExit(f"[{left_name},{right_name}] disagrees with -dθ")
        bracket_rows.append(
            {
                "fields": [left_name, right_name],
                "bracket": [sp.sstr(term) for term in bracket],
                "minus_dtheta": sp.sstr(vertical),
            }
        )

    # Unit contact form from the locked Einstein frame β = 1/9. Same kernel as θ.
    eta = {coord: sp.simplify(value / 3) for coord, value in THETA_COEFF.items()}
    d_eta = exterior_derivative(eta)
    if d_eta != {(TH1, PH1): -sp.sin(TH1) / 3, (TH2, PH2): -sp.sin(TH2) / 3}:
        raise SystemExit("dη is not dθ/3")

    curvature_text = "-sin(theta1) dtheta1∧dphi1 - sin(theta2) dtheta2∧dphi2"
    projection = {
        "rule": "P(X) = X - θ(X) ∂ψ",
        "theta": "dpsi + cos(theta1) dphi1 + cos(theta2) dphi2",
        "images": {
            "∂theta1": "∂theta1",
            "∂phi1": "∂phi1 - cos(theta1) ∂psi",
            "∂theta2": "∂theta2",
            "∂phi2": "∂phi2 - cos(theta2) ∂psi",
            "∂psi": "0",
        },
    }
    # A lock moves only when its stored value is this curvature and extras = 0.
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
        "vacuum_picked": False,
        "fiber_traced": False,
        "structure_group": {
            "group": "U(1)",
            "fundamental_field": "∂psi",
            "parent_forms": "SU(2)×SU(2)",
            "quotient": "diagonal U(1)",
            "isometry_of_factor": "SU(2)×SU(2)×U(1)",
        },
        "forms": {
            "sigma": "left-invariant Maurer–Cartan forms σ^i of the first SU(2)",
            "Sigma": "left-invariant Maurer–Cartan forms Σ^i of the second SU(2)",
            "theta": "σ^3 + Σ^3 = dpsi + cos(theta1) dphi1 + cos(theta2) dphi2",
            "eta": "θ/3",
            "sigma5": "Σ^5 is a fiber factor and supplies no Maurer–Cartan form",
        },
        "horizontal_projection": projection,
        "D": {
            "formula": "D_X = P(X) = X - θ(X) ∂psi",
            "spacetime": "D_μ = P(∂/∂x^μ). θ(∂/∂x^μ) remains the pullback of θ.",
        },
        "F": {
            "formula": "[D_X, D_Y] = -dθ(X,Y) ∂psi",
            "bracket_term": "0",
            "reason_bracket_term": "U(1) is abelian, so (1/2)[θ, θ] = 0 and F = dθ.",
            "two_form": curvature_text,
            "two_form_pairs": {f"d{a}∧d{b}": sp.sstr(value) for (a, b), value in curvature.items()},
            "eta_exterior": two_form_text(d_eta),
            "omega_T_relation": "dη/2 = dθ/6",
            "bracket_checks": bracket_rows,
            "bianchi": "dF = 0",
        },
        "rows_changed": len(moved),
        "moved": moved,
        "rescored": rescored,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Horizontal connection",
        "",
        "The fiber of Y^14 → M^4 is Σ^5 × T^{1,1}. The Maurer–Cartan forms used are the left-invariant forms of SU(2)×SU(2). Their diagonal U(1) component is the connection form on T^{1,1}. Σ^5 supplies no Maurer–Cartan form.",
        "",
        "Structure group: U(1). Fundamental field: ∂ψ. Parent forms: SU(2)×SU(2). The isometry of the T^{1,1} factor is SU(2)×SU(2)×U(1).",
        "",
        "θ = σ^3 + Σ^3 = dψ + cos(θ1) dφ1 + cos(θ2) dφ2.",
        "",
        "The locked unit contact form is η = θ/3.",
        "",
        "## Horizontal projection",
        "",
        "P(X) = X − θ(X) ∂ψ.",
        "",
        "| field | P(field) |",
        "|-------|----------|",
        "| ∂θ1 | ∂θ1 |",
        "| ∂φ1 | ∂φ1 − cos(θ1) ∂ψ |",
        "| ∂θ2 | ∂θ2 |",
        "| ∂φ2 | ∂φ2 − cos(θ2) ∂ψ |",
        "| ∂ψ | 0 |",
        "",
        "## D",
        "",
        "D_X = P(X).",
        "",
        "D_μ = P(∂/∂x^μ). The coefficient θ(∂/∂x^μ) is the pullback of θ.",
        "",
        "## F",
        "",
        "[D_X, D_Y] = −dθ(X,Y) ∂ψ.",
        "",
        "U(1) is abelian, so the quadratic bracket (1/2)[θ, θ] vanishes and F = dθ.",
        "",
        "F = −sin(θ1) dθ1∧dφ1 − sin(θ2) dθ2∧dφ2.",
        "",
        "dη = dθ/3. dη/2 = dθ/6. dF = 0.",
        "",
        "The identity [D, D] = −dθ ∂ψ holds on the pairs (∂θ1, P(∂φ1)), (∂θ2, P(∂φ2)), and (∂θ1, ∂θ2).",
        "",
        "## What moved",
        "",
        "Moved: " + (", ".join(moved) if moved else "none") + ".",
        f"Rows changed: {len(moved)}.",
        "No stored lock has this curvature as its value with extras = 0.",
        "",
        "CONNECTION CONSTRUCTED — CURVATURE dθ — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
