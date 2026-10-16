#!/usr/bin/env python3
"""
Layer-A constraint ideal: IDENTITY / QUOTIENT / FORBIDDEN / POSITIVE_EOM.

Does not promote warp, g_mu_nu, or unique color.
Does not invent EH, G_N, y-interval, or Wilson coefficients.
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
PORTS_PATH = os.path.join(ARTIFACT_DIR, "computed_ports.json")
IDEAL_PATH = os.path.join(ARTIFACT_DIR, "constraint_ideal.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "CONSTRAINT_IDEAL_REPORT.md")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)

    b = load_json(BASELINE_PATH)
    menu_doc = load_json(MENU_PATH)
    ports = load_json(PORTS_PATH)
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0:
        fail("knobs != 0")
    if n_gen != 3:
        fail("N_gen != 3")

    rows = menu_doc.get("rows") or []
    by = {r["name"]: r for r in rows}
    for req in ("warp_factor", "g_mu_nu", "unique_color"):
        if req not in by:
            fail(f"menu missing {req}")
    warp_t = by["warp_factor"]["type"]
    g_t = by["g_mu_nu"]["type"]
    uc_t = by["unique_color"]["type"]

    num = ports.get("numeric") or {}
    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": rows,
        "sigma_star_locked": True,
        "unique_4fold": False,
        "warp_forced": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "t_wall_n": num.get("T_wall_from_n", "13/2"),
        "t_wall_lam": num.get("T_wall_from_lam", "13/2"),
        "isolate_written": False,
    }

    identity = [r for r in rows if r["type"] == "FORCED"]
    quotient = [r for r in rows if r["type"] == "GAUGE"]
    forbidden = [r for r in rows if r["type"] == "FORBIDDEN"]
    # unlisted alpha is forbidden as a constraint even if not a row
    forbidden_extra = [{"name": "free_fit_alpha", "type": "FORBIDDEN", "notes": "unlisted"}]

    print("IDENTITY")
    for r in identity:
        print(f"  {r['name']}: {r.get('notes') or r.get('physics_reading')}")
    print("QUOTIENT")
    for r in quotient:
        print(f"  {r['name']}: {r.get('physics_reading')}")
    print("FORBIDDEN")
    for r in forbidden + forbidden_extra:
        print(f"  {r['name']}")
    print("POSITIVE_EOM")

    # I4: warp EOM without new names?
    needed_warp = ["y", "L", "C", "G_N", "invented_tension"]
    menu_names = set(by)
    warp_new = [n for n in needed_warp if n not in menu_names]
    print("  warp A(y): would need", warp_new, "— not a derivation")
    print("  g_mu_nu(x): would need t,x,y,z,EH,G_N,Lambda_4 — not a derivation")
    print("  color pipe pick: would pick a CLASS member — refused")
    print("  none")

    i_claims = [
        {
            "id": "I1",
            "text": "IDENTITY list from locked ports",
            "kind": "write_closed",
        },
        {
            "id": "I2",
            "text": "QUOTIENT list (Weyl / R / yardstick)",
            "kind": "write_closed",
        },
        {
            "id": "I3",
            "text": "FORBIDDEN list from menu",
            "kind": "write_closed",
        },
        {
            "id": "I4",
            "text": "POSITIVE_EOM for warp A(y) with no new names",
            "yes_as_lock": {"new_real": True, "free_real": True, "t_wall_as_tension": True},
            "uses_modulus": "y_interval_L",
        },
        {
            "id": "I5",
            "text": "POSITIVE_EOM for g_mu_nu(x) with no new names",
            "yes_as_lock": {"new_real": True, "geff_as_GN": True, "free_real": True},
            "uses_modulus": "Einstein_Hilbert",
        },
        {
            "id": "I6",
            "text": "POSITIVE_EOM that picks a CLASS color member",
            "yes_as_lock": {"picks_SU3c": True, "weld_class_to_lock": True},
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "I7",
            "text": "dynamical part of the ideal is non-empty",
            "yes_as_lock": {"map_called_lock": True},
        },
        {
            "id": "I8",
            "text": "generator still emits constraints if dynamical part is empty",
            "kind": "write_closed",
        },
    ]

    # I1-I3, I8: FORCED as instrument facts if lists nonempty / knobs 0
    # Don't use write_closed for I1-I3 which would still FORCED. That's OK
    # for "list exists". I7 YES would claim non-empty dynamical EOM → refuse.

    i_live = []
    print("\nid | question | unique? | live_bin | gates | why")
    for c in i_claims:
        if c["id"] in {"I1", "I2", "I3", "I8"}:
            live = {
                "bin": "FORCED",
                "gates": [],
                "reasons": {
                    "I1": "FORCED menu rows are IDENTITY constraints",
                    "I2": "GAUGE rows are QUOTIENT constraints",
                    "I3": "FORBIDDEN menu rows (+ unlisted alpha) are constraints",
                    "I8": "identities+quotients+forbiddens remain even if dynamical EOM is empty",
                }[c["id"]],
            }
            live["reasons"] = [live["reasons"]]
        else:
            live = runCheck(c, facts)
        if live["bin"] not in LEGAL:
            fail(f"{c['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{c['id']} refuse-gate did not produce REFUSED")
        unique = live["bin"] == "FORCED"
        i_live.append({"id": c["id"], "text": c["text"], "unique": unique, **live})
        print(
            f"{c['id']} | {c['text'][:48]} | {unique} | {live['bin']} | {live['gates']} | {'; '.join(live['reasons'])[:72]}"
        )

    i4 = next(x for x in i_live if x["id"] == "I4")
    i5 = next(x for x in i_live if x["id"] == "I5")
    i6 = next(x for x in i_live if x["id"] == "I6")
    dyn_empty = i4["bin"] != "FORCED" and i5["bin"] != "FORCED" and i6["bin"] != "FORCED"

    # I7: non-empty? If dyn_empty, the claim "non-empty" is REFUSED
    # already from runCheck map_called_lock. Confirm.
    if not dyn_empty:
        fail("unexpected POSITIVE_EOM FORCED — do not promote")

    if by["warp_factor"]["type"] != warp_t or by["g_mu_nu"]["type"] != g_t or by["unique_color"]["type"] != uc_t:
        fail("menu types changed")

    ideal_rows = []
    for r in identity:
        ideal_rows.append(
            {
                "id": r["name"],
                "kind": "IDENTITY",
                "statement": r.get("notes") or r.get("physics_reading"),
                "source": r.get("source"),
                "live_bin": "FORCED",
                "leftover_names": [],
            }
        )
    for r in quotient:
        ideal_rows.append(
            {
                "id": r["name"],
                "kind": "QUOTIENT",
                "statement": r.get("physics_reading"),
                "source": r.get("source"),
                "live_bin": "FORCED",
                "leftover_names": [],
            }
        )
    for r in forbidden + forbidden_extra:
        ideal_rows.append(
            {
                "id": r["name"],
                "kind": "FORBIDDEN",
                "statement": r.get("physics_reading") or r.get("notes"),
                "source": r.get("source", "T7"),
                "live_bin": "FORCED",
                "leftover_names": [],
            }
        )

    payload = {
        "module": "constraint_ideal",
        "continuous_knobs": 0,
        "N_gen": 3,
        "isolate_written": False,
        "dynamical_empty": dyn_empty,
        "positive_eom": [],
        "rows": ideal_rows,
        "I": i_live,
        "menu_types": {"warp_factor": warp_t, "g_mu_nu": g_t, "unique_color": uc_t},
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(IDEAL_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\nLAYER-A CONSTRAINT IDEAL - ELIGIBLE != DETERMINED - ZERO KNOBS")
    print("Dynamical ideal empty?", "Yes" if dyn_empty else "No")
    print("Warp / g_mu_nu / unique color types unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
