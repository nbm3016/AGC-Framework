#!/usr/bin/env python3
"""
14D uniqueness probe: sector != landscape.
Score only bases on disk. Do not weld G_SE onto all 14D.
Do not pick a non-SE base because uniqueness failed outside G_SE.
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
CU_PATH = os.path.join(ARTIFACT_DIR, "controlled_uniqueness.json")
GU_PATH = os.path.join(ARTIFACT_DIR, "global_uniqueness_probe.json")
LABC_PATH = os.path.join(ARTIFACT_DIR, "se_aps_L_abc.json")
ATTEMPTS_PATH = os.path.join(ARTIFACT_DIR, "uniqueness_14d_attempts.json")


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
    cu = load_json(CU_PATH)
    gu = load_json(GU_PATH) if os.path.isfile(GU_PATH) else {}
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0:
        fail("knobs != 0")
    if n_gen != 3:
        fail("N_gen != 3")

    ca = cu.get("class_analysis") or {}
    cdef = cu.get("class_definition") or {}
    isolates = bool(ca.get("skeleton_isolates_T11"))
    n_bases = int(ca.get("n_bases") or 0)
    not_included = list(cdef.get("not_included") or [])
    lambda_hits = list(ca.get("locked_lambda_hits") or [])
    global_u = bool(gu.get("global_vacuum_uniqueness_achieved"))
    proof_boundary = gu.get("proof_boundary") or cu.get("theorem_level_claim") or ""

    later_scored = False
    labc_on_disk = os.path.isfile(LABC_PATH)
    labc_first_slice = False
    if labc_on_disk:
        labc = load_json(LABC_PATH)
        banner = str(labc.get("banner") or "")
        labc_first_slice = "first-slice" in banner.lower() or "first slice" in banner.lower()
        # L^{a,b,c} catalog is first-slice parallel, not later-slice uniqueness score
        later_scored = False

    outside = []
    for d in cu.get("deformations") or cu.get("open_directions") or []:
        if isinstance(d, dict) and d.get("status") == "outside_class_open":
            outside.append(d.get("deformation") or d.get("mechanism"))

    print("READ")
    print(f"  G_SE n_bases={n_bases} skeleton_isolates_T11={isolates}")
    print(f"  locked_lambda_hits={lambda_hits}")
    print(f"  not_included={not_included}")
    print(f"  global_vacuum_uniqueness_achieved={global_u}")
    print(f"  L_abc on disk={labc_on_disk} first_slice_banner={labc_first_slice}")
    print(f"  later_slice_scored={later_scored}")
    print(f"  outside_class_open={outside[:3]}")

    rows = menu_doc.get("rows") or []
    warp_t = next((r["type"] for r in rows if r["name"] == "warp_factor"), None)
    g_t = next((r["type"] for r in rows if r["name"] == "g_mu_nu"), None)
    uc_t = next((r["type"] for r in rows if r["name"] == "unique_color"), None)

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
        "isolates_T11": isolates,
        "global_14d": global_u,
        "later_scored": later_scored,
    }

    def bin_u1():
        if isolates and lambda_hits == ["T^{1,1}"]:
            return {
                "bin": "CLASS",
                "gates": [],
                "reasons": [
                    f"skeleton_isolates_T11=true inside G_SE ({n_bases} bases); sector theorem, not all 14D"
                ],
            }
        if isolates:
            return {
                "bin": "CLASS",
                "gates": [],
                "reasons": ["skeleton_isolates_T11 true; class G_SE not landscape"],
            }
        return {"bin": "UNKNOWN", "gates": [], "reasons": ["isolation flag not on disk"]}

    def bin_u5():
        if later_scored:
            return {
                "bin": "FORCED",
                "gates": [],
                "reasons": ["later-slice bases present and scored"],
            }
        if labc_on_disk and labc_first_slice:
            return {
                "bin": "UNKNOWN",
                "gates": [],
                "reasons": [
                    "L^{a,b,c} catalog is on disk as first-slice parallel, not a later-slice uniqueness score; later-slice / other 14D untested"
                ],
            }
        return {
            "bin": "UNKNOWN",
            "gates": [],
            "reasons": ["later-slice / non-SE bases not scored on disk"],
        }

    u_claims = [
        {"id": "U1", "text": "T^{1,1} isolated inside first-slice G_SE by locked lambda-tilde / sigma*"},
        {
            "id": "U2",
            "text": "that theorem covers bases outside the first slice",
            "yes_as_lock": {"weld_class_to_lock": True, "map_called_lock": True},
        },
        {
            "id": "U3",
            "text": "unique 14D fibration forced landscape-wide (all fibrations)",
            "yes_as_lock": {"weld_class_to_lock": True, "map_called_lock": True},
        },
        {
            "id": "U4",
            "text": "non-SE / later-slice base forced as THE vacuum because uniqueness failed outside G_SE",
            "yes_as_lock": {"weld_class_to_lock": True},
            "uses_modulus": "K3_as_the_4fold",
            "labels_modulus_as": "the 4-fold",
        },
        {"id": "U5", "text": "later-slice / non-SE bases actually present and scored on disk"},
    ]

    u_live = []
    print("\nid | question | unique? | live_bin | gates | why")
    for c in u_claims:
        if c["id"] == "U1":
            live = bin_u1()
        elif c["id"] == "U5":
            live = bin_u5()
        else:
            live = runCheck(c, facts)
        if live["bin"] not in LEGAL:
            fail(f"{c['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{c['id']} refuse-gate did not produce REFUSED")
        unique = live["bin"] == "FORCED"
        u_live.append({"id": c["id"], "text": c["text"], "unique": unique, **live})
        print(
            f"{c['id']} | {c['text'][:44]} | {unique} | {live['bin']} | {live.get('gates', [])} | {'; '.join(live['reasons'])[:72]}"
        )

    u3 = next(x for x in u_live if x["id"] == "U3")
    promote = u3["bin"] == "FORCED" and knobs == 0
    if promote:
        fail("would promote landscape-wide 14D — unexpected")
    if next(r["type"] for r in rows if r["name"] == "warp_factor") != warp_t:
        fail("warp type changed")
    if next(r["type"] for r in rows if r["name"] == "g_mu_nu") != g_t:
        fail("g_mu_nu type changed")
    if next(r["type"] for r in rows if r["name"] == "unique_color") != uc_t:
        fail("unique_color type changed")

    payload = {
        "module": "uniqueness_14d_probe",
        "continuous_knobs": 0,
        "N_gen": 3,
        "G_SE_n_bases": n_bases,
        "skeleton_isolates_T11": isolates,
        "global_vacuum_uniqueness_achieved": global_u,
        "later_slice_scored": later_scored,
        "labc_on_disk_first_slice_only": labc_on_disk and labc_first_slice,
        "promote_landscape": False,
        "U": u_live,
        "proof_boundary": proof_boundary[:400],
        "isolate_written": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(ATTEMPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\n14D UNIQUENESS PROBE - SECTOR != LANDSCAPE - ZERO KNOBS")
    print("Is landscape-wide 14D uniqueness FORCED?", "Yes" if promote else "No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
