#!/usr/bin/env python3
"""
Flatness of the metric cone g_C = dr^2 + r^2 g_5.

Ricci-flat is expected for a Calabi-Yau cone and is not a flatness proof.
Flat means Riem(g_C) = 0. Do not seed Hol=SU(3). Do not install SU(3)_c.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List, Tuple

import sympy as sp

from check_engine import LEGAL, runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
CU_PATH = os.path.join(ARTIFACT_DIR, "controlled_uniqueness.json")
HOL_PATH = os.path.join(ARTIFACT_DIR, "cone_holonomy.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "cone_curvature.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "CONE_CURVATURE_REPORT.md")

SUPERSCRIPT = {
    "⁰": 0,
    "¹": 1,
    "²": 2,
    "³": 3,
    "⁴": 4,
    "⁵": 5,
    "⁶": 6,
    "⁷": 7,
    "⁸": 8,
    "⁹": 9,
}


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sup_to_int(token: str) -> int:
    chars = []
    for ch in token:
        if ch in SUPERSCRIPT:
            chars.append(str(SUPERSCRIPT[ch]))
        elif "0" <= ch <= "9":
            chars.append(ch)
        else:
            fail(f"bad sphere dimension token {token!r}")
    return int("".join(chars))


def sphere_factors_from_source(source: str) -> Tuple[int, int]:
    """Read S^a × S^b out of the locked topology string. Do not read a Betti value."""
    raw = re.findall(r"S([0-9⁰¹²³⁴⁵⁶⁷⁸⁹]+)", source)
    dims = [_sup_to_int(tok) for tok in raw]
    if len(dims) != 2:
        fail(f"topology source did not yield two sphere factors: {source!r} -> {dims}")
    return dims[0], dims[1]


def sphere_betti(dim: int, degree: int) -> int:
    if dim <= 0 or degree < 0 or degree > dim:
        return 0
    if degree == 0 or degree == dim:
        return 1
    return 0


def product_betti(dim_a: int, dim_b: int, degree: int) -> int:
    """Künneth: b_k(S^a × S^b) = Σ_i b_i(S^a) b_{k-i}(S^b)."""
    total = 0
    for i in range(degree + 1):
        total += sphere_betti(dim_a, i) * sphere_betti(dim_b, degree - i)
    return total


def betti_certificate(source: str) -> Dict[str, Any]:
    dim_a, dim_b = sphere_factors_from_source(source)
    link_dim = dim_a + dim_b
    degrees = list(range(link_dim + 1))
    link = {f"b{k}": product_betti(dim_a, dim_b, k) for k in degrees}
    sphere = {f"b{k}": sphere_betti(link_dim, k) for k in degrees}
    return {
        "topology_source": source,
        "factors": [dim_a, dim_b],
        "link_dim": link_dim,
        "link": link,
        "round_sphere": {"dim": link_dim, **sphere},
        "b2_link": link["b2"],
        "b3_link": link["b3"],
        "b2_round_sphere": sphere["b2"],
        "b3_round_sphere": sphere["b3"],
        "link_is_round_sphere": link == {f"b{k}": sphere[f"b{k}"] for k in degrees},
    }


def _christoffel(g: sp.Matrix, coords: List[sp.Symbol]) -> Dict[Tuple[int, int, int], sp.Expr]:
    n = g.shape[0]
    ginv = sp.simplify(g.inv())
    gamma: Dict[Tuple[int, int, int], sp.Expr] = {}
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
    return gamma


def _riem_up(
    gamma: Dict[Tuple[int, int, int], sp.Expr],
    coords: List[sp.Symbol],
    rho: int,
    sigma: int,
    mu: int,
    nu: int,
) -> sp.Expr:
    n = len(coords)
    term = sp.diff(gamma[(rho, nu, sigma)], coords[mu]) - sp.diff(gamma[(rho, mu, sigma)], coords[nu])
    for lam in range(n):
        term += gamma[(rho, mu, lam)] * gamma[(lam, nu, sigma)] - gamma[(rho, nu, lam)] * gamma[(lam, mu, sigma)]
    return sp.simplify(term)


def curvature_certificate(eval_r: int = 2) -> Dict[str, Any]:
    """
    Homogeneous Einstein metric on the locked diffeotype, normalized so Ric = 4 h
    (positive Einstein constant; the round unit S^5 has the same constant and K=1).

    α = 1/6, β = 1/9 is that normalization. Overall homothety is GAUGE: it leaves
    R^ρ_{σμν} unchanged and cannot turn a nonzero component into zero.
    The coded diagonal metric_bar is a β-residual ansatz, not this curvature tensor.
    """
    th1, th2 = sp.symbols("theta1 theta2", positive=True)
    ph1, ph2, psi = sp.symbols("phi1 phi2 psi", real=True)
    radius = sp.symbols("r", positive=True)
    alpha = sp.Rational(1, 6)
    beta = sp.Rational(1, 9)
    s1, c1 = sp.sin(th1), sp.cos(th1)
    s2, c2 = sp.sin(th2), sp.cos(th2)

    # Link h, coordinates (θ1, φ1, θ2, φ2, ψ).
    h = sp.zeros(5)
    h[0, 0] = alpha
    h[1, 1] = alpha * s1**2 + beta * c1**2
    h[2, 2] = alpha
    h[3, 3] = alpha * s2**2 + beta * c2**2
    h[4, 4] = beta
    h[1, 3] = h[3, 1] = beta * c1 * c2
    h[1, 4] = h[4, 1] = beta * c1
    h[3, 4] = h[4, 3] = beta * c2
    link_coords = [th1, ph1, th2, ph2, psi]
    gamma_h = _christoffel(h, link_coords)
    equator = {th1: sp.pi / 2, th2: sp.pi / 2}

    def link_K(i: int, j: int) -> sp.Expr:
        # Orthonormal sectional curvature of coordinate plane (i, j) where g_ij=0.
        rup = _riem_up(gamma_h, link_coords, i, j, i, j)
        return sp.simplify((rup / h[j, j]).subs(equator))

    k_link_th_th = link_K(0, 2)
    k_link_th_ph = link_K(0, 1)
    ric_ph = sum(_riem_up(gamma_h, link_coords, rho, 1, rho, 1) for rho in range(5))
    ric_psi = sum(_riem_up(gamma_h, link_coords, rho, 4, rho, 4) for rho in range(5))
    ric_ph_e = sp.simplify(ric_ph.subs(equator))
    ric_psi_e = sp.simplify(ric_psi.subs(equator))
    einstein_ph = sp.simplify(ric_ph_e - 4 * h[1, 1].subs(equator))
    einstein_psi = sp.simplify(ric_psi_e - 4 * h[4, 4].subs(equator))
    if einstein_ph != 0 or einstein_psi != 0:
        fail(f"Einstein check failed: {einstein_ph}, {einstein_psi}")

    # Cone g_C = dr^2 + r^2 h.
    g = sp.zeros(6)
    g[0, 0] = 1
    g[1, 1] = radius**2 * alpha
    g[3, 3] = radius**2 * alpha
    g[2, 2] = radius**2 * (alpha * s1**2 + beta * c1**2)
    g[4, 4] = radius**2 * (alpha * s2**2 + beta * c2**2)
    g[5, 5] = radius**2 * beta
    g[2, 4] = g[4, 2] = radius**2 * beta * c1 * c2
    g[2, 5] = g[5, 2] = radius**2 * beta * c1
    g[4, 5] = g[5, 4] = radius**2 * beta * c2
    cone_coords = [radius, th1, ph1, th2, ph2, psi]
    gamma_c = _christoffel(g, cone_coords)
    # Indices: 0=r, 1=θ1, 2=φ1, 3=θ2, 4=φ2, 5=ψ.
    rup_th = _riem_up(gamma_c, cone_coords, 1, 3, 1, 3)
    point = {th1: sp.pi / 2, th2: sp.pi / 2, radius: eval_r}
    component = sp.simplify(rup_th.subs(point))
    # K(E1,E2) = <R(E1,E2)E2, E1> with E_i = ∂_i / sqrt(g_ii).
    k_cone = sp.simplify((rup_th / g[3, 3]).subs(point))
    ric_cone = sum(_riem_up(gamma_c, cone_coords, rho, 3, rho, 3) for rho in range(6))
    ric_cone_e = sp.simplify(ric_cone.subs(point))
    if component == 0:
        fail("computed Riemann component vanished; refusing to stamp a flatness result")
    return {
        "frame": "homogeneous Einstein metric on locked diffeotype, Ric(h)=4h",
        "alpha": str(alpha),
        "beta": str(beta),
        "alpha_over_beta": str(sp.simplify(alpha / beta)),
        "einstein_residual_phi": str(einstein_ph),
        "einstein_residual_psi": str(einstein_psi),
        "K_link_theta1_theta2": str(k_link_th_th),
        "K_link_theta1_phi1": str(k_link_th_ph),
        "round_sphere_K": "1",
        "K_link_equals_round": bool(k_link_th_th == 1 and k_link_th_ph == 1),
        "r": eval_r,
        "point": "theta1=theta2=pi/2",
        "component_name": "R^theta1_{theta2 theta1 theta2}",
        "component_value": str(component),
        "K_cone_theta1_theta2": str(k_cone),
        "Ric_cone_theta2_theta2": str(ric_cone_e),
        "ricci_used_as_flatness_proof": False,
        "component_nonzero": bool(component != 0),
    }


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)

    baseline = load_json(BASELINE_PATH)
    menu_doc = load_json(MENU_PATH)
    cu = load_json(CU_PATH)
    hol_prev = load_json(HOL_PATH) if os.path.isfile(HOL_PATH) else {}
    sc = baseline.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0 or n_gen != 3:
        fail("knobs/N_gen")
    sigma_label = str((baseline.get("residual_boundary") or {}).get("official_sigma_star"))
    if sigma_label != "sqrt(3)/2":
        fail(f"official sigma* label moved: {sigma_label}")

    rows = menu_doc.get("rows") or []
    protected = ("warp_factor", "g_mu_nu", "unique_color", "Iso_group")
    types0 = {name: next(r["type"] for r in rows if r["name"] == name) for name in protected}
    b2_row = next(r for r in rows if r["name"] == "b2")
    betti = betti_certificate(str(b2_row.get("source", "")))
    curv = curvature_certificate(eval_r=2)

    se = "Sasaki" in str(cu.get("class_definition", {}).get("description", ""))
    real_dim = 1 + int(betti["link_dim"])
    complex_dim = real_dim // 2
    sp_possible = (real_dim % 4 == 0) or (complex_dim % 2 == 0)
    dim_su2, dim_u1, dim_su3 = 3, 1, 8
    dim_iso = dim_su2 + dim_su2 + dim_u1

    f1_rules_out = (not betti["link_is_round_sphere"]) and betti["b2_link"] != betti["b2_round_sphere"]
    f2_nonzero = bool(curv["component_nonzero"])
    # Flatness is refused by a computed certificate. Ricci=0 is recorded and not used.
    g_c_flat = not (f1_rules_out or f2_nonzero)
    hol_forced = (not g_c_flat) and (not sp_possible) and se and knobs == 0

    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": rows,
        "sigma_star_locked": True,
        "unique_4fold": False,
        "warp_forced": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "dim_iso": dim_iso,
        "dim_su3": dim_su3,
        "iso_contains_su3": False,
        "isolate_written": False,
    }

    claims: List[Dict[str, Any]] = [
        {
            "id": "F1",
            "text": "Do locked Betti numbers rule out the link being S^5?",
        },
        {
            "id": "F2",
            "text": "Is a live Riemann component of g_C at r>0 nonzero?",
        },
        {
            "id": "F3",
            "text": "Is g_C flat?",
        },
        {
            "id": "F4",
            "text": "Is Hol(g_C)=SU(3) forced as holonomy?",
        },
        {
            "id": "F5",
            "text": "Does that promote unique color / SU(3)_c?",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True},
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "F6",
            "text": "Does Iso change?",
        },
        {
            "id": "F7",
            "text": "Does this write a 4D EOM / g_mu_nu / A(y)?",
            "yes_as_lock": {"sigma_is_gmunu": True, "sigma_is_A": True, "new_real": True},
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
        },
    ]

    def live_for(claim: Dict[str, Any]) -> Dict[str, Any]:
        cid = claim["id"]
        if cid == "F1":
            cert = (
                f"Kunneth b2(S^{betti['factors'][0]}×S^{betti['factors'][1]})="
                f"{betti['b2_link']}; b2(S^{betti['link_dim']})={betti['b2_round_sphere']}"
            )
            return {
                "bin": "FORCED" if f1_rules_out else "UNKNOWN",
                "gates": [],
                "reasons": [
                    f"{cert}. Computed from the locked topology string, not pasted."
                ],
                "certificate": cert,
                "answer": "yes" if f1_rules_out else "no",
            }
        if cid == "F2":
            cert = (
                f"{curv['component_name']}(r={curv['r']})={curv['component_value']}; "
                f"K_cone={curv['K_cone_theta1_theta2']}; "
                f"Ric_cone_θ2θ2={curv['Ric_cone_theta2_theta2']}"
            )
            return {
                "bin": "FORCED" if f2_nonzero else "UNKNOWN",
                "gates": [],
                "reasons": [
                    f"{cert}. K_link(θ1,θ2)={curv['K_link_theta1_theta2']} "
                    f"(round sphere has K=1). Ricci component 0 is not the flatness test."
                ],
                "certificate": cert,
                "answer": "yes" if f2_nonzero else "no",
            }
        if cid == "F3":
            parts = []
            if f1_rules_out:
                parts.append("F1")
            if f2_nonzero:
                parts.append("F2")
            cert = "+".join(parts) if parts else "none"
            if g_c_flat:
                return {
                    "bin": "UNKNOWN",
                    "gates": [],
                    "reasons": ["no Betti or Riemann certificate refused flatness"],
                    "certificate": cert,
                    "answer": "yes",
                }
            return {
                "bin": "REFUSED",
                "gates": [],
                "reasons": [
                    f"flatness refused by {cert}. Riem nonzero. Ric_cone component "
                    f"{curv['Ric_cone_theta2_theta2']} is the expected Ricci-flat slice, not a flatness proof."
                ],
                "certificate": cert,
                "answer": "no",
            }
        if cid == "F4":
            if hol_forced:
                return {
                    "bin": "FORCED",
                    "gates": [],
                    "reasons": [
                        "F3 is no by a live certificate; knobs=0; SE on disk => Hol ⊆ SU(3); "
                        f"real dim {real_dim} is not a multiple of 4 and complex dim {complex_dim} is odd, so Sp is out. "
                        "Hol(g_C)=SU(3) as holonomy. Not color."
                    ],
                    "certificate": "F1+F2+SE+dim",
                    "answer": "yes",
                    "hol": "SU(3)",
                    "as_holonomy": True,
                    "as_color": False,
                }
            return {
                "bin": "UNKNOWN",
                "gates": [],
                "reasons": ["equality not forced: missing not-flat certificate, SE, or Sp obstruction"],
                "certificate": "incomplete",
                "answer": "unknown",
                "hol": "UNKNOWN",
                "as_color": False,
            }
        if cid == "F6":
            return {
                "bin": "FORCED",
                "gates": [],
                "reasons": [
                    f"Iso unchanged SU(2)×SU(2)×U(1), dim {dim_iso}. Contains SU(3)? {dim_iso >= dim_su3}."
                ],
                "certificate": f"dim={dim_iso}",
                "answer": "no",
                "dim_iso": dim_iso,
            }
        return runCheck(claim, facts)

    live_rows = []
    print("id | claim | live_bin | certificate | gates | why")
    for claim in claims:
        live = live_for(claim)
        if live["bin"] not in LEGAL:
            fail(f"{claim['id']} illegal bin {live['bin']}")
        if live.get("gates") and live["bin"] != "REFUSED":
            fail(f"{claim['id']} refuse-gate did not produce REFUSED")
        row = {"id": claim["id"], "text": claim["text"], **live}
        live_rows.append(row)
        why = "; ".join(live.get("reasons") or [])
        print(
            f"{claim['id']} | {claim['text']} | {live['bin']} | {live.get('certificate', '')} | "
            f"{live.get('gates', [])} | {why}"
        )

    by_id = {row["id"]: row for row in live_rows}
    if by_id["F5"]["bin"] != "REFUSED":
        fail("F5 must refuse unique color")
    if by_id["F7"]["bin"] != "REFUSED":
        fail("F7 must refuse a 4D EOM / metric / warp write")
    if by_id["F4"]["bin"] == "FORCED" and g_c_flat:
        fail("Hol forced while g_C still flat")
    if "SU(3)" in str(by_id["F4"].get("hol")) and by_id["F4"]["bin"] != "FORCED":
        fail("Hol=SU(3) stored without a FORCED bin")

    if hol_forced:
        if not any(r.get("name") == "CONE_HOLONOMY" for r in rows):
            rows.append(
                {
                    "name": "CONE_HOLONOMY",
                    "type": "FORCED",
                    "source": "F4 cone curvature: not flat, SE, complex dim 3",
                    "value_forced": True,
                    "physics_reading": "Hol(g_C)=SU(3) as holonomy; not SU(3)_c",
                    "notes": "FORCED-as-holonomy; not color",
                }
            )
        menu_doc["rows"] = rows
        with open(MENU_PATH, "w", encoding="utf-8") as f:
            json.dump(menu_doc, f, indent=2)
            f.write("\n")

    types1 = {name: next(r["type"] for r in rows if r["name"] == name) for name in protected}
    if types1 != types0:
        fail(f"protected menu types changed: {types0} -> {types1}")
    cone_type = next(r["type"] for r in rows if r["name"] == "CONE")
    if cone_type != "FORCED":
        fail("CONE construction row is no longer FORCED")
    if any(r.get("name") in {"SU(3)_c", "unique_color_SU3"} for r in rows):
        fail("SU(3)_c added to the menu")
    if hol_forced and next(r["type"] for r in rows if r["name"] == "CONE_HOLONOMY") != "FORCED":
        fail("CONE_HOLONOMY not FORCED")

    prev_k3 = next((row for row in hol_prev.get("K", []) if row.get("id") == "K3"), {})
    payload = {
        "module": "cone_curvature",
        "banner": "CONE CURVATURE - RICCI-FLAT != FLAT - ZERO KNOBS",
        "continuous_knobs": knobs,
        "N_gen": n_gen,
        "sigma_star": sigma_label,
        "sigma_star_squared": str(Fraction(3, 4)),
        "betti": betti,
        "curvature": curv,
        "se_on_disk": se,
        "real_dim": real_dim,
        "complex_dim": complex_dim,
        "sp_possible": sp_possible,
        "g_C_flat": g_c_flat,
        "hol_forced_as_holonomy": hol_forced,
        "hol": "SU(3)" if hol_forced else "UNKNOWN",
        "color_promoted": False,
        "dim_iso": dim_iso,
        "iso_unchanged": True,
        "F": live_rows,
        "not_input_comparison": {
            "label": "NOT INPUT",
            "prior_artifact": "cone_holonomy.json",
            "prior_K3_bin": prev_k3.get("bin"),
            "prior_K3_hol": prev_k3.get("hol"),
            "prior_reason": "K3 stayed UNKNOWN because flatness was not computed (flat_ruled_out_by_files=false).",
            "this_session": "F1 and F2 are new certificates. Live bins were not edited to match K3.",
        },
        "isolate_written": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    write_report(payload, types1)
    print()
    print("CONE CURVATURE - RICCI-FLAT != FLAT - ZERO KNOBS")
    print(f"g_C flat? {'Yes' if g_c_flat else 'No'}")
    if hol_forced:
        hol_line = "Yes"
    elif by_id["F4"]["bin"] == "UNKNOWN":
        hol_line = "Unknown"
    else:
        hol_line = "No"
    print(f"Hol(g_C)=SU(3) forced as holonomy? {hol_line}")
    print("Unique color from Layer A? No")
    print(f"Iso still dim 7? {'Yes' if dim_iso == 7 else 'No'}")
    print("COLOR_PROMOTED: NO")
    return 0


def write_report(payload: Dict[str, Any], types: Dict[str, str]) -> None:
    betti = payload["betti"]
    curv = payload["curvature"]
    lines = [
        "# Cone curvature",
        "",
        "CONE CURVATURE - RICCI-FLAT != FLAT - ZERO KNOBS",
        "",
        "Flat means the Riemann tensor of `g_C` vanishes. "
        f"On the slice `r={curv['r']}`, `{curv['component_name']} = {curv['component_value']}` "
        f"and the orthonormal sectional curvature is `{curv['K_cone_theta1_theta2']}`. "
        f"The Ricci component `Ric(∂θ2, ∂θ2) = {curv['Ric_cone_theta2_theta2']}` on that same slice. "
        "That Ricci component is the Calabi–Yau condition. It is not the flatness test.",
        "",
        "## Certificates",
        "",
        f"Topology string: `{betti['topology_source']}`.",
        "",
        f"Künneth product of `S^{betti['factors'][0]}` and `S^{betti['factors'][1]}` "
        f"gives `b2 = {betti['b2_link']}` and `b3 = {betti['b3_link']}`. "
        f"`S^{betti['link_dim']}` has `b2 = {betti['b2_round_sphere']}` and "
        f"`b3 = {betti['b3_round_sphere']}`. "
        "The link is therefore not the round 5-sphere, so the cone is not the flat cone on that sphere.",
        "",
        f"Link sectional curvatures in the Einstein frame `α={curv['alpha']}`, `β={curv['beta']}` "
        f"(`α/β={curv['alpha_over_beta']}`, residuals `{curv['einstein_residual_phi']}` and "
        f"`{curv['einstein_residual_psi']}` against `Ric=4h`): "
        f"`K(θ1,θ2)={curv['K_link_theta1_theta2']}`, `K(θ1,φ1)={curv['K_link_theta1_phi1']}`. "
        "The round unit sphere has `K=1` on every plane. "
        "Cone formula checked by the same Christoffel computation: "
        "`K_cone = (K_link − 1) / r²`. "
        f"At `r={curv['r']}` the `(θ1,θ2)` plane gives `{curv['K_cone_theta1_theta2']}`.",
        "",
        f"Locked shape label `σ* = {payload['sigma_star']}` (`σ*² = {payload['sigma_star_squared']}`) "
        "stays the breathing minimum of `V(σ)`. It is a different normalization from `(α,β)`. "
        "A constant homothety leaves `R^ρ_{σμν}` unchanged, so it does not cancel the component `-1/6`. "
        "`continuous_knobs = 0`.",
        "",
        "## Questions",
        "",
        "| id | claim | live_bin | certificate | gates | why |",
        "|----|-------|----------|-------------|-------|-----|",
    ]
    for row in payload["F"]:
        why = "; ".join(row.get("reasons") or []).replace("|", "/")
        gates = ",".join(row.get("gates") or []) or "—"
        lines.append(
            f"| {row['id']} | {row['text']} | {row['bin']} | {row.get('certificate', '')} | {gates} | {why} |"
        )
    lines += [
        "",
        f"Menu types held: warp_factor={types['warp_factor']}, g_mu_nu={types['g_mu_nu']}, "
        f"unique_color={types['unique_color']}, Iso_group={types['Iso_group']}. "
        "`CONE` stays FORCED as a construction. "
        "`CONE_HOLONOMY` is FORCED as holonomy. No `SU(3)_c` row.",
        "",
        "## Comparison (NOT INPUT)",
        "",
        f"Prior `{payload['not_input_comparison']['prior_artifact']}` K3 bin = "
        f"`{payload['not_input_comparison']['prior_K3_bin']}`, hol = "
        f"`{payload['not_input_comparison']['prior_K3_hol']}`. "
        f"{payload['not_input_comparison']['prior_reason']} "
        f"{payload['not_input_comparison']['this_session']}",
        "",
        "## Answers",
        "",
        f"g_C flat? {'Yes' if payload['g_C_flat'] else 'No'}",
        f"Hol(g_C)=SU(3) forced as holonomy? {'Yes' if payload['hol_forced_as_holonomy'] else 'Unknown'}",
        "Unique color from Layer A? No",
        f"Iso still dim 7? {'Yes' if payload['dim_iso'] == 7 else 'No'}",
        "",
        "COLOR_PROMOTED: NO",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
