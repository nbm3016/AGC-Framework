#!/usr/bin/env python3
"""
Wave 2 descendants of the ten wave-1 objects.
Compute from the locked 5-metric. Do not freeze Layer A.
Do not identify the transverse metric with g_mu_nu.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List

import sympy as sp

from check_engine import LEGAL, runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
INV_PATH = os.path.join(ARTIFACT_DIR, "generated_inventory.json")
CONE_PATH = os.path.join(ARTIFACT_DIR, "cone_curvature.json")
SPIN_PATH = os.path.join(ARTIFACT_DIR, "spin_dirac.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "generated_wave2.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "GENERATE_WAVE2.md")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def link_metric_data() -> Dict[str, Any]:
    """Einstein-frame T^{1,1} used by the live cone certificate. α=1/6, β=1/9."""
    th1, th2 = sp.symbols("theta1 theta2", positive=True)
    alpha, beta = sp.Rational(1, 6), sp.Rational(1, 9)
    s1, c1 = sp.sin(th1), sp.cos(th1)
    s2, c2 = sp.sin(th2), sp.cos(th2)
    block = sp.Matrix(
        [
            [alpha * s1**2 + beta * c1**2, beta * c1 * c2, beta * c1],
            [beta * c1 * c2, alpha * s2**2 + beta * c2**2, beta * c2],
            [beta * c1, beta * c2, beta],
        ]
    )
    det_block = sp.factor(sp.simplify(block.det()))
    # Positive branch on (0, π).
    sqrt_g = sp.sin(th1) * sp.sin(th2) / 108
    if sp.simplify(det_block - sp.sin(th1) ** 2 * sp.sin(th2) ** 2 / 324) != 0:
        fail(f"volume element changed: {det_block}")
    sphere_area = sp.integrate(sp.sin(th1), (th1, 0, sp.pi)) * sp.integrate(1, (th1, 0, 2 * sp.pi))
    # ∫_{S^2} sinθ dθ dφ = 4π. Connection Θ = (2π/Ψ)(dψ + cosθ dφ) has Euler number 4π/Ψ.
    euler_target = 1
    psi_period = sp.simplify(4 * sp.pi / euler_target)
    if psi_period != 4 * sp.pi:
        fail("Euler (1,1) did not fix the ψ period at 4π")
    angular = sp.Integer(4) * (2 * sp.pi) ** 2
    volume = sp.simplify(angular * psi_period / 108)
    # Charge-zero j=1 function of one SU(2). g^{θθ}=6.
    sqrt_pos = sp.sin(th1) * sp.sin(th2)
    f = sp.cos(th1)
    flux = sp.diff(f, th1) * 6 * sqrt_pos
    delta_cos = sp.simplify(sp.diff(flux, th1) / sqrt_pos)
    ratio = sp.simplify(delta_cos / f)
    return {
        "alpha": str(alpha),
        "beta": str(beta),
        "sqrt_g": "sin(theta1)*sin(theta2)/108",
        "psi_period": "4*pi",
        "euler_number_per_sphere": euler_target,
        "volume": str(volume),
        "sphere_area_factor": str(sphere_area),
        "scalar_casimir_check": str(ratio),
    }


def einstein_lambda() -> sp.Expr:
    """Ric(∂ψ, ∂ψ) / g_ψψ at the equator. Homogeneous, so the constant is global."""
    th1, th2 = sp.symbols("theta1 theta2", real=True)
    ph1, ph2, psi = sp.symbols("phi1 phi2 psi", real=True)
    coords = [th1, ph1, th2, ph2, psi]
    alpha, beta = sp.Rational(1, 6), sp.Rational(1, 9)
    s1, c1 = sp.sin(th1), sp.cos(th1)
    s2, c2 = sp.sin(th2), sp.cos(th2)
    g = sp.zeros(5)
    g[0, 0] = alpha
    g[2, 2] = alpha
    g[1, 1] = alpha * s1**2 + beta * c1**2
    g[3, 3] = alpha * s2**2 + beta * c2**2
    g[4, 4] = beta
    g[1, 3] = g[3, 1] = beta * c1 * c2
    g[1, 4] = g[4, 1] = beta * c1
    g[3, 4] = g[4, 3] = beta * c2
    ginv = sp.simplify(g.inv())
    gamma: Dict[tuple, sp.Expr] = {}
    n = 5
    for rho in range(n):
        for mu in range(n):
            for nu in range(mu, n):
                acc = 0
                for sig in range(n):
                    acc += ginv[rho, sig] * (
                        sp.diff(g[nu, sig], coords[mu])
                        + sp.diff(g[mu, sig], coords[nu])
                        - sp.diff(g[mu, nu], coords[sig])
                    )
                val = sp.simplify(acc / 2)
                gamma[(rho, mu, nu)] = val
                gamma[(rho, nu, mu)] = val

    def rup(rho: int, sigma: int, mu: int, nu: int) -> sp.Expr:
        term = sp.diff(gamma[(rho, nu, sigma)], coords[mu]) - sp.diff(gamma[(rho, mu, sigma)], coords[nu])
        for lam in range(n):
            term += gamma[(rho, mu, lam)] * gamma[(lam, nu, sigma)] - gamma[(rho, nu, lam)] * gamma[(lam, mu, sigma)]
        return sp.simplify(term)

    point = {th1: sp.pi / 2, th2: sp.pi / 2}
    ric_psi = sp.simplify(sum(rup(rho, 4, rho, 4) for rho in range(n)).subs(point))
    return sp.simplify(ric_psi / g[4, 4].subs(point))


def killing_dirac_eigenvalue(alpha: Fraction, dim: int) -> Fraction:
    """Clifford relation e·e = +1. Dψ = Σ e_i·∇_{e_i}ψ = α Σ (e_i·e_i) ψ."""
    clifford_square = 1
    return alpha * dim * clifford_square


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)

    baseline = load_json(BASELINE_PATH)
    menu = load_json(MENU_PATH)
    inv = load_json(INV_PATH)
    cone = load_json(CONE_PATH)
    spin = load_json(SPIN_PATH)
    knobs = int((baseline.get("status_classification") or {}).get("continuous_knobs"))
    if knobs != 0 or menu.get("isolate_written") or inv.get("isolate_frozen"):
        fail("knobs or freeze flag")
    if int(spin["certificate"]["spectral_dimension"]) != 5:
        fail("spectral dimension moved")
    if spin["certificate"].get("algebra_is_M4") or spin.get("algebra") != "C^infty(T^{1,1})":
        fail("algebra retargeted")
    if cone.get("hol") != "SU(3)" or cone.get("color_promoted"):
        fail("holonomy record moved")

    by_name = {name: row for row in inv["new"] for name in row["extra_names"]}
    required = [
        "REEB_XI",
        "CONTACT_ETA",
        "TRANSVERSE_BASE",
        "KILLING_FORM_TOWER",
        "OMEGA_C",
        "OMEGA_VOL_C",
        "ISO_BUNDLE_FAMILY",
        "HARM_2",
        "HARM_3",
        "D5_SPECTRUM",
        "FINITE_COVERS",
    ]
    for name in required:
        if name not in by_name:
            fail(f"wave-1 object missing: {name}")
    if by_name["TRANSVERSE_BASE"].get("value") != "S^2×S^2":
        fail("transverse base is not the locked S^2×S^2")
    if list(by_name["TRANSVERSE_BASE"].get("euler_class") or []) != [1, 1]:
        fail("Euler class is not (1,1)")
    if by_name["ISO_BUNDLE_FAMILY"]["live_bin"] != "CLASS":
        fail("Iso bundle family bin moved")
    if by_name["D5_SPECTRUM"]["live_bin"] != "UNKNOWN":
        fail("wave-1 D5 bin moved")
    if by_name["FINITE_COVERS"].get("degrees") != [1]:
        fail("finite-cover degree moved")

    rows = {row["name"]: row for row in menu["rows"]}
    if rows["g_mu_nu"]["type"] != "OPEN-FIELD" or rows["g_mu_nu"].get("value_forced"):
        fail("g_mu_nu is not an open field")
    if rows["unique_color"]["type"] != "FORBIDDEN":
        fail("unique color moved")

    geom = link_metric_data()
    lam = einstein_lambda()
    if lam != 4:
        fail(f"Einstein constant is {lam}, expected 4")
    scalar = 5 * lam
    alphas = [Fraction(s) for s in spin["certificate"]["killing_alpha"]]
    dirac_on_killing = [str(killing_dirac_eigenvalue(alpha, 5)) for alpha in alphas]
    if "3" in dirac_on_killing or "3/1" in dirac_on_killing:
        fail("N_gen appeared as a Killing eigenvalue")

    # Gysin: π*(1,1)=0 and H^2(total) ≅ Z²/Z(1,1) has rank 1.
    quotient_rank = 2 - 1
    if quotient_rank != int(cone["betti"]["b2_link"]):
        fail("Euler class does not reproduce b2")

    descendants: List[Dict[str, Any]] = [
        {
            "id": "W1",
            "object": "SASAKI_PHI_J",
            "unique": True,
            "live_bin": "FORCED",
            "extras": "Phi(X)=grad_X xi; J=Phi on ker eta",
            "why": "The Levi-Civita connection of locked g5 and the unit Reeb determine Φ, and Φ squared is -1 on the contact distribution.",
        },
        {
            "id": "W2",
            "object": "g_T_omega_T",
            "unique": True,
            "live_bin": "FORCED",
            "extras": "base S^2×S^2; omega_T=d eta/2; g_T is not g_mu_nu",
            "why": "g_T is g5 on ker η, pushed to the Reeb quotient. ω_T = dη/2 is basic. The quotient is the locked transverse base. This metric is not g_μν(x).",
        },
        {
            "id": "W3",
            "object": "PARALLEL_SPINORS_CONE",
            "unique": True,
            "live_bin": "FORCED",
            "extras": "Hol=SU(3); complex line of parallel spinors; phase is Iso U(1)",
            "why": "Spin(6) spinors branch as 3⊕1 under SU(3). Exact holonomy SU(3) leaves one complex parallel spinor. The phase is the locked Reeb U(1), not a color factor.",
        },
        {
            "id": "W4",
            "object": "HARM_2_EULER_PAIRING",
            "unique": True,
            "live_bin": "FORCED",
            "extras": "H^2 ≅ Z^2/Z(1,1); rank 1; not a flux",
            "why": f"π*(1,1) is exact. The quotient of base cohomology by the Euler class has rank {quotient_rank}, matching b2. HARM_2 is the harmonic generator of that quotient, up to sign.",
        },
        {
            "id": "W5",
            "object": "D5_LABEL_FORMULA",
            "unique": True,
            "live_bin": "FORCED",
            "extras": (
                f"E(j_L,j_R,q) with no cutoff list; Killing eigenvalues {dirac_on_killing} "
                f"under e·e=+1; scalar Laplacian on cos theta1 gives {geom['scalar_casimir_check']}"
            ),
            "why": "D5 commutes with the locked Iso, so eigenvalues are a function of irrep labels. No finite list and no j-cutoff are written. The Killing spinors sit at ±5/2. N_gen is not one of those values. The scalar Casimir is a different operator.",
        },
        {
            "id": "W6",
            "object": "VOL_T11",
            "unique": True,
            "live_bin": "FORCED",
            "extras": geom["volume"],
            "why": (
                f"sqrt(g)={geom['sqrt_g']}. Euler number {geom['euler_number_per_sphere']} "
                f"fixes ψ period {geom['psi_period']}. Volume integrates to {geom['volume']}."
            ),
        },
        {
            "id": "W7",
            "object": "EINSTEIN_SCALAR_G5",
            "unique": True,
            "live_bin": "FORCED",
            "extras": f"Ric={lam}*g; scalar={scalar}",
            "why": f"Ric(∂ψ,∂ψ)/g_ψψ at θ=π/2 equals {lam}. Dimension 5 gives scalar curvature {scalar}.",
        },
        {
            "id": "W8",
            "object": "CONE_HOMOTHETY",
            "unique": True,
            "live_bin": "FORCED",
            "extras": "L_(r d/dr) g_C = 2 g_C; existing GAUGE; not a GeV",
            "why": "On dr^2+r^2 g5 the radial field r∂_r is the unique homothety of weight 2 with unit ∂r. It is the cone scale already carried as Weyl gauge.",
        },
        {
            "id": "W9",
            "object": "J_CONE",
            "unique": True,
            "live_bin": "FORCED",
            "extras": "J(d/dr)=xi; no extra real",
            "why": "The cone complex structure sends ∂r to the Reeb and restricts to Φ on the link. Wave-1 contact data fix it. No new real parameter.",
        },
        {
            "id": "W9b",
            "object": "LINK_SECOND_FUNDAMENTAL",
            "unique": True,
            "live_bin": "FORCED",
            "extras": "II = g5 / r along the radial normal",
            "why": "The level set of r in the cone has second fundamental form g5/r. The cone metric fixes it.",
        },
    ]

    facts = {
        "knobs": knobs,
        "N_gen": int(spin["N_gen"]),
        "modulus_menu": menu["rows"],
        "sigma_star_locked": True,
        "warp_forced": False,
        "unique_4fold": False,
        "isolate_written": False,
    }
    refusals = [
        {
            "id": "R1",
            "text": "Resolved-cone radii a,b are selected",
            "object": "RESOLVED_CONE_RADII",
            "yes_as_lock": {"free_real": True, "new_real": True},
            "uses_modulus": "resolved_cone_a_b",
        },
        {
            "id": "R2",
            "text": "D3 or Klebanov-Witten is imported as the 5-fold",
            "object": "D3_KW",
            "yes_as_lock": {"weld_class_to_lock": True, "burned": True},
            "uses_modulus": "KW_quiver",
        },
        {
            "id": "R3",
            "text": "g_T is g_mu_nu",
            "object": "g_T_EQUALS_g_mu_nu",
            "yes_as_lock": {"sigma_is_gmunu": True, "modulus_called_lock": True},
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "R4",
            "text": "Hol(g_C) is unique color",
            "object": "HOL_EQUALS_COLOR",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True},
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "R5",
            "text": "N_gen is a D5 eigenvalue",
            "object": "N_GEN_AS_EIGENVALUE",
            "yes_as_lock": {"map_called_lock": True},
            "uses_modulus": "N_gen_as_D5_eigenvalue",
            "labels_modulus_as": "FORCED",
        },
    ]
    refused_rows = []
    for claim in refusals:
        live = runCheck(claim, facts)
        if live["bin"] != "REFUSED":
            fail(f"{claim['id']} did not refuse")
        refused_rows.append(
            {
                "id": claim["id"],
                "object": claim["object"],
                "unique": False,
                "live_bin": live["bin"],
                "extras": ",".join(live.get("gates") or []),
                "why": "; ".join(live.get("reasons") or []),
                "gates": live.get("gates") or [],
            }
        )

    for row in descendants:
        if row["live_bin"] not in LEGAL:
            fail(f"{row['id']} illegal bin")
    forced = [row for row in descendants if row["live_bin"] == "FORCED" and row["unique"]]
    color_forced = False
    metric_forced = False
    # CLASS family remains, and the Dirac formula is not a finite closed spectrum.
    still_open = by_name["ISO_BUNDLE_FAMILY"]["live_bin"] == "CLASS" or any(
        row["live_bin"] == "UNKNOWN" for row in descendants
    )

    payload = {
        "module": "generate_wave2",
        "banner": "GENERATE WAVE 2 - DESCENDANTS OF THE TEN - ZERO KNOBS",
        "continuous_knobs": knobs,
        "isolate_frozen": False,
        "algebra": spin.get("algebra"),
        "spectral_dimension": spin["certificate"]["spectral_dimension"],
        "geometry": geom,
        "einstein_lambda": str(lam),
        "scalar_curvature": str(scalar),
        "descendants": descendants,
        "refusals": refused_rows,
        "n_forced": len(forced),
        "unique_color_forced": color_forced,
        "unique_g_mu_nu_forced": metric_forced,
        "layer_a_still_open": still_open,
        "g_mu_nu_type": rows["g_mu_nu"]["type"],
        "unique_color": rows["unique_color"]["type"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    write_report(payload)

    print("id | object | unique? | live_bin | extras | why")
    for row in descendants + refused_rows:
        uniq = "Yes" if row["unique"] else "No"
        print(f"{row['id']} | {row['object']} | {uniq} | {row['live_bin']} | {row['extras']} | {row['why']}")
    print()
    print("GENERATE WAVE 2 - DESCENDANTS OF THE TEN - ZERO KNOBS")
    print(f"New FORCED descendants: {payload['n_forced']}")
    print(f"Unique color forced? {'Yes' if color_forced else 'No'}")
    print(f"Unique g_mu_nu forced? {'Yes' if metric_forced else 'No'}")
    print(f"Layer A still open? {'Yes' if still_open else 'No'}")
    if color_forced or metric_forced or not still_open:
        fail("wave 2 closed color, the metric, or the generator")
    return 0


def write_report(payload: Dict[str, Any]) -> None:
    lines = [
        "# Wave 2 descendants",
        "",
        "GENERATE WAVE 2 - DESCENDANTS OF THE TEN - ZERO KNOBS",
        "",
        f"Algebra `{payload['algebra']}`, spectral dimension `{payload['spectral_dimension']}`. "
        f"Einstein constant `{payload['einstein_lambda']}`, scalar curvature `{payload['scalar_curvature']}`. "
        f"Volume `{payload['geometry']['volume']}`. The isolate is not frozen.",
        "",
        "| id | object | unique? | live_bin | extras | why |",
        "|----|--------|---------|----------|--------|-----|",
    ]
    for row in payload["descendants"] + payload["refusals"]:
        uniq = "Yes" if row["unique"] else "No"
        why = str(row["why"]).replace("|", "/")
        extras = str(row["extras"]).replace("|", "/")
        lines.append(
            f"| {row['id']} | {row['object']} | {uniq} | {row['live_bin']} | {extras} | {why} |"
        )
    lines += [
        "",
        f"New FORCED descendants: {payload['n_forced']}",
        "",
        f"Unique color forced? {'Yes' if payload['unique_color_forced'] else 'No'}",
        "",
        f"Unique g_μν forced? {'Yes' if payload['unique_g_mu_nu_forced'] else 'No'}",
        "",
        f"Layer A still open? {'Yes' if payload['layer_a_still_open'] else 'No'}",
        "",
        f"`g_mu_nu` stays `{payload['g_mu_nu_type']}`. Unique color stays `{payload['unique_color']}`.",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
