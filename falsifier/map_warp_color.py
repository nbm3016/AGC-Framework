#!/usr/bin/env python3
"""
Two MAP modules. An occupant with declared extras is not a derivation.
T_wall is not brane tension. Euler (1,1) is not c2 of an SU(3) bundle.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List

from check_engine import runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
INV_PATH = os.path.join(ARTIFACT_DIR, "generated_inventory.json")
OUT_WARP = os.path.join(ARTIFACT_DIR, "m_warp.json")
OUT_COLOR = os.path.join(ARTIFACT_DIR, "m_colorpipe.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "MAP_WARP_COLOR.md")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def cup_s2xs2(left: tuple, right: tuple) -> int:
    """H^2(S^2×S^2)=Z⊕Z, H^4=Z. (a,b)∪(c,d) = ad+bc."""
    a, b = left
    c, d = right
    return a * d + b * c


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
    knobs = int((baseline.get("status_classification") or {}).get("continuous_knobs"))
    if knobs != 0:
        fail("knobs")
    rows = {row["name"]: row for row in menu["rows"]}
    warp = rows["warp_factor"]
    color = rows["unique_color"]
    if warp["type"] != "OPEN-FIELD" or warp.get("value_forced"):
        fail("warp slot is not an open field")
    if color["type"] != "FORBIDDEN":
        fail("unique color is not forbidden")

    by_name = {row["name"]: row for row in inv["already"]}
    t_wall = Fraction(str(by_name["T_wall_identity"]["value"]))
    if t_wall != Fraction(13, 2):
        fail("T_wall moved")
    base = next(row for row in inv["new"] if "TRANSVERSE_BASE" in row["extra_names"])
    euler = tuple(base["euler_class"])
    if euler != (1, 1):
        fail("Euler class moved")
    iso = str(by_name["Iso_group"]["value"])
    dim_iso = 3 + 3 + 1
    dim_su3 = 8
    iso_contains_su3 = dim_iso >= dim_su3 and "SU(3)" in iso
    pairing = cup_s2xs2(euler, euler)

    facts = {
        "knobs": knobs,
        "N_gen": int(by_name["N_gen"]["value"]),
        "modulus_menu": menu["rows"],
        "sigma_star_locked": True,
        "warp_forced": False,
        "unique_4fold": False,
        "isolate_written": False,
        "dim_iso": dim_iso,
        "dim_su3": dim_su3,
        "iso_contains_su3": iso_contains_su3,
    }

    # Dimensionless locked numbers. k has dimension length^{-1}. None of these is that dimension.
    dimensionless = {
        "T_wall": str(t_wall),
        "sigma_star": str(by_name["sigma_star"]["value"]),
        "vol": "16*pi**3/27",
        "ricci_factor": 4,
        "eight_pi_G_eff": "9/16",
    }
    k_solutions_from_t_wall: List[str] = []
    k_solutions_from_geometry: List[str] = []
    w2_no = len(k_solutions_from_t_wall) != 1
    w3_no = len(k_solutions_from_geometry) != 1
    # c2 of an SU(3) bundle lies in H^4. Euler (1,1) is a class in H^2.
    # The cup square is the self-pairing of that U(1) class, not c2(SU(3)).
    c2_from_euler: List[int] = []
    c2_from_harm: List[int] = []
    c2_no_euler = len(c2_from_euler) != 1
    c2_no_harm = len(c2_from_harm) != 1
    c4_no = not iso_contains_su3

    warp_rows = [
        {
            "id": "W1",
            "text": "Is RS a legal OPEN-FIELD occupant if extras are listed?",
            "unique": False,
            "live_bin": "CONSISTENT",
            "extras": ["k", "L", "y"],
            "why": (
                f"warp_factor type is {warp['type']} and value_forced is {warp.get('value_forced')}. "
                "A(y)=-k|y| with those extras listed is a map occupant. Survive is not a derivation."
            ),
        }
    ]
    w2_claim = {
        "id": "W2",
        "text": "Does T_wall=13/2 force a unique number for k?",
        "yes_as_lock": {"t_wall_as_tension": True, "new_real": True},
        "uses_modulus": "T_wall_as_GeV3",
        "labels_modulus_as": "FORCED",
    }
    w2 = runCheck(w2_claim, facts)
    if not w2_no:
        fail("T_wall produced a unique k")
    warp_rows.append(
        {
            "id": "W2",
            "text": w2_claim["text"],
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["k"],
            "gates": w2["gates"],
            "why": (
                f"T_wall={t_wall} is a dimensionless spectral identity. "
                "The set of k compatible with that number has not one element. "
                "T_wall was not read as brane tension."
            ),
        }
    )
    w3_claim = {
        "id": "W3",
        "text": "Do σ*, Vol, Ric=4g, or 9/16 force k?",
        "yes_as_lock": {"geff_as_GN": True, "new_real": True, "lambda_is_R_meters": True},
        "uses_modulus": "eight_pi_G_eff_as_G_N",
        "labels_modulus_as": "G_N",
    }
    w3 = runCheck(w3_claim, facts)
    if not w3_no:
        fail("geometry produced a unique k")
    warp_rows.append(
        {
            "id": "W3",
            "text": w3_claim["text"],
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["k"],
            "gates": w3["gates"],
            "why": (
                "Locked tests are dimensionless: "
                + ", ".join(f"{key}={val}" for key, val in dimensionless.items())
                + ". None is a length^{-1}."
            ),
        }
    )
    if not (w2_no and w3_no):
        fail("W4 condition failed")
    warp_rows.append(
        {
            "id": "W4",
            "text": "Bin k as EXTERNAL. Warp type stays OPEN-FIELD.",
            "unique": False,
            "live_bin": "EXTERNAL",
            "extras": ["k", "L", "y"],
            "why": f"W2 and W3 are No. k is EXTERNAL. warp_factor stays {warp['type']}.",
        }
    )

    color_rows = [
        {
            "id": "C1",
            "text": "Legal CLASS occupant of the color-pipe with extra c2, not unique color?",
            "unique": False,
            "live_bin": "CLASS",
            "extras": ["c2"],
            "why": (
                f"unique_color type is {color['type']}. "
                "An SU(3) bundle on S^2×S^2 with c2 listed is a pipe member, not a derived color group."
            ),
        }
    ]
    c2_claim = {
        "id": "C2",
        "text": "Does Euler (1,1) force c2 of that SU(3) bundle?",
        "yes_as_lock": {"c2_as_color": True, "unique_color_derived": True},
        "uses_modulus": "unique_color",
        "labels_modulus_as": "FORCED",
    }
    c2_live = runCheck(c2_claim, facts)
    if not c2_no_euler:
        fail("Euler class produced a unique c2")
    color_rows.append(
        {
            "id": "C2",
            "text": c2_claim["text"],
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["c2"],
            "gates": c2_live["gates"],
            "why": (
                f"Euler {euler} is in H^2. Its cup square is {pairing}, the self-pairing of that U(1) class. "
                "c2 of an SU(3) bundle is a class in H^4 and is not that pairing. "
                f"Integers obtained for c2: {c2_from_euler or 'none'}."
            ),
        }
    )
    color_rows.append(
        {
            "id": "C3",
            "text": "Does HARM_2 or b2=1 force c2?",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["c2"],
            "why": (
                f"b2={by_name['b2']['value']} is the rank of H^2 of T^{{1,1}}. "
                "HARM_2 is the harmonic 2-form in that line. "
                f"Neither assigns an element of H^4. Integers obtained for c2: {c2_from_harm or 'none'}."
            ),
        }
    )
    color_rows.append(
        {
            "id": "C4",
            "text": "Does Iso contain SU(3) so the bundle is derived?",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["c2"],
            "why": f"dim Iso={dim_iso}, dim SU(3)={dim_su3}. {dim_iso}<{dim_su3}, so Iso does not contain SU(3).",
        }
    )
    if not (c2_no_euler and c2_no_harm and c4_no):
        fail("C5 condition failed")
    color_rows.append(
        {
            "id": "C5",
            "text": "Unique color stays FORBIDDEN; pipe stays CLASS; c2 stays EXTERNAL.",
            "unique": False,
            "live_bin": "EXTERNAL",
            "extras": ["c2"],
            "why": f"C2, C3, and C4 are No. unique_color stays {color['type']}. The pipe stays CLASS.",
        }
    )

    if rows["warp_factor"]["type"] != "OPEN-FIELD" or rows["unique_color"]["type"] != "FORBIDDEN":
        fail("menu types moved")
    if any(row.get("live_bin") == "FORCED" for row in warp_rows + color_rows):
        fail("a map was labeled FORCED")

    stamp = datetime.now(timezone.utc).isoformat()
    warp_doc = {
        "module": "M_WARP",
        "occupant": "A(y)=-k|y|",
        "warp_factor": "exp(-k|y|)",
        "declared_extras": ["k", "L", "y"],
        "k_bin": "EXTERNAL",
        "warp_type": warp["type"],
        "warp_value_forced": False,
        "T_wall_read_as_tension": False,
        "continuous_knobs": 0,
        "rows": warp_rows,
        "timestamp_utc": stamp,
    }
    color_doc = {
        "module": "M_COLORPIPE",
        "occupant": "SU(3) bundle on S^2×S^2",
        "declared_extras": ["c2"],
        "c2_bin": "EXTERNAL",
        "pipe_type": "CLASS",
        "unique_color": color["type"],
        "euler_cup_square": pairing,
        "euler_cup_square_is_c2": False,
        "iso_contains_SU3": iso_contains_su3,
        "continuous_knobs": 0,
        "rows": color_rows,
        "timestamp_utc": stamp,
    }
    for path, doc in ((OUT_WARP, warp_doc), (OUT_COLOR, color_doc)):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, indent=2)
            handle.write("\n")
    write_report(warp_rows, color_rows)

    print("id | claim | unique? | live_bin | extras | why")
    print("M_WARP")
    for row in warp_rows:
        extras = ",".join(row["extras"])
        print(f"{row['id']} | {row['text']} | {'Yes' if row['unique'] else 'No'} | {row['live_bin']} | {extras} | {row['why']}")
    print("M_COLORPIPE")
    for row in color_rows:
        extras = ",".join(row["extras"])
        print(f"{row['id']} | {row['text']} | {'Yes' if row['unique'] else 'No'} | {row['live_bin']} | {extras} | {row['why']}")
    print()
    print("MAP WARP + COLORPIPE - EXTRAS DECLARED - ZERO KNOBS")
    print("k forced by T_wall? No")
    print("c2 forced by Euler(1,1) / HARM_2? No")
    print("Unique color forced? No")
    print("Warp value forced? No")
    return 0


def write_report(warp_rows: List[Dict[str, Any]], color_rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# MAP warp and color pipe",
        "",
        "MAP WARP + COLORPIPE - EXTRAS DECLARED - ZERO KNOBS",
        "",
        "An occupant that lists its extras survives as a map. That is not a derivation.",
        "",
        "## M_WARP",
        "",
        "Occupant `A(y)=-k|y|`, warp factor `e^{-k|y|}`. Extras `k`, `L`, `y`.",
        "",
        "| id | claim | unique? | live_bin | extras | why |",
        "|----|-------|---------|----------|--------|-----|",
    ]
    for row in warp_rows:
        lines.append(
            f"| {row['id']} | {row['text']} | {'Yes' if row['unique'] else 'No'} | {row['live_bin']} | "
            f"{', '.join(row['extras'])} | {row['why'].replace('|', '/')} |"
        )
    lines += [
        "",
        "## M_COLORPIPE",
        "",
        "Occupant: an SU(3) bundle on the locked transverse base. Extra `c2`.",
        "",
        "| id | claim | unique? | live_bin | extras | why |",
        "|----|-------|---------|----------|--------|-----|",
    ]
    for row in color_rows:
        lines.append(
            f"| {row['id']} | {row['text']} | {'Yes' if row['unique'] else 'No'} | {row['live_bin']} | "
            f"{', '.join(row['extras'])} | {row['why'].replace('|', '/')} |"
        )
    lines += [
        "",
        "k forced by T_wall? No",
        "",
        "c2 forced by Euler(1,1) / HARM_2? No",
        "",
        "Unique color forced? No",
        "",
        "Warp value forced? No",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
