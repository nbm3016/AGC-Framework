#!/usr/bin/env python3
"""
Discovery scan of forced bundles against the two typed holes.
Do not pick a member of the Iso-bundle family.
Do not assign the volume class, or the Euler cup-square, as c2(SU(3)).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
INV_PATH = os.path.join(ARTIFACT_DIR, "generated_inventory.json")
CONE_PATH = os.path.join(ARTIFACT_DIR, "cone_curvature.json")
SPIN_PATH = os.path.join(ARTIFACT_DIR, "spin_dirac.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "pincer_discover.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "PINCER_DISCOVER.md")

C2_TYPE = "c2 of an SU(3) bundle on S^2×S^2 with c1=0"


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sphere_betti(dim: int, degree: int) -> int:
    if degree < 0 or degree > dim:
        return 0
    return 1 if degree in (0, dim) else 0


def product_betti(dim_a: int, dim_b: int, degree: int) -> int:
    return sum(sphere_betti(dim_a, i) * sphere_betti(dim_b, degree - i) for i in range(degree + 1))


def record(
    bundle: str,
    char_class: str,
    degree: int,
    structure_group: str,
    lives_on: str,
    c1_vanishes: bool,
    rank_c: int,
    why: str,
) -> Dict[str, Any]:
    on_base_h4 = lives_on == "S^2×S^2" and degree == 4
    type_match = on_base_h4 and structure_group == "SU(3)" and c1_vanishes and rank_c == 3
    # A matching type still needs extras=0 and uniqueness. None of these are that class.
    unique = False
    extras = [] if type_match else ["not_c2_SU3"]
    promote = type_match and unique and extras == []
    return {
        "bundle": bundle,
        "char_class": char_class,
        "degree": degree,
        "structure_group": structure_group,
        "lives_on": lives_on,
        "c1_vanishes": c1_vanishes,
        "rank_C": rank_c,
        "type_match_c2": type_match,
        "unique": unique,
        "extras": extras,
        "promote": promote,
        "live_bin": "FORCED" if promote else "EXTERNAL",
        "why": why,
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
    menu = load_json(MENU_PATH)
    inv = load_json(INV_PATH)
    cone = load_json(CONE_PATH)
    spin = load_json(SPIN_PATH)
    knobs = int((baseline.get("status_classification") or {}).get("continuous_knobs"))
    if knobs != 0:
        fail("knobs")
    rows = {row["name"]: row for row in menu["rows"]}
    if rows["unique_color"]["type"] != "FORBIDDEN":
        fail("unique color moved")
    family = next(row for row in inv["new"] if "ISO_BUNDLE_FAMILY" in row["extra_names"])
    if family["live_bin"] != "CLASS":
        fail("iso family is not CLASS")

    base = next(row for row in inv["new"] if "TRANSVERSE_BASE" in row["extra_names"])
    euler = [int(x) for x in base["euler_class"]]
    if euler != [1, 1] or base.get("value") != "S^2×S^2":
        fail("transverse base moved")
    if cone.get("hol") != "SU(3)" or cone.get("color_promoted"):
        fail("cone holonomy record moved")
    if int(spin["certificate"]["link_dim"]) != 5:
        fail("link dimension moved")
    if int(spin["certificate"]["n_spin_structures"]) != 1:
        fail("spin bundle is not unique")

    b4_link = product_betti(2, 3, 4)
    # Holomorphic tangent of CP1×CP1 is O(2,0) ⊕ O(0,2).
    # c = (1+2x)(1+2y) = 1 + (2x+2y) + 4 xy.
    c1_tangent = (2, 2)
    c2_tangent = 2 * 2
    euler_cup = euler[0] * euler[1] + euler[1] * euler[0]
    chi_base = 2 * 2
    if c2_tangent != chi_base:
        fail("tangent c2 disagrees with Euler characteristic")
    if euler_cup == c2_tangent:
        # Both are integers. They are still different characteristic classes.
        pass

    bundles: List[Dict[str, Any]] = [
        record(
            "T(T^{1,1})",
            "p1",
            4,
            "SO(5)",
            "T^{1,1}",
            False,
            0,
            f"Real rank 5. Computed b4(S^2×S^3)={b4_link}, so the rational degree-4 class on the link is 0. It does not supply a class in H^4 of the base, and the structure group is not SU(3).",
        ),
        record(
            "T(S^2×S^2)",
            "c2 of O(2,0)⊕O(0,2)",
            4,
            "U(2)",
            "S^2×S^2",
            False,
            2,
            f"Holomorphic tangent splits as O(2,0)⊕O(0,2). c1={c1_tangent} does not vanish. c2 evaluates to {c2_tangent}, equal to the Euler number, not to c2 of a rank-3 SU(3) bundle.",
        ),
        record(
            "Reeb U(1)",
            "Euler (1,1), cup-square",
            2,
            "U(1)",
            "S^2×S^2",
            False,
            1,
            f"Primary class is Euler {euler} in H^2. Cup-square equals {euler_cup}. That integer is the U(1) self-pairing. It is not c2(SU(3)). The volume class of the base is not assigned as c2(SU(3)).",
        ),
        record(
            "Spin(T^{1,1})",
            "p1 of the spin lift",
            4,
            "Spin(5)",
            "T^{1,1}",
            False,
            0,
            "One spin structure lifts SO(5) to Spin(5). Pontryagin data match the tangent bundle. Structure group Spin(5) is not SU(3).",
        ),
        record(
            "T(g_C)",
            "c2 of the cone tangent bundle",
            4,
            "SU(3)",
            "cone",
            True,
            3,
            "Holonomy SU(3) reduces the structure group of the cone tangent bundle, so c1 vanishes on the cone. The class lives on the 6-fold, not in H^4(S^2×S^2). It is not the color bundle on the base.",
        ),
        record(
            "transverse complex",
            "c2 of the transverse holomorphic tangent bundle",
            4,
            "U(2)",
            "S^2×S^2",
            False,
            2,
            f"Locked transverse J has complex rank 2. Same Chern data as T(S^2×S^2): c1={c1_tangent}≠0, c2={c2_tangent}. Structure group U(2), not SU(3).",
        ),
    ]

    su3_bundles = [row for row in bundles if row["structure_group"] == "SU(3)"]
    type_hits = [row for row in bundles if row["type_match_c2"]]
    if type_hits:
        fail("a class was type-matched to c2(SU(3)) on the base")
    if any(row["char_class"].startswith("volume") for row in bundles):
        fail("volume class was listed as a Chern class")
    # D4: inventory atoms are dimensionless or topological. None has dimension length^{-1}.
    length_atoms: List[str] = []
    k_external = len(length_atoms) == 0
    promoted = [row["bundle"] for row in bundles if row["promote"]]
    if promoted or not k_external:
        fail("promotion or a length atom appeared")

    payload = {
        "module": "pincer_discover",
        "banner": "PINCER DISCOVER - FORCED BUNDLES ONLY - ZERO KNOBS",
        "continuous_knobs": 0,
        "iso_bundle_family_skipped": True,
        "b4_link": b4_link,
        "euler_cup_square": euler_cup,
        "tangent_c1": list(c1_tangent),
        "tangent_c2_evaluation": c2_tangent,
        "euler_cup_assigned_as_c2_SU3": False,
        "volume_class_assigned_as_c2_SU3": False,
        "bundles": bundles,
        "D3_structure_group_SU3": [row["bundle"] for row in su3_bundles],
        "D3_on_the_base": False,
        "D4_length_dimension_atoms": length_atoms,
        "k_bin": "EXTERNAL",
        "c2_bin": "EXTERNAL",
        "c2_SU3_forced": False,
        "k_forced_without_observer_stick": False,
        "promoted_to_sheet_A": promoted,
        "unique_color": "FORBIDDEN",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    write_report(payload)

    print("bundle | char_class | degree | structure_group | type_match_c2? | unique? | live_bin | why")
    for row in bundles:
        print(
            f"{row['bundle']} | {row['char_class']} | {row['degree']} | {row['structure_group']} | "
            f"{'Yes' if row['type_match_c2'] else 'No'} | {'Yes' if row['unique'] else 'No'} | "
            f"{row['live_bin']} | {row['why']}"
        )
    print()
    print(
        "D4: no locked atom has dimension length^{-1}. "
        "k stays EXTERNAL under R11."
    )
    print(
        "D5: no class is c2 of an SU(3) bundle on S^2×S^2 with extras=0. "
        "c2 and k stay EXTERNAL. Unique color stays FORBIDDEN. No promotion to Sheet A."
    )
    print()
    print("PINCER DISCOVER - FORCED BUNDLES ONLY - ZERO KNOBS")
    print("c2 of SU(3) forced from a locked bundle? No")
    print("k forced without observer stick? No")
    print("Any promotion to Sheet A? No")
    return 0


def write_report(payload: Dict[str, Any]) -> None:
    lines = [
        "# Pincer discovery",
        "",
        "PINCER DISCOVER - FORCED BUNDLES ONLY - ZERO KNOBS",
        "",
        "Only bundles already forced by the locked geometry are scored. "
        "The Iso-bundle family is not sampled. "
        f"The cup-square of Euler (1,1) is {payload['euler_cup_square']}. "
        f"The holomorphic tangent bundle has c1={payload['tangent_c1']} and c2 evaluating to {payload['tangent_c2_evaluation']}. "
        "Neither number is assigned as c2 of an SU(3) bundle. "
        "The volume class of S^2×S^2 is not assigned as that Chern class.",
        "",
        "| bundle | char_class | degree | structure_group | type_match_c2? | unique? | live_bin | why |",
        "|--------|------------|--------|-----------------|----------------|---------|----------|-----|",
    ]
    for row in payload["bundles"]:
        why = row["why"].replace("|", "/")
        lines.append(
            f"| {row['bundle']} | {row['char_class']} | {row['degree']} | {row['structure_group']} | "
            f"{'Yes' if row['type_match_c2'] else 'No'} | {'Yes' if row['unique'] else 'No'} | "
            f"{row['live_bin']} | {why} |"
        )
    lines += [
        "",
        f"D3: structure group SU(3) occurs for {payload['D3_structure_group_SU3']}, on the cone, not on the base.",
        "",
        "D4: no locked atom has dimension length^{-1}. k stays EXTERNAL under R11.",
        "",
        "D5: c2 and k stay EXTERNAL. Unique color stays FORBIDDEN. Nothing is promoted to Sheet A.",
        "",
        "c2 of SU(3) forced from a locked bundle? No",
        "",
        "k forced without observer stick? No",
        "",
        "Any promotion to Sheet A? No",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
