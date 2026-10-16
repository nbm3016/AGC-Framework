#!/usr/bin/env python3
"""
Atom S: Connes reconstruction against the locked isolate.

A commutative spectral triple obeying the spin-manifold axioms
reconstructs one compact oriented Riemannian spin manifold up to isometry.
This probe asks whether locked atoms determine such a triple.
Holonomy of g_C is not a 4D metric. Do not seed g_mu_nu.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

from check_engine import LEGAL, runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
IDEAL_PATH = os.path.join(ARTIFACT_DIR, "constraint_ideal.json")
E4_PATH = os.path.join(ARTIFACT_DIR, "e4_metric_attempts.json")
CONE_JSON = os.path.join(ARTIFACT_DIR, "cone_curvature.json")
CONE_REPORT = os.path.join(ARTIFACT_DIR, "CONE_CURVATURE_REPORT.md")
APS_PATH = os.path.join(ARTIFACT_DIR, "native_aps_index.py")
OUT_PATH = os.path.join(ARTIFACT_DIR, "connes_reconstruct.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "CONNES_RECONSTRUCT_REPORT.md")

SKIP_DIRS = {".git", "mcps", "agent-tools", "__pycache__", "terminals", ".grok"}
AXIOMS = (
    "commutativity of A",
    "bounded commutators and compact resolvent",
    "regularity",
    "order one",
    "orientability (Hochschild cycle represents chirality)",
    "finiteness and absolute continuity",
    "reality operator J and a fixed KO-dimension",
    "Poincare duality",
    "spectral dimension 4",
)


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _is_triple_record(obj: Any) -> bool:
    """A record is a triple only when algebra, Hilbert space, and Dirac are all present."""
    if not isinstance(obj, dict):
        return False
    keys = {str(k).lower() for k in obj}
    has_a = bool(keys & {"algebra", "algebra_a", "a_algebra"})
    has_h = bool(keys & {"hilbert", "hilbert_space", "spinor_module"})
    has_d = bool(keys & {"dirac", "dirac_operator", "operator_d"})
    return has_a and has_h and has_d


def _walk_records(obj: Any, found: List[str], label: str) -> None:
    if _is_triple_record(obj):
        found.append(label)
    if isinstance(obj, dict):
        for key, val in obj.items():
            _walk_records(val, found, f"{label}.{key}")
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            _walk_records(val, found, f"{label}[{i}]")


def scan_disk() -> Dict[str, Any]:
    """Inventory spectral-triple records and a Weyl-law slope. A sentence is not a record."""
    phrase_hits: List[str] = []
    records: List[str] = []
    slope_hits: List[str] = []
    ko_hits: List[str] = []
    fluctuation_hits: List[str] = []
    own = {
        "connes_reconstruct_probe.py",
        "connes_reconstruct.json",
        "CONNES_RECONSTRUCT_REPORT.md",
    }
    for dirpath, dirnames, filenames in os.walk(ARTIFACT_DIR):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            low = name.lower()
            if low.endswith((".png", ".zip", ".pdf", ".pyc")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), ARTIFACT_DIR).replace("\\", "/")
            if rel in own:
                continue
            path = os.path.join(dirpath, name)
            if low.endswith(".json"):
                try:
                    with open(path, encoding="utf-8") as handle:
                        _walk_records(json.load(handle), records, rel)
                except (OSError, json.JSONDecodeError):
                    pass
            if not low.endswith((".py", ".json", ".md", ".txt")):
                continue
            try:
                with open(path, encoding="utf-8", errors="ignore") as handle:
                    for lineno, line in enumerate(handle, 1):
                        text = line.lower()
                        if "spectral triple" in text or "twisted spectral" in text:
                            phrase_hits.append(f"{rel}:{lineno}")
                        if ("weyl" in text and "slope" in text) or "weyl_slope" in text or "weyl law" in text:
                            slope_hits.append(f"{rel}:{lineno}")
                        if "ko-dimension" in text or "ko_dimension" in text or "kodimension" in text:
                            ko_hits.append(f"{rel}:{lineno}")
                        if "inner fluctuation" in text or "inner_fluctuation" in text:
                            fluctuation_hits.append(f"{rel}:{lineno}")
            except OSError:
                continue
    return {
        "triple_phrase_mentions": sorted(set(phrase_hits)),
        "triple_records": sorted(set(records)),
        "weyl_slope_mentions": sorted(set(slope_hits)),
        "ko_dimension_mentions": sorted(set(ko_hits)),
        "inner_fluctuation_mentions": sorted(set(fluctuation_hits)),
    }


def axiom_table(triple_count: int) -> List[Dict[str, Any]]:
    rows = []
    for name in AXIOMS:
        rows.append(
            {
                "axiom": name,
                "holds_for_a_unique_isolate_triple": triple_count == 1,
                "why": (
                    "one stored triple would still need a field check"
                    if triple_count == 1
                    else "no (A, H, D) record is on disk, so the axiom is not instantiated"
                ),
            }
        )
    return rows


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)
    if not os.path.isfile(CONE_JSON) or not os.path.isfile(CONE_REPORT):
        fail("cone curvature tables are missing")

    baseline = load_json(BASELINE_PATH)
    menu_doc = load_json(MENU_PATH)
    ideal = load_json(IDEAL_PATH)
    e4 = load_json(E4_PATH)
    cone = load_json(CONE_JSON)
    sc = baseline.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0 or n_gen != 3:
        fail("knobs/N_gen")

    rows = menu_doc.get("rows") or []
    protected = ("unique_color", "Iso_group", "CONE_HOLONOMY", "g_mu_nu", "warp_factor")
    types0 = {name: next(r["type"] for r in rows if r["name"] == name) for name in protected}
    g_row = next(r for r in rows if r["name"] == "g_mu_nu")
    hol_row = next(r for r in rows if r["name"] == "CONE_HOLONOMY")
    value_forced_before = bool(g_row.get("value_forced"))

    inventory = scan_disk()
    triple_count = len(inventory["triple_records"])
    slope_on_disk = len(inventory["weyl_slope_mentions"]) > 0
    ko_on_disk = len(inventory["ko_dimension_mentions"]) > 0
    fluctuation_on_disk = len(inventory["inner_fluctuation_mentions"]) > 0
    axioms = axiom_table(triple_count)
    axioms_hold = triple_count == 1 and all(row["holds_for_a_unique_isolate_triple"] for row in axioms)

    aps_text = open(APS_PATH, encoding="utf-8").read()
    internal_dirac_is_4d = ("not a computation of ker D_5" not in aps_text)
    # Finite zero-mode count versus an L2 spinor space.
    finite_count_determines_H = False

    positive_eom = list(ideal.get("positive_eom") or [])
    dynamical_empty = len(positive_eom) == 0
    if bool(ideal.get("dynamical_empty")) != dynamical_empty:
        fail("constraint_ideal dynamical_empty flag disagrees with positive_eom")

    unique_A = triple_count == 1
    unique_H = finite_count_determines_H and unique_A
    unique_D = unique_A and ko_on_disk and fluctuation_on_disk and (not internal_dirac_is_4d)
    slope_is_triple = False
    unique_metric = bool(axioms_hold and unique_A and unique_H and unique_D and knobs == 0)
    # A Weyl slope is a real number, not (A, H, D), so it cannot finish the triple.
    if slope_on_disk and not slope_is_triple:
        unique_metric = unique_metric and triple_count == 1

    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": rows,
        "sigma_star_locked": True,
        "warp_forced": False,
        "unique_4fold": False,
        "isolate_written": False,
    }

    claims = [
        {
            "id": "N1",
            "text": "Is a unique algebra A forced by locked atoms (not picked C^infty(M^4))?",
            "yes_as_lock": {"map_called_lock": True},
            "uses_modulus": "C_infty_M4",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "N2",
            "text": "Is a unique Hilbert space H / spinor module forced?",
            "yes_as_lock": {"map_called_lock": True},
            "uses_modulus": "spinor_module_H",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "N3",
            "text": "Is a unique Dirac D forced (no free KO-dimension, no free inner-fluctuation knobs)?",
            "yes_as_lock": {"free_real": True, "new_real": True},
            "uses_modulus": "KO_dimension",
        },
        {
            "id": "N4",
            "text": "Do the reconstruction axioms hold for that unique triple with spectral dimension 4?",
            "yes_as_lock": {"map_called_lock": True},
            "uses_modulus": "spectral_dimension_4",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "N5",
            "text": "Does Weyl slope 2 by itself force (M^4, g)?",
            "yes_as_lock": {"map_called_lock": True},
            "uses_modulus": "weyl_slope_2",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "N6",
            "text": "Does reconstruction force a unique g_mu_nu(x) modulo diffeomorphism / Weyl already GAUGE?",
            "yes_as_lock": {"modulus_called_lock": True},
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "N7",
            "text": "May we pick eta_mu_nu / FLRW / RS because N6 failed?",
            "yes_as_lock": {"weld_class_to_lock": True},
            "uses_modulus": "eta_mu_nu",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "N8",
            "text": "Does 9/16 become G_N, or sigma* become g?",
            "yes_as_lock": {"geff_as_GN": True, "sigma_is_gmunu": True},
            "uses_modulus": "eight_pi_G_eff_as_G_N",
            "labels_modulus_as": "G_N",
        },
    ]
    unique_flag = {
        "N1": unique_A,
        "N2": unique_H,
        "N3": unique_D,
        "N4": axioms_hold,
        "N5": False,
        "N6": unique_metric,
        "N7": False,
        "N8": False,
    }
    inventory_why = {
        "N1": (
            f"structured (A, H, D) records: {triple_count}. "
            f"Phrase mentions: {len(inventory['triple_phrase_mentions'])}. "
            "A sentence is not an algebra."
        ),
        "N2": f"N_gen={n_gen} is a finite wall-index count. An L2 spinor space is not determined by that count.",
        "N3": (
            f"KO-dimension mentions: {len(inventory['ko_dimension_mentions'])}. "
            f"Inner-fluctuation mentions: {len(inventory['inner_fluctuation_mentions'])}. "
            "native_aps_index.py states the wall-index rule is not ker D_5."
        ),
        "N4": f"axioms instantiated for a unique triple: {axioms_hold}. Forced dims on disk are the 5-link, the 6-cone, and the 14D fibration.",
        "N5": (
            f"Weyl-slope mentions: {len(inventory['weyl_slope_mentions'])}. "
            "A slope is not A, not H, not D, and not g."
        ),
        "N6": "Reconstruction needs a unique triple. None is stored, so g is not reconstructed.",
        "N7": "A failed reconstruction does not license a named 4D metric.",
        "N8": "8πG_eff = 9/16 is a locked pure number. σ* is the 5-shape.",
    }

    live_rows = []
    print("id | claim | unique? | live_bin | gates | why")
    for claim in claims:
        cid = claim["id"]
        if unique_flag[cid]:
            live = {
                "bin": "FORCED",
                "gates": [],
                "reasons": [inventory_why[cid]],
                "unique": True,
            }
        else:
            live = runCheck(claim, facts)
            live["unique"] = False
            live["reasons"] = [inventory_why[cid]] + list(live.get("reasons") or [])
        if live["bin"] not in LEGAL:
            fail(f"{cid} illegal bin")
        if live.get("gates") and live["bin"] != "REFUSED":
            fail(f"{cid} gate without REFUSED")
        if cid in {"N7", "N8"} and live["bin"] != "REFUSED":
            fail(f"{cid} must refuse")
        row = {"id": cid, "text": claim["text"], **live}
        live_rows.append(row)
        why = "; ".join(live["reasons"])
        print(
            f"{cid} | {claim['text']} | {'Yes' if live['unique'] else 'No'} | "
            f"{live['bin']} | {live.get('gates', [])} | {why}"
        )

    by_id = {row["id"]: row for row in live_rows}
    if by_id["N6"]["unique"] and knobs == 0:
        g_row["value_forced"] = True
        g_row["type"] = "FORCED"
        fail("N6 upgraded g_mu_nu; this path is closed unless a triple exists")
    if g_row.get("type") != "OPEN-FIELD" or g_row.get("value_forced"):
        fail("g_mu_nu moved")
    if value_forced_before:
        fail("g_mu_nu value_forced was already true")

    types1 = {name: next(r["type"] for r in rows if r["name"] == name) for name in protected}
    if types1 != types0:
        fail(f"protected types changed: {types0} -> {types1}")
    if any(r.get("name") == "SU(3)_c" for r in rows):
        fail("SU(3)_c added")

    e4_m6 = next((row for row in e4.get("M", e4.get("rows", [])) if row.get("id") == "M6"), None)
    if e4_m6 is None:
        e4_rows = e4.get("questions") or e4.get("attempts") or []
        # e4 file stores questions at top level under a list key; fall back to scanning.
        blob = json.dumps(e4)
        e4_unique = '"id": "M6"' in blob and '"unique": false' in blob
    else:
        e4_unique = bool(e4_m6.get("unique"))
    # Read M6 directly from the known list key used by e4_metric_probe.
    m6 = None
    for key, val in e4.items():
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict) and item.get("id") == "M6":
                    m6 = item
    if m6 is None:
        fail("E4 M6 row missing")
    e4_value_forced = bool(e4.get("value_forced"))

    payload = {
        "module": "connes_reconstruct",
        "banner": "CONNES RECONSTRUCT - TRIPLE != METRIC - ZERO KNOBS",
        "continuous_knobs": knobs,
        "N_gen": n_gen,
        "inventory": inventory,
        "axioms": axioms,
        "internal_wall_index_is_4d_dirac": internal_dirac_is_4d,
        "dynamical_empty": dynamical_empty,
        "positive_eom_count": len(positive_eom),
        "hol_of_cone": cone.get("hol"),
        "g_C_flat": cone.get("g_C_flat"),
        "hol_is_4d_metric": False,
        "cone_holonomy_reading": hol_row.get("physics_reading"),
        "g_mu_nu_type": g_row.get("type"),
        "g_mu_nu_value_forced": bool(g_row.get("value_forced")),
        "unique_spectral_triple": bool(unique_A and unique_H and unique_D and axioms_hold),
        "unique_g_mu_nu": bool(by_id["N6"]["unique"]),
        "color_type": types1["unique_color"],
        "N": live_rows,
        "not_input_comparison": {
            "label": "NOT INPUT",
            "e4_value_forced": e4_value_forced,
            "e4_M6_bin": m6.get("bin"),
            "e4_M6_unique": m6.get("unique"),
            "e4_note": "E4 metric value was not forced. That row was not edited.",
            "dynamical_ideal_empty": dynamical_empty,
            "weyl_slope_on_disk": slope_on_disk,
            "weyl_slope_is_a_triple": slope_is_triple,
            "hol": cone.get("hol"),
            "hol_note": "Hol(g_C) is holonomy of the cone. It is not g_mu_nu(x).",
        },
        "isolate_written": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    if e4_unique and m6.get("unique") is True:
        payload["not_input_comparison"]["e4_disagreement"] = True
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    write_report(payload)

    print()
    print("CONNES RECONSTRUCT - TRIPLE != METRIC - ZERO KNOBS")
    print(
        "Unique spectral triple from Layer A? "
        + ("Yes" if payload["unique_spectral_triple"] else "No")
    )
    print(f"Unique g_mu_nu from Layer A? {'Yes' if payload['unique_g_mu_nu'] else 'No'}")
    print(f"Dynamical ideal still empty? {'Yes' if dynamical_empty else 'No'}")
    print(f"Unique color unchanged FORBIDDEN? {'Yes' if types1['unique_color'] == 'FORBIDDEN' else 'No'}")
    print("METRIC_PROMOTED: NO")
    if payload["unique_g_mu_nu"] or types1["unique_color"] != "FORBIDDEN" or not dynamical_empty:
        fail("final lines inconsistent with the inventory")
    return 0


def write_report(payload: Dict[str, Any]) -> None:
    inv = payload["inventory"]
    comp = payload["not_input_comparison"]
    lines = [
        "# Connes reconstruction",
        "",
        "CONNES RECONSTRUCT - TRIPLE != METRIC - ZERO KNOBS",
        "",
        "A commutative spectral triple that satisfies the spin-manifold axioms reconstructs one compact oriented Riemannian spin manifold up to isometry. "
        "The isolate determines that manifold only when it determines the triple. "
        f"Structured (A, H, D) records: {len(inv['triple_records'])}. "
        f"Phrase mentions: {len(inv['triple_phrase_mentions'])}. "
        f"KO-dimension mentions: {len(inv['ko_dimension_mentions'])}. "
        f"Inner-fluctuation mentions: {len(inv['inner_fluctuation_mentions'])}. "
        f"Weyl-slope mentions: {len(inv['weyl_slope_mentions'])}.",
        "",
        "The Module A wall-index rule produces a finite zero-mode count. "
        "Its source file states that this rule is not `ker D_5`. "
        "That count is not a Hilbert space of 4D spinors and not a Dirac operator of a reconstructed 4-manifold.",
        "",
        f"`Hol(g_C) = {payload['hol_of_cone']}` is holonomy of the cone (`g_C` flat: {payload['g_C_flat']}). "
        f"Menu reading: {payload['cone_holonomy_reading']}. "
        "That holonomy is not `g_mu_nu(x)`.",
        "",
        f"Dynamical ideal: `positive_eom` has {payload['positive_eom_count']} rows. Empty: {payload['dynamical_empty']}.",
        "",
        "## Axioms",
        "",
        "| axiom | holds for a unique isolate triple |",
        "|-------|-------------------------------------|",
    ]
    for row in payload["axioms"]:
        lines.append(f"| {row['axiom']} | {row['holds_for_a_unique_isolate_triple']} |")
    lines += [
        "",
        "## Questions",
        "",
        "| id | claim | unique? | live_bin | gates | why |",
        "|----|-------|---------|----------|-------|-----|",
    ]
    for row in payload["N"]:
        why = "; ".join(row.get("reasons") or []).replace("|", "/")
        gates = ",".join(row.get("gates") or []) or "—"
        uniq = "Yes" if row.get("unique") else "No"
        lines.append(f"| {row['id']} | {row['text']} | {uniq} | {row['bin']} | {gates} | {why} |")
    lines += [
        "",
        f"`g_mu_nu` stays `{payload['g_mu_nu_type']}` with `value_forced = {payload['g_mu_nu_value_forced']}`. "
        f"Unique color stays `{payload['color_type']}`. "
        "`Iso_group` and `CONE_HOLONOMY` types are unchanged.",
        "",
        "## Comparison (NOT INPUT)",
        "",
        f"E4 `value_forced = {comp['e4_value_forced']}`, M6 bin `{comp['e4_M6_bin']}`, unique `{comp['e4_M6_unique']}`. "
        f"{comp['e4_note']}",
        "",
        f"Dynamical ideal empty: {comp['dynamical_ideal_empty']}.",
        "",
        f"Weyl slope on disk: {comp['weyl_slope_on_disk']}. Treated as a triple: {comp['weyl_slope_is_a_triple']}.",
        "",
        f"{comp['hol_note']}",
        "",
        "## Answers",
        "",
        "Unique spectral triple from Layer A? "
        + ("Yes" if payload["unique_spectral_triple"] else "No"),
        "Unique g_mu_nu from Layer A? No",
        f"Dynamical ideal still empty? {'Yes' if payload['dynamical_empty'] else 'No'}",
        "Unique color unchanged FORBIDDEN? Yes",
        "",
        "METRIC_PROMOTED: NO",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
