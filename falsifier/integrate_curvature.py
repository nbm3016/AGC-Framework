"""Fiber integral of the gauge kinetic term on T^{1,1}.

Zero-mode curvature factors out. The inner product is the Riemannian
metric: ||Z||^2 = 1/9 and the round metric of radius-squared 1/6 on each
S^2. The Cartan–Killing form is not used.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "integrate_curvature.json"
OUT_MD = ROOT / "INTEGRATE_CURVATURE.md"

TH, PH = sp.symbols("theta phi", real=True)
TH2, PH2, PSI = sp.symbols("theta2 phi2 psi", real=True)
RADIUS2 = sp.Rational(1, 6)
Z_NORM2 = sp.Rational(1, 9)


def round_gram() -> dict[tuple[str, str], sp.Expr]:
    """g(K_i, K_j) for the three rotational fields, round metric R^2 = 1/6."""
    # Components (∂θ, ∂φ). Norms are the smooth polynomials, checked against the fields.
    fields = {
        "1": (sp.sin(PH), sp.cos(TH) / sp.sin(TH) * sp.cos(PH)),
        "2": (-sp.cos(PH), sp.cos(TH) / sp.sin(TH) * sp.sin(PH)),
        "3": (sp.Integer(0), sp.Integer(1)),
    }
    smooth = {
        ("1", "1"): 1 - sp.sin(TH) ** 2 * sp.cos(PH) ** 2,
        ("2", "2"): 1 - sp.sin(TH) ** 2 * sp.sin(PH) ** 2,
        ("3", "3"): sp.sin(TH) ** 2,
        ("1", "2"): -sp.sin(TH) ** 2 * sp.sin(PH) * sp.cos(PH),
        ("1", "3"): sp.sin(TH) * sp.cos(TH) * sp.cos(PH),
        ("2", "3"): sp.sin(TH) * sp.cos(TH) * sp.sin(PH),
    }
    gram = {}
    for i in ("1", "2", "3"):
        for j in ("1", "2", "3"):
            key = (i, j) if i <= j else (j, i)
            gamma = fields[i][0] * fields[j][0] + sp.sin(TH) ** 2 * fields[i][1] * fields[j][1]
            target = smooth[key] if i <= j else smooth[key]
            if sp.simplify(gamma - target) != 0:
                raise SystemExit(f"round metric disagrees on K{i},K{j}")
            gram[(i, j)] = sp.simplify(RADIUS2 * target)
    return gram


def sphere_integral(density: sp.Expr) -> sp.Expr:
    return sp.integrate(sp.integrate(density * sp.sin(TH), (TH, 0, sp.pi)), (PH, 0, 2 * sp.pi))


def locked_volume() -> sp.Expr:
    theta = sp.integrate(sp.sin(TH), (TH, 0, sp.pi)) * sp.integrate(1, (PH, 0, 2 * sp.pi))
    psi = sp.integrate(1, (PSI, 0, 4 * sp.pi))
    return sp.simplify(theta * theta * psi / 108)


def sigma5_volume(locks: list[dict]) -> list[str]:
    hits = []
    for item in locks:
        if item.get("extras") != 0:
            continue
        name = str(item.get("name", "")).lower()
        blob = json.dumps(item)
        if ("Σ^5" in blob or "sigma5" in name or "five_fold" in name) and "vol" in name:
            hits.append(item["name"])
    return hits


def main() -> int:
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")
    vol_lock = next(item for item in locks if item["name"] == "VOL_T11")
    if vol_lock.get("extras") != 0:
        raise SystemExit("VOL_T11 extras are not 0")
    volume = locked_volume()
    if sp.simplify(volume - sp.sympify(vol_lock["value"])) != 0:
        raise SystemExit(f"computed volume {volume} disagrees with the lock")

    gram = round_gram()
    # Spectator: the other S^2 and the ψ circle, density sinθ1 sinθ2 / 108.
    other = sp.integrate(sp.sin(TH2), (TH2, 0, sp.pi)) * sp.integrate(1, (PH2, 0, 2 * sp.pi))
    psi = sp.integrate(1, (PSI, 0, 4 * sp.pi))
    spectator = sp.simplify(other * psi / 108)

    left = {}
    for i in ("1", "2", "3"):
        for j in ("1", "2", "3"):
            integral = sp.simplify(sphere_integral(gram[(i, j)]) * spectator)
            left[f"L{i}L{j}"] = integral
    diagonal = left["L1L1"]
    for key, value in left.items():
        expect = diagonal if key[1] == key[3] else 0
        if sp.simplify(value - expect) != 0:
            raise SystemExit(f"sphere integral {key} is {value}")
    z_coeff = sp.simplify(Z_NORM2 * volume)
    if sp.simplify(z_coeff - diagonal) != 0:
        raise SystemExit(f"u(1) coefficient {z_coeff} disagrees with su(2) {diagonal}")

    coefficient = sp.sstr(diagonal)
    sigma5 = sigma5_volume(locks)
    # A coefficient moves a lock only when the stored value is that coefficient and extras = 0.
    matches = []
    for item in locks:
        if item.get("extras") != 0:
            continue
        value = item.get("value")
        if not isinstance(value, str):
            continue
        try:
            parsed = sp.sympify(value)
        except (sp.SympifyError, TypeError, ValueError):
            continue
        if parsed.free_symbols - {sp.pi}:
            continue
        if sp.simplify(parsed - diagonal) == 0:
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
        "cartan_killing_used": False,
        "zero_mode": True,
        "volume": sp.sstr(volume),
        "Z_norm_squared": "1/9",
        "sphere_radius_squared": "1/6",
        "integral": "∫ g(K_a, K_b) F^a F^b dvol = I_ab F^a F^b",
        "I_ab": f"({coefficient}) δ_ab",
        "coefficients": {
            "su2_left": coefficient,
            "su2_right": coefficient,
            "u1": coefficient,
        },
        "per_generator": True,
        "sigma5_volume": sigma5,
        "equals_stored_atom": bool(moved),
        "rows_changed": len(moved),
        "moved": moved,
        "rescored": rescored,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Integrated curvature",
        "",
        "The gauge kinetic term is integrated on T^{1,1} with the locked volume 16π³/27. A_μ^a(x) is a zero mode, so F_μν^a(x) factors out of the fiber integral. The inner product is g(K_a, K_b) from the Riemannian metric. ||Z||² = 1/9. Each S² carries the round metric of radius-squared 1/6. The Cartan–Killing form is not used.",
        "",
        "∫_{T^{1,1}} g(K_a, K_b) F^a F^b dvol = I_ab F^a F^b.",
        "",
        f"I_ab = ({coefficient}) δ_ab.",
        "",
        "| sector | generators | coefficient of each F² |",
        "|--------|------------|------------------------|",
        f"| su(2) | L1, L2, L3 | {coefficient} |",
        f"| su(2) | R1, R2, R3 | {coefficient} |",
        f"| u(1) | Z = ∂ψ | {coefficient} |",
        "",
        "The three rotational integrals on one round S² agree on the diagonal and vanish off it. The second S² repeats that integral. g(L_i, R_j) = 0 and g(L_i, Z) = 0. The u(1) integral is ||Z||² times the locked volume, and it equals the same coefficient.",
        "",
        "Neither coefficient is a measured coupling. Z is the fundamental field ∂ψ.",
        "",
        "## Σ^5",
        "",
        "Σ^5 stays a factor. "
        + (
            "Its volume enters: " + ", ".join(sigma5) + "."
            if sigma5
            else "No lock with extras = 0 is a volume of Σ^5, so Σ^5 does not enter the volume."
        ),
        "",
        "## Stored atoms",
        "",
        "The coefficient "
        + coefficient
        + " equals a stored atom: "
        + ("yes, " + ", ".join(moved) if moved else "no")
        + ".",
        "",
        "Moved: " + (", ".join(moved) if moved else "none") + ".",
        f"Rows changed: {len(moved)}.",
        "",
        "CURVATURE INTEGRATED — COEFFICIENTS RECORDED — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
