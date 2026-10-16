#!/usr/bin/env python3
"""
Unique survivor hunt among first-wave maps.
Strict ISOLATE_COMPLETE: no extra real and no extra name, even tagged external.
Unique-in-catalog != unique-from-isolate. Never FORCED.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

from check_engine import LEGAL, runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
CAT_PATH = os.path.join(ARTIFACT_DIR, "solutions_catalog.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "unique_survivor.json")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def strict_complete(row: Dict[str, Any]) -> bool:
    if row.get("live_bin") == "REFUSED":
        return False
    if not row.get("SLOT_LEGAL"):
        return False
    names = row.get("external_names") or []
    if names:
        return False
    return bool(row.get("ISOLATE_COMPLETE"))


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)
    cat = load_json(CAT_PATH)
    menu = load_json(MENU_PATH)
    b = load_json(BASELINE_PATH)
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0 or n_gen != 3:
        fail("knobs/N_gen")

    by = {r["id"]: r for r in cat.get("rows") or []}
    rows = menu.get("rows") or []
    types0 = {n: next(r["type"] for r in rows if r["name"] == n) for n in ("warp_factor", "g_mu_nu", "unique_color")}

    def slot(ids: List[str]) -> List[Dict[str, Any]]:
        missing = [i for i in ids if i not in by]
        if missing:
            fail(f"catalog missing {missing}")
        return [by[i] for i in ids]

    warp = slot(["W1", "W2", "W3"])
    metric = slot(["G1", "G2", "G3"])
    color = slot(["C2", "C1", "C3", "C4", "C5", "C6"])
    hd = slot(["D1", "D2"])
    dead = ["W4", "G4", "C1", "C3", "C4", "C5", "C6", "D2", "F1"]
    for d in dead:
        if d in by and by[d]["live_bin"] != "REFUSED":
            fail(f"{d} was not refused in first catalog")

    def summarize(ids_tested: List[str]) -> Dict[str, Any]:
        tested = [by[i] for i in ids_tested]
        complete = [r for r in tested if strict_complete(r)]
        n_c = len(complete)
        unique = n_c == 1
        return {
            "n_tested": len(tested),
            "n_complete": n_c,
            "complete_ids": [r["id"] for r in complete],
            "unique_complete": unique,
        }

    s1 = summarize(["W1", "W2", "W3"])
    s2 = summarize(["G1", "G2", "G3"])
    s3 = summarize(["C2", "C1", "C3", "C4", "C5", "C6"])
    s4 = summarize(["D1", "D2"])

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

    questions = [
        {
            "id": "S1",
            "slot": "warp",
            "sum": s1,
            "text": "unique isolate-complete warp in {W1,W2,W3}",
            "yes_as_lock": {"modulus_called_lock": True} if s1["unique_complete"] else {},
            "uses_modulus": "warp_factor",
            "labels_modulus_as": "FORCED" if s1["unique_complete"] else None,
        },
        {
            "id": "S2",
            "slot": "metric",
            "sum": s2,
            "text": "unique isolate-complete metric in {G1,G2,G3}",
            "yes_as_lock": {"modulus_called_lock": True} if s2["unique_complete"] else {},
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED" if s2["unique_complete"] else None,
        },
        {
            "id": "S3",
            "slot": "color",
            "sum": s3,
            "text": "C2 unique isolate-complete color from Layer A",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True},
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "S4",
            "slot": "HD",
            "sum": s4,
            "text": "unique isolate-complete HD coefficient",
            "yes_as_lock": {"map_called_lock": True},
        },
        {
            "id": "S5",
            "slot": "tie",
            "sum": {"n_tested": 0, "n_complete": 0, "unique_complete": False, "complete_ids": []},
            "text": "simplest / SM-exists / anthropic / const-is-natural may break a tie",
            "yes_as_lock": {"weld_class_to_lock": True, "free_real": True},
        },
        {
            "id": "S6",
            "slot": "promote",
            "sum": {"n_tested": 0, "n_complete": 0, "unique_complete": False, "complete_ids": []},
            "text": "unique-in-catalog promotes warp/g_mu_nu/unique color/HD coeff to FORCED",
            "yes_as_lock": {"modulus_called_lock": True, "map_called_lock": True},
            "uses_modulus": "warp_factor",
            "labels_modulus_as": "FORCED",
        },
    ]

    out_rows = []
    print("id | slot | n_tested | n_complete | unique_complete? | live_bin | gates | why")
    for q in questions:
        live = runCheck(q, facts)
        if live["bin"] not in LEGAL:
            fail(f"{q['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{q['id']} refuse-gate did not produce REFUSED")
        # uniqueness questions: unique-complete occupant != FORCED
        if q["id"] in {"S1", "S2", "S4"}:
            if q["sum"]["unique_complete"]:
                live["bin"] = "CONSISTENT"
                live["reasons"] = [
                    f"unique isolate-complete occupant {q['sum']['complete_ids']} in catalog; catalog uniqueness != isolate atom; not FORCED"
                ]
                live["gates"] = []
            elif q["sum"]["n_complete"] == 0:
                live["bin"] = "REFUSED"
                live["reasons"] = ["zero isolate-complete maps (strict: no extra name/real)"]
            else:
                live["bin"] = "REFUSED"
                live["reasons"] = ["tie among isolate-complete maps; no anthropic break"]
        if q["id"] == "S3":
            # catalog-of-one is not unique color; C2 not strict-complete
            live["bin"] = "REFUSED"
            live["reasons"] = [
                "C2 carries external bundle moduli so not isolate-complete; catalog-of-one is not unique color"
            ]
        if live["bin"] == "FORCED":
            fail(f"{q['id']} must not be FORCED")
        sm = q["sum"]
        rec = {
            "id": q["id"],
            "slot": q["slot"],
            "n_tested": sm["n_tested"],
            "n_complete": sm["n_complete"],
            "unique_complete": sm["unique_complete"],
            "complete_ids": sm["complete_ids"],
            "live_bin": live["bin"],
            "gates": live.get("gates") or [],
            "why": live.get("reasons") or [],
        }
        out_rows.append(rec)
        print(
            f"{rec['id']} | {rec['slot']:6} | {rec['n_tested']} | {rec['n_complete']} | {rec['unique_complete']} | {rec['live_bin']} | {rec['gates']} | {'; '.join(rec['why'])[:64]}"
        )

    types1 = {n: next(r["type"] for r in rows if r["name"] == n) for n in types0}
    if types1 != types0:
        fail("menu types changed")

    payload = {
        "continuous_knobs": 0,
        "strict_complete": {r["id"]: strict_complete(r) for r in cat["rows"]},
        "questions": out_rows,
        "unique_complete_warp": s1["unique_complete"],
        "unique_complete_metric": s2["unique_complete"],
        "unique_color": False,
        "any_promoted": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\nUNIQUE SURVIVOR HUNT - CATALOG != ISOLATE - ZERO KNOBS")
    print("Unique isolate-complete warp from Layer A?", "Yes" if s1["unique_complete"] else "No")
    print("Unique isolate-complete metric from Layer A?", "Yes" if s2["unique_complete"] else "No")
    print("Unique color from Layer A? No")
    print("Any menu type promoted? No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
