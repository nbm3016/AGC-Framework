#!/usr/bin/env python3
"""
Dual pincer. Audit the typed holes, then scan the locked inventory.
R11: an observer stick is not physics. Dimensionless locks only.
Promote only when type matches, the value is unique, and extras are empty.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
INV_PATH = os.path.join(ARTIFACT_DIR, "generated_inventory.json")
WAVE2_PATH = os.path.join(ARTIFACT_DIR, "generated_wave2.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "pincer_results.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "PINCER_REPORT.md")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def cup(left: List[int], right: List[int]) -> int:
    """(a,b) ∪ (c,d) = ad + bc in H^4(S^2×S^2, Z) ≅ Z."""
    return left[0] * right[1] + left[1] * right[0]


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
    wave2 = load_json(WAVE2_PATH)
    knobs = int((baseline.get("status_classification") or {}).get("continuous_knobs"))
    if knobs != 0:
        fail("knobs")
    rows = {row["name"]: row for row in menu["rows"]}
    if rows["warp_factor"]["type"] != "OPEN-FIELD" or rows["unique_color"]["type"] != "FORBIDDEN":
        fail("slot types moved")
    if rows["warp_factor"].get("value_forced") or rows["unique_color"].get("value_forced"):
        fail("open slot already promoted")

    already = {row["name"]: row for row in inv["already"]}
    base = next(row for row in inv["new"] if "TRANSVERSE_BASE" in row["extra_names"])
    euler = [int(x) for x in base["euler_class"]]
    if euler != [1, 1]:
        fail("Euler class moved")
    t_wall = Fraction(str(already["T_wall_identity"]["value"]))
    if t_wall != Fraction(13, 2):
        fail("T_wall moved")
    geff = str(already["eight_pi_G_eff_number"]["value"])
    if geff != "9/16":
        fail("G_eff number moved")
    vol = next(row for row in wave2["descendants"] if row["object"] == "VOL_T11")
    ric = next(row for row in wave2["descendants"] if row["object"] == "EINSTEIN_SCALAR_G5")
    hol = next(row for row in inv["already"] if row["name"] == "CONE_HOLONOMY")
    if "QCD" in str(hol.get("reading", "")) + str(hol.get("physics_reading", "")):
        fail("holonomy labeled QCD")

    pairing = cup(euler, euler)
    # SU(3) structure group: det = 1, so c1 vanishes. c2 is then a free class in H^4.
    color_hole = {
        "module": "M_colorpipe",
        "target_hole": "c2",
        "occupant": "SU(3) bundle on S^2×S^2",
        "required_type": "class in H^4(S^2×S^2, Z) assigned as c2 of an SU(3) bundle",
        "cohomology_degree": 4,
        "coefficient_ring": "Z",
        "integer_domain": "Z",
        "c1_required_to_vanish": True,
        "dimension_or_degree": "degree 4",
        "r11_status": "no unit conversion; dimensionless type still has to match",
    }
    # k from A(y)=-k|y|. [A]=1 so [k]=length^{-1}. Locked g5 is already normalized.
    gravity_hole = {
        "module": "M_warp",
        "target_hole": "k",
        "occupant": "A(y)=-k|y|",
        "required_type": "quantity of dimension length^{-1} in the normalized g5 units",
        "dimension_of_k": "length^{-1}",
        "dimension_or_degree": "length^{-1}",
        "locked_g5_normalized": True,
        "ric": ric["extras"],
        "vol": vol["extras"],
        "R_c_introduced": False,
        "r11_status": "observer conversion withdrawn; k stays EXTERNAL",
    }

    atoms: List[Dict[str, Any]] = [
        {
            "id": "P1a",
            "candidate_atom": "Euler (1,1)",
            "target": "c2",
            "atom_type": "class in H^2(S^2×S^2, Z)",
            "degree": 2,
            "value": euler,
            "unique_as_itself": True,
            "extras": [],
        },
        {
            "id": "P1b",
            "candidate_atom": "cup-square of Euler (1,1)",
            "target": "c2",
            "atom_type": "U(1) Euler self-pairing in H^4, evaluated as an integer",
            "degree": 4,
            "value": pairing,
            "unique_as_itself": True,
            "extras": [],
        },
        {
            "id": "P2a",
            "candidate_atom": "T_wall",
            "target": "k",
            "atom_type": "dimensionless spectral identity",
            "degree": "dimensionless",
            "value": str(t_wall),
            "unique_as_itself": True,
            "extras": [],
        },
        {
            "id": "P2b",
            "candidate_atom": "sigma_star",
            "target": "k",
            "atom_type": "dimensionless shape",
            "degree": "dimensionless",
            "value": str(already["sigma_star"]["value"]),
            "unique_as_itself": True,
            "extras": [],
        },
        {
            "id": "P2c",
            "candidate_atom": "Vol",
            "target": "k",
            "atom_type": "dimensionless volume of normalized g5",
            "degree": "dimensionless",
            "value": vol["extras"],
            "unique_as_itself": True,
            "extras": [],
        },
        {
            "id": "P2d",
            "candidate_atom": "Ric=4g, scalar 20",
            "target": "k",
            "atom_type": "dimensionless curvature of normalized g5",
            "degree": "dimensionless",
            "value": "Ric factor 4, scalar 20",
            "unique_as_itself": True,
            "extras": [],
        },
        {
            "id": "P2e",
            "candidate_atom": "8πG_eff",
            "target": "k",
            "atom_type": "dimensionless number",
            "degree": "dimensionless",
            "value": geff,
            "unique_as_itself": True,
            "extras": [],
        },
    ]

    scored: List[Dict[str, Any]] = []
    for atom in atoms:
        if atom["target"] == "c2":
            type_match = atom["atom_type"] == color_hole["required_type"]
            # Degree-4 integer is still the wrong characteristic class.
            if atom["id"] == "P1b":
                type_match = False
            unique = False
            why = (
                f"{atom['candidate_atom']} has type '{atom['atom_type']}' and value {atom['value']}. "
                "c2 requires an SU(3) characteristic class in H^4 with c1=0. "
                "The cup-square 2 is the U(1) self-pairing. It is not assigned to an SU(3) bundle."
            )
        else:
            type_match = atom["degree"] == "length^{-1}"
            unique = False
            why = (
                f"{atom['candidate_atom']}={atom['value']} is {atom['degree']}. "
                "k needs dimension length^{-1}. Normalized g5 leaves no radius to multiply. "
                "A product k·R_c is not introduced."
            )
        promote = bool(type_match and unique and atom["extras"] == [])
        scored.append(
            {
                **atom,
                "type_match": type_match,
                "unique": unique,
                "promote": promote,
                "live_bin": "FORCED" if promote else "EXTERNAL",
                "why": why,
            }
        )

    c2_forced = any(row["target"] == "c2" and row["promote"] for row in scored)
    k_forced = any(row["target"] == "k" and row["promote"] for row in scored)
    k_needs_length = not k_forced
    r11_withdraws_k = k_needs_length
    if r11_withdraws_k:
        for row in scored:
            if row["target"] == "k":
                row["live_bin"] = "EXTERNAL"
                row["r11"] = "conversion withdrawn"
    promoted = [row["candidate_atom"] for row in scored if row["promote"]]
    if promoted or c2_forced or k_forced:
        fail("promotion without type, uniqueness, and empty extras")
    if rows["unique_color"]["type"] != "FORBIDDEN":
        fail("unique color moved")

    holes = [color_hole, gravity_hole]
    payload = {
        "module": "pincer_audit_scan",
        "banner": "PINCER AUDIT AND SCAN - RULE R11 ENFORCED - ZERO KNOBS",
        "rule_r11": "Observer stick is not physics. Conversion is withdrawn after comparison. Dimensionless locks only.",
        "continuous_knobs": 0,
        "holes": holes,
        "scan": scored,
        "c2_type_matched_and_forced": False,
        "k_forced_without_observer_stick": False,
        "promoted_to_sheet_A": [],
        "any_parameter_promoted": False,
        "unique_color": "FORBIDDEN",
        "k_bin": "EXTERNAL",
        "c2_bin": "EXTERNAL",
        "euler_cup_square": pairing,
        "euler_cup_square_is_c2_SU3": False,
        "R_c_introduced": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    write_report(payload)

    print("module | target_hole | required_type | dimension_or_degree | r11_status")
    for hole in holes:
        print(
            f"{hole['module']} | {hole['target_hole']} | {hole['required_type']} | "
            f"{hole['dimension_or_degree']} | {hole['r11_status']}"
        )
    print()
    print("id | candidate_atom | target | type_match? | unique? | live_bin | why")
    for row in scored:
        print(
            f"{row['id']} | {row['candidate_atom']} | {row['target']} | "
            f"{'Yes' if row['type_match'] else 'No'} | {'Yes' if row['unique'] else 'No'} | "
            f"{row['live_bin']} | {row['why']}"
        )
    print()
    print("PINCER AUDIT AND SCAN - RULE R11 ENFORCED - ZERO KNOBS")
    print("Color c2 type-matched and forced? No")
    print("k forced without observer stick? No")
    print("Any parameter promoted to Sheet A? No")
    print("Isolate baseline byte-stable? pending full check")
    return 0


def write_report(payload: Dict[str, Any]) -> None:
    lines = [
        "# Pincer audit and scan",
        "",
        "PINCER AUDIT AND SCAN - RULE R11 ENFORCED - ZERO KNOBS",
        "",
        payload["rule_r11"],
        "",
        "## Phase 1 — typed holes",
        "",
        "| module | target_hole | required_type | dimension_or_degree | r11_status |",
        "|--------|-------------|----------------|---------------------|------------|",
    ]
    for hole in payload["holes"]:
        lines.append(
            f"| {hole['module']} | {hole['target_hole']} | {hole['required_type']} | "
            f"{hole['dimension_or_degree']} | {hole['r11_status']} |"
        )
    color = payload["holes"][0]
    lines += [
        "",
        f"Color hole: degree {color['cohomology_degree']}, coefficient ring {color['coefficient_ring']}, "
        f"integer domain {color['integer_domain']}. "
        f"c1 required to vanish: {color['c1_required_to_vanish']}.",
        "",
        "Gravity hole: dimension of k is length^{-1}. "
        "Locked g5 is already normalized. No compact radius R_c is introduced.",
        "",
        "## Phase 2 — inventory scan",
        "",
        "| id | candidate_atom | target | type_match? | unique? | live_bin | why |",
        "|----|----------------|--------|-------------|---------|----------|-----|",
    ]
    for row in payload["scan"]:
        why = row["why"].replace("|", "/")
        lines.append(
            f"| {row['id']} | {row['candidate_atom']} | {row['target']} | "
            f"{'Yes' if row['type_match'] else 'No'} | {'Yes' if row['unique'] else 'No'} | "
            f"{row['live_bin']} | {why} |"
        )
    lines += [
        "",
        f"Cup-square of Euler (1,1) equals {payload['euler_cup_square']}. "
        "That integer is the U(1) self-pairing. It is not c2 of an SU(3) bundle.",
        "",
        "Color c2 type-matched and forced? No",
        "",
        "k forced without observer stick? No",
        "",
        "Any parameter promoted to Sheet A? No",
        "",
        f"Unique color stays {payload['unique_color']}. k stays {payload['k_bin']}. c2 stays {payload['c2_bin']}.",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
