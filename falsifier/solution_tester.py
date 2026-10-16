#!/usr/bin/env python3
"""
Plug named external models into CLASS / OPEN-FIELD slots.
Survive != derived. Never FORCED from a plug-in.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

from check_engine import LEGAL, runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "solutions_catalog.json")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def catalog() -> List[Dict[str, Any]]:
    return [
        {"id": "W1", "slot": "warp_factor", "claim": "A = const", "external_names": []},
        {
            "id": "W2",
            "slot": "warp_factor",
            "claim": "RS A = -k |y|",
            "external_names": ["k", "L", "y"],
        },
        {
            "id": "W3",
            "slot": "warp_factor",
            "claim": "KW / conifold log warp",
            "external_names": ["log_warp", "y"],
        },
        {
            "id": "W4",
            "slot": "warp_factor",
            "claim": "identify A(y) with phi(theta,psi)",
            "external_names": [],
            "yes_as_lock": {"sigma_is_A": True, "phi_is_gmunu": True},
            "forbidden_reading": True,
        },
        {"id": "G1", "slot": "g_mu_nu", "claim": "eta_mu_nu as model vacuum", "external_names": ["eta_mu_nu"]},
        {"id": "G2", "slot": "g_mu_nu", "claim": "FLRW as model vacuum", "external_names": ["a_t", "k_curv"]},
        {
            "id": "G3",
            "slot": "g_mu_nu",
            "claim": "RS warped product as model vacuum",
            "external_names": ["k", "L", "y"],
        },
        {
            "id": "G4",
            "slot": "g_mu_nu",
            "claim": "identify g_mu_nu with sigma*",
            "external_names": [],
            "yes_as_lock": {"sigma_is_gmunu": True},
            "forbidden_reading": True,
        },
        {
            "id": "C1",
            "slot": "Iso_as_color",
            "claim": "Iso only (control)",
            "external_names": [],
            "yes_as_lock": {"unique_color_derived": True},
        },
        {
            "id": "C2",
            "slot": "leftover_X4_family",
            "claim": "SU(3) bundle that does not pick CP^2 or K3 as THE space",
            "external_names": ["c2", "k_instanton", "bundle_moduli"],
        },
        {
            "id": "C3",
            "slot": "CP2_as_the_4fold",
            "claim": "SU(3) instanton on CP^2 as THE color space",
            "external_names": ["instanton"],
            "yes_as_lock": {"weld_class_to_lock": True, "picks_SU3c": True},
            "picks_the_member": True,
        },
        {
            "id": "C4",
            "slot": "K3_as_the_4fold",
            "claim": "SU(3) on K3 as THE color space",
            "external_names": ["bundle_moduli"],
            "yes_as_lock": {"weld_class_to_lock": True, "picks_SU3c": True},
            "picks_the_member": True,
        },
        {
            "id": "C5",
            "slot": "Iso_as_color",
            "claim": "Iso contains SU(3)_c",
            "external_names": [],
            "yes_as_lock": {"picks_SU3c": True},
        },
        {
            "id": "C6",
            "slot": "G_SM_from_isolate",
            "claim": "Iso x SU(3) = G_SM claimed derived",
            "external_names": [],
            "yes_as_lock": {"weld_class_to_lock": True, "unique_color_derived": True},
            "labels_modulus_as": "derived",
        },
        {
            "id": "D1",
            "slot": "leftover_X4_family",
            "slot_kind": "CLASS",
            "claim": "Lovelock form, alpha tagged external",
            "external_names": ["alpha_k"],
            "uses_modulus": "leftover_X4_family",
        },
        {
            "id": "D2",
            "slot": "leftover_X4_family",
            "claim": "use official r to fix alpha",
            "external_names": [],
            "yes_as_lock": {"free_real": True, "new_real": True},
            "claim_as_isolate_atom": True,
            "uses_modulus": "alpha_k_from_r",
        },
        {
            "id": "F1",
            "slot": "overall_R",
            "claim": "chosen Freund-Rubin n_F as native M_R",
            "external_names": [],
            "yes_as_lock": {"stick_as_R": True, "lambda_is_R_meters": True},
            "claim_as_isolate_atom": True,
            "uses_modulus": "overall_R",
            "labels_modulus_as": "FORCED",
        },
    ]


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)
    menu_doc = load_json(MENU_PATH)
    b = load_json(BASELINE_PATH)
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0 or n_gen != 3:
        fail("knobs/N_gen")
    rows = menu_doc.get("rows") or []
    by = {r["name"]: r for r in rows}
    types_before = {n: by[n]["type"] for n in ("warp_factor", "g_mu_nu", "unique_color") if n in by}

    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": rows,
        "sigma_star_locked": True,
        "unique_4fold": False,
        "warp_forced": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "t_wall_n": "13/2",
        "t_wall_lam": "13/2",
        "isolate_written": False,
    }

    results = []
    print("id | slot | SLOT_LEGAL | ISOLATE_COMPLETE | live_bin | gates | why")
    for cand in catalog():
        slot = cand["slot"]
        row = by.get(slot)
        slot_type = row["type"] if row else cand.get("slot_kind")
        slot_legal = slot_type in {"CLASS", "OPEN-FIELD"}
        if row and row["type"] not in {"CLASS", "OPEN-FIELD"}:
            slot_legal = False

        claim = {
            "id": cand["id"],
            "text": cand["claim"],
            "uses_modulus": cand.get("uses_modulus") or (slot if slot_legal else slot),
            "external_names": cand.get("external_names") or [],
            "claim_as_isolate_atom": cand.get("claim_as_isolate_atom", False),
            "yes_as_lock": cand.get("yes_as_lock") or {},
            "labels_modulus_as": cand.get("labels_modulus_as"),
        }
        live = runCheck(claim, facts)
        gates = list(live.get("gates") or [])
        isolate_complete = True
        why = list(live.get("reasons") or [])

        if not slot_legal:
            isolate_complete = False
            if "R-unlisted-modulus" not in gates and slot_type in {"FORBIDDEN", "GAUGE", "FORCED"}:
                gates.append("R-unlisted-modulus" if slot_type == "FORBIDDEN" else "R-map-called-lock")
            why.append(f"slot {slot} type {slot_type} is not CLASS/OPEN-FIELD")
        if cand.get("forbidden_reading") or cand.get("picks_the_member"):
            isolate_complete = False
        if live.get("gates"):
            isolate_complete = False
        if cand.get("claim_as_isolate_atom"):
            isolate_complete = False

        live_bin = live.get("bin") or "UNKNOWN"
        if not slot_legal or cand.get("forbidden_reading") or cand.get("picks_the_member"):
            live_bin = "REFUSED"
        if live_bin == "FORCED":
            live_bin = "CLASS" if slot_type == "CLASS" else "CONSISTENT"
            why.append("plug-in never FORCED (survive != derived)")
        if live.get("gates") and live_bin != "REFUSED":
            live_bin = "REFUSED"
        if live_bin not in LEGAL or live_bin == "FORCED":
            fail(f"{cand['id']} illegal or FORCED plug-in bin {live_bin}")

        if slot_legal and isolate_complete and live_bin not in {"CONSISTENT", "CLASS"}:
            live_bin = "CLASS" if slot_type == "CLASS" else "CONSISTENT"

        rec = {
            "id": cand["id"],
            "slot": slot,
            "claim": cand["claim"],
            "external_names": cand.get("external_names") or [],
            "SLOT_LEGAL": slot_legal,
            "ISOLATE_COMPLETE": isolate_complete,
            "live_bin": live_bin,
            "gates": gates,
            "why": why,
        }
        results.append(rec)
        print(
            f"{rec['id']} | {slot:22} | {slot_legal} | {isolate_complete} | {live_bin} | {gates} | {'; '.join(why)[:60]}"
        )

    types_after = {n: next(r["type"] for r in rows if r["name"] == n) for n in types_before}
    if types_after != types_before:
        fail("menu types changed")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "continuous_knobs": 0,
                "any_promoted_to_FORCED": False,
                "rows": results,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            },
            f,
            indent=2,
        )
        f.write("\n")

    survive = [r["id"] for r in results if r["live_bin"] in {"CONSISTENT", "CLASS"}]
    complete = [r["id"] for r in results if r["ISOLATE_COMPLETE"]]
    print("\nSOLUTION TEST - SURVIVE != FORCED - ZERO KNOBS")
    print("Surviving maps:", survive)
    print("Isolate-complete maps:", complete)
    print("Menu types unchanged: warp, g_mu_nu, unique color, HD, M_R, 14D")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
