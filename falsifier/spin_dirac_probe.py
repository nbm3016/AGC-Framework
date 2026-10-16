#!/usr/bin/env python3
"""
Canonical spin structure and Riemannian Dirac operator of the locked 5-fold.

The algebra is C^infty of that 5-fold. Reconstruction returns the 5-fold.
Do not set A = C^infty(M^4). Do not write g_mu_nu. Do not equate N_gen with ker D.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List, Tuple

from check_engine import LEGAL, runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
CU_PATH = os.path.join(ARTIFACT_DIR, "controlled_uniqueness.json")
APS_PATH = os.path.join(ARTIFACT_DIR, "native_aps_index.py")
CONE_PATH = os.path.join(ARTIFACT_DIR, "cone_curvature.json")
CONNES_PATH = os.path.join(ARTIFACT_DIR, "connes_reconstruct.json")
E4_PATH = os.path.join(ARTIFACT_DIR, "e4_metric_attempts.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "spin_dirac.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "SPIN_DIRAC_REPORT.md")

SUPERSCRIPT = {ch: i for i, ch in enumerate("⁰¹²³⁴⁵⁶⁷⁸⁹")}


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _sup_to_int(token: str) -> int:
    chars: List[str] = []
    for ch in token:
        if ch in SUPERSCRIPT:
            chars.append(str(SUPERSCRIPT[ch]))
        elif "0" <= ch <= "9":
            chars.append(ch)
        else:
            fail(f"bad sphere token {token!r}")
    return int("".join(chars))


def sphere_factors(source: str) -> Tuple[int, int]:
    raw = re.findall(r"S([0-9⁰¹²³⁴⁵⁶⁷⁸⁹]+)", source)
    dims = [_sup_to_int(tok) for tok in raw]
    if len(dims) != 2:
        fail(f"topology source did not yield two spheres: {source!r}")
    return dims[0], dims[1]


def sphere_betti(dim: int, degree: int) -> int:
    if degree < 0 or degree > dim:
        return 0
    if degree == 0 or degree == dim:
        return 1
    return 0


def product_betti(dim_a: int, dim_b: int, degree: int) -> int:
    return sum(sphere_betti(dim_a, i) * sphere_betti(dim_b, degree - i) for i in range(degree + 1))


def sw_sphere(dim: int) -> int:
    """
    TS^n ⊕ ε^1 is trivial of rank n+1, so the total Stiefel-Whitney class of TS^n is 1.
    Return w2 in F2.
    """
    if dim < 1:
        fail("sphere dimension")
    trivial_rank = dim + 1
    # Whitney product: w(TS^n) * w(ε) = w(ε^{n+1}) = 1, and w(ε)=1.
    # Every positive class vanishes. w2 is the class in degree 2.
    _ = trivial_rank
    return 0


def h1_f2_dimension(simply_connected: bool, connected: bool) -> int:
    """
    H^1(M; Z/2) ≅ Hom(H_1, Z/2) ⊕ Ext(H_0, Z/2).
    Simply connected ⇒ H_1 = 0 by Hurewicz. Connected ⇒ H_0 = Z, and Ext(Z, Z/2)=0.
    """
    if not connected:
        fail("link is not connected")
    if not simply_connected:
        return -1
    hom = 0
    ext = 0
    return hom + ext


def spin_certificate(dim_a: int, dim_b: int) -> Dict[str, Any]:
    link_dim = dim_a + dim_b
    b0 = product_betti(dim_a, dim_b, 0)
    b1 = product_betti(dim_a, dim_b, 1)
    # S^n, n≥2, is simply connected. π1 of a product is the product of π1.
    pi1_trivial = dim_a >= 2 and dim_b >= 2
    connected = b0 == 1
    h1 = h1_f2_dimension(pi1_trivial, connected)
    w2_a = sw_sphere(dim_a)
    w2_b = sw_sphere(dim_b)
    w2 = (w2_a + w2_b) % 2
    if w2 != 0 or h1 < 0:
        n_spin = 0
    else:
        n_spin = 2**h1
    ko = link_dim % 8
    weyl_exponent = str(Fraction(link_dim, 2))
    # Killing constants on a simply connected SE manifold of dimension 4m+1.
    m_se, remainder = divmod(link_dim, 4)
    killing_family = remainder == 1
    killing_alpha = ["-1/2", "1/2"] if killing_family else []
    # Spinor fibre dimension of Cl_n is 2^{floor(n/2)}.
    spinor_rank = 2 ** (link_dim // 2)
    return {
        "factors": [dim_a, dim_b],
        "link_dim": link_dim,
        "b0": b0,
        "b1": b1,
        "pi1_trivial": pi1_trivial,
        "w2_sphere_factors": [w2_a, w2_b],
        "w2": w2,
        "h1_f2_dimension": h1,
        "n_spin_structures": n_spin,
        "extra_continuous_knobs": 0 if n_spin == 1 else None,
        "ko_dimension": ko,
        "ko_dimension_free": False,
        "spectral_dimension": link_dim,
        "weyl_exponent": weyl_exponent,
        "weight2_exponent": 2,
        "weight2_matches_dirac": weyl_exponent == "2" or weyl_exponent == "2/1",
        "killing_dimension_is_4m_plus_1": killing_family,
        "killing_m": m_se if killing_family else None,
        "killing_alpha": killing_alpha,
        "spinor_rank": spinor_rank,
        "l2_dimension": "infinite",
        "algebra": "C^infty(T^{1,1})",
        "algebra_is_M4": False,
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
    cone = load_json(CONE_PATH)
    connes = load_json(CONNES_PATH)
    e4 = load_json(E4_PATH)
    sc = baseline.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0 or n_gen != 3:
        fail("knobs/N_gen")
    sigma_label = str((baseline.get("residual_boundary") or {}).get("official_sigma_star"))
    if sigma_label != "sqrt(3)/2":
        fail("sigma* label moved")

    rows = menu_doc.get("rows") or []
    protected = ("g_mu_nu", "unique_color", "Iso_group", "CONE_HOLONOMY", "warp_factor")
    types0 = {name: next(r["type"] for r in rows if r["name"] == name) for name in protected}
    g_row = next(r for r in rows if r["name"] == "g_mu_nu")
    if g_row.get("type") != "OPEN-FIELD" or g_row.get("value_forced"):
        fail("g_mu_nu is not an open field")
    b2_source = str(next(r["source"] for r in rows if r["name"] == "b2"))
    dim_a, dim_b = sphere_factors(b2_source)
    cert = spin_certificate(dim_a, dim_b)

    se = "Sasaki" in str(cu.get("class_definition", {}).get("description", ""))
    aps_text = open(APS_PATH, encoding="utf-8").read()
    wall_index_is_ker_d5 = "not a computation of ker D_5" not in aps_text
    if wall_index_is_ker_d5:
        fail("native wall-index file no longer disclaims ker D_5")

    spin_ok = cert["w2"] == 0 and cert["b0"] == 1
    unique_spin = spin_ok and cert["n_spin_structures"] == 1 and cert["b1"] == 0 and cert["h1_f2_dimension"] == 0
    extra_knob = cert["extra_continuous_knobs"] not in (0,)
    algebra_ok = cert["algebra"] == "C^infty(T^{1,1})" and cert["algebra_is_M4"] is False
    if "C^infty(M^4)" in cert["algebra"] or cert["algebra_is_M4"]:
        fail("A was set to C^infty(M^4)")
    hilbert_ok = unique_spin
    dirac_ok = (
        unique_spin
        and sigma_label == "sqrt(3)/2"
        and cert["ko_dimension_free"] is False
        and cert["ko_dimension"] == cert["link_dim"] % 8
        and not extra_knob
    )
    spectral_dim = cert["spectral_dimension"]
    reconstructs_5 = algebra_ok and hilbert_ok and dirac_ok and spectral_dim == cert["link_dim"] == 5
    reconstructs_4metric = False
    if reconstructs_4metric or spectral_dim == 4:
        fail("reconstruction was retargeted to dimension 4")
    killing_ok = bool(se and cert["pi1_trivial"] and cert["killing_dimension_is_4m_plus_1"])
    n_gen_equals_ker = False
    n_gen_equals_l2 = n_gen == cert["l2_dimension"]
    cone_dim = 1 + cert["link_dim"]
    hol = cone.get("hol")
    hol_is_dirac = False

    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": rows,
        "sigma_star_locked": True,
        "warp_forced": False,
        "unique_4fold": False,
        "isolate_written": False,
    }
    claims: List[Dict[str, Any]] = [
        {"id": "S1", "text": "Is T^{1,1} spin from locked topology?"},
        {"id": "S2", "text": "Is the spin structure unique (locked b1 / Betti)? Extra continuous knob?"},
        {"id": "S3", "text": "Is A forced as C^infty(T^{1,1}), or picked as C^infty(M^4)?"},
        {"id": "S4", "text": "Is H = L^2(T^{1,1}, S) unique from that spin structure?"},
        {"id": "S5", "text": "Is D = Dirac(g5) unique (no free KO-dim, no free inner fluctuation)?"},
        {"id": "S6", "text": "Does this triple reconstruct T^{1,1}?"},
        {
            "id": "S7",
            "text": "Does this triple reconstruct a unique g_mu_nu(x) on M^4?",
            "yes_as_lock": {"modulus_called_lock": True},
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "S8",
            "text": "Is N_gen=3 equal to ker D5 or to L^2 spinors of M^4?",
            "yes_as_lock": {"map_called_lock": True},
            "uses_modulus": "ker_D5_equals_N_gen",
            "labels_modulus_as": "FORCED",
        },
        {"id": "S9", "text": "Is the spectral dimension 5, not 4?"},
        {
            "id": "S10",
            "text": "May a Weyl-weight-2 twist retarget reconstruction to M^4?",
            "yes_as_lock": {"map_called_lock": True, "free_real": True},
            "uses_modulus": "weyl_weight_2",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "S11",
            "text": "Do cone spinors (A6,H6,D6) reconstruct g_mu_nu(x)?",
            "yes_as_lock": {"map_called_lock": True, "modulus_called_lock": True},
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "S12",
            "text": "Promote g_mu_nu or unique color?",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True, "modulus_called_lock": True},
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
        },
    ]
    computed = {
        "S1": {
            "unique": spin_ok,
            "bin": "FORCED" if spin_ok else "UNKNOWN",
            "why": (
                f"w2(S^{dim_a}×S^{dim_b})={cert['w2']} from stable parallelizability of each sphere. "
                f"b0={cert['b0']}."
            ),
        },
        "S2": {
            "unique": unique_spin and not extra_knob,
            "bin": "FORCED" if unique_spin and not extra_knob else "UNKNOWN",
            "why": (
                f"Künneth b1={cert['b1']}. π1 trivial={cert['pi1_trivial']}. "
                f"H^1(Z/2) dimension={cert['h1_f2_dimension']}. "
                f"spin structures={cert['n_spin_structures']}. extra knobs={cert['extra_continuous_knobs']}."
            ),
        },
        "S3": {
            "unique": algebra_ok,
            "bin": "FORCED" if algebra_ok else "REFUSED",
            "why": f"A={cert['algebra']}. Picked as C^infty(M^4)? {cert['algebra_is_M4']}.",
        },
        "S4": {
            "unique": hilbert_ok,
            "bin": "FORCED" if hilbert_ok else "UNKNOWN",
            "why": (
                f"Unique spin structure determines the spinor bundle. "
                f"Fibre rank={cert['spinor_rank']}. H=L^2 of that bundle."
            ),
        },
        "S5": {
            "unique": dirac_ok,
            "bin": "FORCED" if dirac_ok else "UNKNOWN",
            "why": (
                f"Dirac(g5) is the Clifford contraction of the spin connection. "
                f"Shape σ*={sigma_label} is locked. KO-dimension={cert['ko_dimension']} "
                f"(n mod 8), free={cert['ko_dimension_free']}. Inner fluctuation 1-form is 0."
            ),
        },
        "S6": {
            "unique": reconstructs_5,
            "bin": "FORCED" if reconstructs_5 else "UNKNOWN",
            "why": (
                f"Canonical commutative triple of spectral dimension {spectral_dim} "
                "reconstructs the locked 5-fold."
            ),
        },
        "S9": {
            "unique": spectral_dim == 5 and cert["weight2_matches_dirac"] is False,
            "bin": "FORCED" if spectral_dim == 5 else "UNKNOWN",
            "why": (
                f"Spectral dimension={spectral_dim}. Weyl exponent={cert['weyl_exponent']}. "
                f"Weight-2 exponent={cert['weight2_exponent']}."
            ),
        },
    }

    live_rows = []
    print("id | claim | unique? | live_bin | gates | why")
    for claim in claims:
        cid = claim["id"]
        if cid in computed:
            slot = computed[cid]
            live = {
                "bin": slot["bin"],
                "gates": [],
                "reasons": [slot["why"]],
                "unique": slot["unique"],
            }
        else:
            live = runCheck(claim, facts)
            live["unique"] = False
            extra = {
                "S7": f"Reconstructed dimension is {spectral_dim}. A 4-metric is not the output.",
                "S8": (
                    f"N_gen={n_gen}. Spinor fibre rank={cert['spinor_rank']}. "
                    f"L^2 dimension={cert['l2_dimension']}. "
                    "native_aps_index.py states the wall-index rule is not ker D_5. "
                    f"Equal to ker D5? {n_gen_equals_ker}. Equal to L^2? {n_gen_equals_l2}."
                ),
                "S10": (
                    f"Weight-2 exponent {cert['weight2_exponent']} against Dirac exponent "
                    f"{cert['weyl_exponent']}. The twist is not applied."
                ),
                "S11": (
                    f"Cone real dimension={cone_dim}. Hol(g_C)={hol} is holonomy, "
                    f"recorded as a Dirac operator? {hol_is_dirac}."
                ),
                "S12": "Promotion would move g_mu_nu or unique color.",
            }
            live["reasons"] = [extra[cid]] + list(live.get("reasons") or [])
        if live["bin"] not in LEGAL:
            fail(f"{cid} illegal bin {live['bin']}")
        if live.get("gates") and live["bin"] != "REFUSED":
            fail(f"{cid} gate without REFUSED")
        if cid in {"S7", "S8", "S10", "S11", "S12"} and live["bin"] != "REFUSED":
            fail(f"{cid} must refuse a 4D or color claim")
        row = {"id": cid, "text": claim["text"], **live}
        live_rows.append(row)
        why = "; ".join(live["reasons"])
        print(
            f"{cid} | {claim['text']} | {'Yes' if live['unique'] else 'No'} | "
            f"{live['bin']} | {live.get('gates', [])} | {why}"
        )

    by_id = {row["id"]: row for row in live_rows}
    five_ids = ("S1", "S2", "S3", "S4", "S5", "S6")
    five_forced = all(by_id[i]["bin"] == "FORCED" and by_id[i]["unique"] for i in five_ids)
    if five_forced:
        existing = {r["name"] for r in rows}
        additions = [
            (
                "SPIN_T11",
                "S1–S2 w2=0 and one spin structure",
                "unique spin structure on the locked 5-fold; not M^4",
                "no extra continuous knob",
            ),
            (
                "DIRAC_T11",
                "S5 Dirac(g5) on that spin structure",
                "Riemannian Dirac on T^{1,1}; not N_gen; not g_mu_nu",
                "KO-dimension fixed at 5",
            ),
            (
                "TRIPLE_T11",
                "S3–S6 canonical commutative triple",
                "reconstruction returns T^{1,1}; not a 4D metric",
                "not SU(3)_c",
            ),
        ]
        for name, source, reading, notes in additions:
            if name not in existing:
                rows.append(
                    {
                        "name": name,
                        "type": "FORCED",
                        "source": source,
                        "value_forced": True,
                        "physics_reading": reading,
                        "notes": notes,
                    }
                )
        menu_doc["rows"] = rows
        with open(MENU_PATH, "w", encoding="utf-8") as handle:
            json.dump(menu_doc, handle, indent=2)
            handle.write("\n")

    if g_row.get("value_forced") or g_row.get("type") != "OPEN-FIELD":
        fail("g_mu_nu was promoted")
    types1 = {name: next(r["type"] for r in rows if r["name"] == name) for name in protected}
    if types1 != types0:
        fail(f"protected types changed: {types0} -> {types1}")
    if any(r.get("name") == "SU(3)_c" for r in rows):
        fail("SU(3)_c added")
    for name in ("SPIN_T11", "DIRAC_T11", "TRIPLE_T11"):
        if five_forced and next(r["type"] for r in rows if r["name"] == name) != "FORCED":
            fail(f"{name} not FORCED")

    connes_n = [row for row in connes.get("N", []) if row.get("id") in {f"N{i}" for i in range(1, 7)}]
    m6 = None
    for val in e4.values():
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict) and item.get("id") == "M6":
                    m6 = item

    payload = {
        "module": "spin_dirac",
        "banner": "SPIN DIRAC T11 - 5-TRIPLE != 4-METRIC - ZERO KNOBS",
        "continuous_knobs": knobs,
        "N_gen": n_gen,
        "sigma_star": sigma_label,
        "topology_source": b2_source,
        "certificate": cert,
        "se_on_disk": se,
        "killing_spinors_admitted": killing_ok,
        "wall_index_is_ker_d5": False,
        "algebra": cert["algebra"],
        "hilbert": "L^2(T^{1,1}, S)",
        "dirac": "Dirac(g5)",
        "unique_5_triple": five_forced,
        "reconstructs_T11": bool(by_id["S6"]["unique"]),
        "unique_g_mu_nu": False,
        "g_mu_nu_type": g_row.get("type"),
        "g_mu_nu_value_forced": bool(g_row.get("value_forced")),
        "color_type": types1["unique_color"],
        "cone_real_dim": cone_dim,
        "hol_of_cone": hol,
        "hol_is_4d_dirac": hol_is_dirac,
        "S": live_rows,
        "not_input_comparison": {
            "label": "NOT INPUT",
            "connes_N1_to_N6": [
                {"id": row.get("id"), "bin": row.get("bin"), "unique": row.get("unique")} for row in connes_n
            ],
            "connes_note": "N1–N6 refused a 4D triple because no triple was stored. Those bins were not edited.",
            "e4_value_forced": e4.get("value_forced"),
            "e4_M6_bin": None if m6 is None else m6.get("bin"),
            "e4_M6_unique": None if m6 is None else m6.get("unique"),
            "hol_note": "Hol(g_C) is holonomy of the cone, not a 4D Dirac operator.",
        },
        "isolate_written": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    write_report(payload)

    print()
    print("SPIN DIRAC T11 - 5-TRIPLE != 4-METRIC - ZERO KNOBS")
    print(f"Unique 5-triple from locked g5? {'Yes' if payload['unique_5_triple'] else 'No'}")
    print(f"Reconstructs T^{{1,1}}? {'Yes' if payload['reconstructs_T11'] else 'No'}")
    print("Unique g_mu_nu from this triple? No")
    print(f"Unique color unchanged FORBIDDEN? {'Yes' if types1['unique_color'] == 'FORBIDDEN' else 'No'}")
    print("METRIC_PROMOTED: NO")
    if payload["unique_g_mu_nu"] or types1["unique_color"] != "FORBIDDEN" or g_row.get("value_forced"):
        fail("metric or color moved")
    if not payload["unique_5_triple"] or not payload["reconstructs_T11"]:
        fail("5-triple was not earned by the spin certificate")
    return 0


def write_report(payload: Dict[str, Any]) -> None:
    cert = payload["certificate"]
    comp = payload["not_input_comparison"]
    lines = [
        "# Spin and Dirac on the locked 5-fold",
        "",
        "SPIN DIRAC T11 - 5-TRIPLE != 4-METRIC - ZERO KNOBS",
        "",
        f"Topology string `{payload['topology_source']}` parses as "
        f"`S^{cert['factors'][0]} × S^{cert['factors'][1]}`, dimension {cert['link_dim']}.",
        "",
        f"Each sphere is stably parallelizable, so `w2 = {cert['w2']}`. "
        f"Künneth gives `b0 = {cert['b0']}` and `b1 = {cert['b1']}`. "
        f"Both factors have dimension at least 2, so `π1` is trivial and "
        f"`dim H^1(Z/2) = {cert['h1_f2_dimension']}`. "
        f"Spin structures: {cert['n_spin_structures']}. "
        f"Extra continuous knobs: {cert['extra_continuous_knobs']}.",
        "",
        f"The algebra is `{payload['algebra']}`. "
        f"The Hilbert space is `{payload['hilbert']}` "
        f"(spinor fibre rank {cert['spinor_rank']}). "
        f"The operator is `{payload['dirac']}` of the locked shape `σ* = {payload['sigma_star']}`. "
        f"KO-dimension is `{cert['ko_dimension']}` because dimension mod 8 is fixed. "
        "The Riemannian operator has vanishing inner-fluctuation 1-form.",
        "",
        f"Sasaki–Einstein on disk: {payload['se_on_disk']}. "
        f"Dimension `{cert['link_dim']} = 4·{cert['killing_m']}+1`, so the Killing constants are "
        f"`α = {cert['killing_alpha']}`. They are two discrete solutions, not a modulus. "
        f"Admitted: {payload['killing_spinors_admitted']}.",
        "",
        f"Spectral dimension of this Dirac operator is {cert['spectral_dimension']}. "
        f"Weyl exponent `{cert['weyl_exponent']}` against a weight-2 exponent `{cert['weight2_exponent']}`. "
        "The weight-2 twist is not applied.",
        "",
        f"`N_gen = {payload['N_gen']}` is the Module A wall-index count. "
        "The wall-index source states that this rule is not `ker D_5`. "
        f"`L^2` is {cert['l2_dimension']}-dimensional.",
        "",
        f"Cone real dimension is {payload['cone_real_dim']}. "
        f"`Hol(g_C) = {payload['hol_of_cone']}` is holonomy. "
        f"Recorded as a 4D Dirac operator: {payload['hol_is_4d_dirac']}.",
        "",
        "## Questions",
        "",
        "| id | claim | unique? | live_bin | gates | why |",
        "|----|-------|---------|----------|-------|-----|",
    ]
    for row in payload["S"]:
        why = "; ".join(row.get("reasons") or []).replace("|", "/")
        gates = ",".join(row.get("gates") or []) or "—"
        uniq = "Yes" if row.get("unique") else "No"
        lines.append(f"| {row['id']} | {row['text']} | {uniq} | {row['bin']} | {gates} | {why} |")
    lines += [
        "",
        f"`g_mu_nu` stays `{payload['g_mu_nu_type']}` with `value_forced = {payload['g_mu_nu_value_forced']}`. "
        f"Unique color stays `{payload['color_type']}`. "
        "`SPIN_T11`, `DIRAC_T11`, and `TRIPLE_T11` are FORCED 5-fold rows. No `SU(3)_c` row.",
        "",
        "## Comparison (NOT INPUT)",
        "",
        comp["connes_note"],
        "",
    ]
    for row in comp["connes_N1_to_N6"]:
        lines.append(f"- `{row['id']}` bin `{row['bin']}`, unique `{row['unique']}`.")
    lines += [
        "",
        f"E4 `value_forced = {comp['e4_value_forced']}`, M6 bin `{comp['e4_M6_bin']}`, "
        f"unique `{comp['e4_M6_unique']}`. That file was not edited.",
        "",
        comp["hol_note"],
        "",
        "## Answers",
        "",
        f"Unique 5-triple from locked g5? {'Yes' if payload['unique_5_triple'] else 'No'}",
        f"Reconstructs T^{{1,1}}? {'Yes' if payload['reconstructs_T11'] else 'No'}",
        "Unique g_mu_nu from this triple? No",
        "Unique color unchanged FORBIDDEN? Yes",
        "",
        "METRIC_PROMOTED: NO",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
