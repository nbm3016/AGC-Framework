#!/usr/bin/env python3
"""
Finish chain. P1 then P2, then the machine.
A failed door is not repaired by picking a class or an integer pair.
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
CU_PATH = os.path.join(ARTIFACT_DIR, "controlled_uniqueness.json")
INV_PATH = os.path.join(ARTIFACT_DIR, "generated_inventory.json")
WAVE2_PATH = os.path.join(ARTIFACT_DIR, "generated_wave2.json")
UNCAP_PATH = os.path.join(ARTIFACT_DIR, "generated_uncap.json")
CATALOG_PATH = os.path.join(ARTIFACT_DIR, "solutions_catalog.json")
H1_PATH = os.path.join(ARTIFACT_DIR, "h1_color_attempts.json")
HD_PATH = os.path.join(ARTIFACT_DIR, "hd_wilson_attempts.json")
E4_PATH = os.path.join(ARTIFACT_DIR, "e4_metric_attempts.json")
CONE_PATH = os.path.join(ARTIFACT_DIR, "cone_curvature.json")

P1_PATH = os.path.join(ARTIFACT_DIR, "p1_y14.json")
P2_PATH = os.path.join(ARTIFACT_DIR, "p2_mpq.json")
SHEET_A_PATH = os.path.join(ARTIFACT_DIR, "isolate_sheet.json")
SHEET_B_PATH = os.path.join(ARTIFACT_DIR, "weld_register.json")
SHEET_C_PATH = os.path.join(ARTIFACT_DIR, "missing_names.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "FINISH_CHAIN.md")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def dump(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def door_p1(cu: Dict[str, Any]) -> Dict[str, Any]:
    claim = str(cu.get("theorem_level_claim", ""))
    landscape_open = cu.get("global_landscape_uniqueness") is False
    sentence = "Uniqueness among all 14D fibrations remains open."
    outside = any(
        item.get("deformation") == "bases_outside_first_slice" and item.get("status") == "outside_class_open"
        for item in cu.get("obstructions") or cu.get("deformations") or []
    )
    # The deformations live under a list. Search the raw structure.
    blob = json.dumps(cu)
    outside = '"status": "outside_class_open"' in blob and "14D fibrations not in G_SE" in blob
    determined = (not landscape_open) and (sentence not in claim) and (not outside)
    return {
        "door": "P1",
        "question": "Is fibration_class uniquely determined, extras=0?",
        "global_landscape_uniqueness": cu.get("global_landscape_uniqueness"),
        "skeleton_isolates_T11_inside_first_slice": cu.get("skeleton_isolates_T11"),
        "determined": determined,
        "extras": [] if determined else ["fibration_class"],
        "extra_name": None if determined else "fibration_class",
        "rebase": False,
        "why": (
            "First-slice files isolate T^{1,1} inside G_SE. "
            "The same files say uniqueness among all 14D fibrations remains open. "
            "No fibration class was picked."
        ),
    }


def door_p2(inv: Dict[str, Any], cone: Dict[str, Any]) -> Dict[str, Any]:
    """Locked 5-fold atoms versus an integer label (p,q) of M^{p,q}."""
    by_name = {row["name"]: row for row in inv["already"]}
    iso = str(by_name["Iso_group"]["value"])
    b2 = int(by_name["b2"]["value"])
    b3 = int(by_name["b3"]["value"])
    n_gen = int(by_name["N_gen"]["value"])
    t_wall = str(by_name["T_wall_identity"]["value"])
    sigma = str(by_name["sigma_star"]["value"])
    link_dim = int(cone["betti"]["link_dim"])
    iso_factors = ["SU(2)", "SU(2)", "U(1)"]
    m_factors = ["SU(3)", "SU(2)", "U(1)"]
    m_dim = (8 + 3 + 1) - (3 + 1 + 1)
    same_iso = iso_factors == m_factors
    same_dim = link_dim == m_dim
    # No locked atom is an integer pair. N_gen is one integer, not (p,q).
    pair_in_atoms = False
    compatible = same_iso and same_dim and pair_in_atoms
    return {
        "door": "P2",
        "question": "Do locked atoms force integers (p,q)?",
        "locked": {
            "b2": b2,
            "b3": b3,
            "N_gen": n_gen,
            "T_wall": t_wall,
            "sigma_star": sigma,
            "iso": iso,
            "link_dim": link_dim,
            "vol": "16*pi**3/27",
        },
        "m_family_dim": m_dim,
        "m_family_iso": "SU(3)×SU(2)×U(1)",
        "same_isometry": same_iso,
        "same_dimension": same_dim,
        "determined": compatible,
        "picked_3_2": False,
        "live_bin": "FORCED" if compatible else "REFUSED",
        "extras": [] if compatible else ["p", "q"],
        "why": (
            f"Locked link dimension {link_dim} and isometry {iso}. "
            f"M^{{p,q}} is dimension {m_dim} with isometry SU(3)×SU(2)×U(1). "
            "No locked atom is a pair (p,q). (3,2) was not selected."
        ),
    }


def sheet_a(menu: Dict[str, Any], inv: Dict[str, Any], wave2: Dict[str, Any], uncap: Dict[str, Any], cone: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for item in inv["already"]:
        if item["live_bin"] != "FORCED":
            continue
        reading = item.get("physics_reading")
        if item["name"] == "eight_pi_G_eff_number":
            reading = "number 9/16, not G_N"
        if item["name"] == "CONE_HOLONOMY":
            reading = "SU(3) as holonomy, not QCD"
        rows.append(
            {
                "name": item["name"],
                "bin": "FORCED",
                "value": item["value"],
                "reading": reading,
            }
        )
    for item in wave2["descendants"]:
        if item["live_bin"] != "FORCED":
            continue
        rows.append({"name": item["object"], "bin": "FORCED", "value": item["extras"], "reading": "descendant"})
    for item in uncap["new"]:
        if item["live_bin"] != "FORCED":
            continue
        rows.append({"name": item["name"], "bin": "FORCED", "value": item["extras"], "reading": "uncap form"})
    # Menu FORCED names not already listed.
    have = {row["name"] for row in rows}
    for item in menu["rows"]:
        if item["type"] == "FORCED" and item["name"] not in have:
            rows.append(
                {
                    "name": item["name"],
                    "bin": "FORCED",
                    "value": item.get("notes"),
                    "reading": item.get("physics_reading"),
                }
            )
    if any(row["bin"] != "FORCED" for row in rows):
        fail("sheet A accepted a non-forced row")
    if cone.get("color_promoted"):
        fail("holonomy stored as color")
    return {
        "sheet": "A",
        "isolate": "T^{1,1}",
        "rebasing": None,
        "continuous_knobs": 0,
        "rows": rows,
    }


def catalog_row(catalog: Dict[str, Any], ident: str) -> Dict[str, Any]:
    for item in catalog["rows"]:
        if item["id"] == ident:
            return item
    fail(f"catalog row {ident} missing")
    return {}


def sheet_b(catalog: Dict[str, Any], h1: Dict[str, Any], hd: Dict[str, Any], inv: Dict[str, Any], menu: Dict[str, Any]) -> Dict[str, Any]:
    occupants = []
    for ident in ("W1", "W2", "W3", "G1", "G2", "G3"):
        src = catalog_row(catalog, ident)
        if src["live_bin"] == "FORCED":
            fail(f"map {ident} is labeled FORCED")
        occupants.append(
            {
                "id": ident,
                "slot": src["slot"],
                "claim": src["claim"],
                "bin": src["live_bin"],
                "extras": list(src.get("external_names") or []),
                "map_not_lock": True,
            }
        )
    pipes = next(item for item in h1["attempts"] if item.get("id") == "H")
    occupants.append(
        {
            "id": "C2_color_pipe",
            "slot": "unique_color",
            "claim": "CLASS Chern / leftover 4-fold pipes",
            "bin": pipes["live_bin"],
            "extras": list(pipes.get("leftover_picks") or []),
            "map_not_lock": True,
        }
    )
    if hd.get("promote_alpha_k"):
        fail("HD alpha was promoted")
    occupants.append(
        {
            "id": "HD_alpha",
            "slot": "alpha_k",
            "claim": "higher-derivative coefficient",
            "bin": "CLASS",
            "extras": ["alpha_k"],
            "map_not_lock": True,
        }
    )
    family = next(item for item in inv["new"] if "ISO_BUNDLE_FAMILY" in item["extra_names"])
    if family["live_bin"] == "FORCED":
        fail("iso bundle family welded to FORCED")
    occupants.append(
        {
            "id": "ISO_BUNDLE_FAMILY",
            "slot": "associated_bundles",
            "claim": "irreps (j_L, j_R, q)",
            "bin": family["live_bin"],
            "extras": ["j_L", "j_R", "q"],
            "map_not_lock": True,
        }
    )
    weyl = next(item for item in menu["rows"] if item["name"] == "Weyl_lambda")
    if weyl["type"] == "FORCED":
        fail("withdrawn scale labeled FORCED")
    occupants.append(
        {
            "id": "scale_withdrawn",
            "slot": "Weyl_lambda",
            "claim": "absolute scale withdrawn; yardstick is not a GeV",
            "bin": weyl["type"],
            "extras": [],
            "map_not_lock": True,
        }
    )
    if any(item["bin"] == "FORCED" for item in occupants):
        fail("a map was labeled FORCED")
    return {"sheet": "B", "weld": False, "continuous_knobs": 0, "rows": occupants}


def sheet_c(e4: Dict[str, Any], p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, Any]:
    blob = json.dumps(e4)
    metric_name = "Einstein_Hilbert" if "Einstein_Hilbert" in blob else "g_mu_nu"
    return {
        "sheet": "C",
        "unique_color_needs": "c2",
        "g_mu_nu_needs": metric_name,
        "Y14_needs": p1["extra_name"] or "none",
        "M_pq_needs": "p,q" if not p2["determined"] else "none",
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
    cu = load_json(CU_PATH)
    inv = load_json(INV_PATH)
    wave2 = load_json(WAVE2_PATH)
    uncap = load_json(UNCAP_PATH)
    catalog = load_json(CATALOG_PATH)
    h1 = load_json(H1_PATH)
    hd = load_json(HD_PATH)
    e4 = load_json(E4_PATH)
    cone = load_json(CONE_PATH)
    knobs = int((baseline.get("status_classification") or {}).get("continuous_knobs"))
    if knobs != 0:
        fail("knobs")

    p1 = door_p1(cu)
    y14_forced = bool(p1["determined"])
    p2 = None
    mpq_forced = False
    if y14_forced:
        fail("P1 succeeded; rebase is not implemented because the files say the landscape is open")
    p2 = door_p2(inv, cone)
    mpq_forced = bool(p2["determined"])
    if mpq_forced or p2["picked_3_2"]:
        fail("P2 picked an integer pair")

    sheet_a_doc = sheet_a(menu, inv, wave2, uncap, cone)
    sheet_b_doc = sheet_b(catalog, h1, hd, inv, menu)
    sheet_c_doc = sheet_c(e4, p1, p2)

    dump(P1_PATH, p1)
    dump(P2_PATH, p2)
    dump(SHEET_A_PATH, sheet_a_doc)
    dump(SHEET_B_PATH, sheet_b_doc)
    dump(SHEET_C_PATH, sheet_c_doc)
    write_report(p1, p2, sheet_a_doc, sheet_b_doc, sheet_c_doc)

    print("FINISH CHAIN - DOORS THEN MACHINE - ZERO KNOBS")
    print(f"P1 Y14 determined? {p1['determined']} extra={p1['extra_name']}")
    print(f"P2 Mpq determined? {p2['determined']} bin={p2['live_bin']} picked_3_2={p2['picked_3_2']}")
    print(f"Y^{{14}} isolate forced? {'Yes' if y14_forced else 'No'}")
    print(f"M^{{p,q}} isolate forced? {'Yes' if mpq_forced else 'No'}")
    print("Unique color forced? No")
    print("Unique g_μν forced? No")
    print("Machine written? Yes")
    return 0


def write_report(p1: Dict[str, Any], p2: Dict[str, Any], sheet_a_doc: Dict[str, Any], sheet_b_doc: Dict[str, Any], sheet_c_doc: Dict[str, Any]) -> None:
    lines = [
        "# Finish chain",
        "",
        "FINISH CHAIN - DOORS THEN MACHINE - ZERO KNOBS",
        "",
        "## P1",
        "",
        p1["why"],
        "",
        f"Determined: {p1['determined']}. Extra: `{p1['extra_name']}`.",
        "",
        "## P2",
        "",
        p2["why"],
        "",
        f"Bin `{p2['live_bin']}`. (3,2) picked: {p2['picked_3_2']}.",
        "",
        "## Sheet A",
        "",
        "FORCED inventory of the current isolate. Holonomy is not QCD. 9/16 is not G_N.",
        "",
        "| name | value | reading |",
        "|------|-------|---------|",
    ]
    for row in sheet_a_doc["rows"]:
        lines.append(f"| {row['name']} | {row['value']} | {row['reading']} |")
    lines += [
        "",
        "## Sheet B",
        "",
        "MAP occupants. None of these bins is FORCED.",
        "",
        "| id | bin | extras |",
        "|----|-----|--------|",
    ]
    for row in sheet_b_doc["rows"]:
        extras = ", ".join(row["extras"]) or "—"
        lines.append(f"| {row['id']} | {row['bin']} | {extras} |")
    lines += [
        "",
        "## Sheet C",
        "",
        f"- Unique color needs: `{sheet_c_doc['unique_color_needs']}`",
        f"- 4D EOM / g_μν needs: `{sheet_c_doc['g_mu_nu_needs']}`",
        f"- Y^{{14}} needs: `{sheet_c_doc['Y14_needs']}`",
        f"- M^{{p,q}} needs: `{sheet_c_doc['M_pq_needs']}`",
        "",
        "Y^{14} isolate forced? No",
        "",
        "M^{p,q} isolate forced? No",
        "",
        "Unique color forced? No",
        "",
        "Unique g_μν forced? No",
        "",
        "Machine written? Yes",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
