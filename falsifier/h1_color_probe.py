#!/usr/bin/env python3
"""
H1 unique-color value probe. Iso is FORCED as a group. Unique color is FORBIDDEN.
Eligible family != determined member. Do not pre-assign Yes.
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
PIPES_PATH = os.path.join(ARTIFACT_DIR, "h1_pipes.json")
ATTEMPTS_PATH = os.path.join(ARTIFACT_DIR, "h1_color_attempts.json")


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
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0:
        fail("knobs != 0")
    if n_gen != 3:
        fail("N_gen != 3")

    menu_rows = menu_doc.get("rows") or []
    uc = next((r for r in menu_rows if r.get("name") == "unique_color"), None)
    iso_row = next((r for r in menu_rows if r.get("name") == "Iso_group"), None)
    gsm = next((r for r in menu_rows if r.get("name") == "G_SM_from_isolate"), None)
    warp = next((r for r in menu_rows if r.get("name") == "warp_factor"), None)
    gmn = next((r for r in menu_rows if r.get("name") == "g_mu_nu"), None)
    if uc is None:
        fail("unique color missing from menu")
    warp_type = warp.get("type") if warp else None
    gmn_type = gmn.get("type") if gmn else None
    iso_type_before = iso_row.get("type") if iso_row else None

    # Attempt A group theory
    dim_su2 = 3
    dim_u1 = 1
    dim_iso = dim_su2 + dim_su2 + dim_u1  # 7
    dim_su3 = 8
    contains = dim_iso >= dim_su3  # necessary condition; 7<8 => False
    print("ATTEMPT A — Group theory")
    print(f"  Iso = SU(2)×SU(2)×U(1)")
    print(f"  dim(SU(2))=3, dim(U(1))=1 ⇒ dim(Iso)={dim_iso}")
    print(f"  dim(SU(3))={dim_su3}")
    print(f"  Lie-subgroup necessary condition dim(H)≤dim(G): {dim_su3}≤{dim_iso}? {contains}")
    print("  Iso cannot contain SU(3) as a Lie subgroup (dimension obstruction).")
    aA = {
        "id": "A",
        "dim_iso": dim_iso,
        "dim_su3": dim_su3,
        "contains_SU3": False,
        "leftover_picks": [],
        "new_names_not_on_menu": [],
        "gates": [],
        "live_bin": "REFUSED",
        "why": "dim(Iso)=7 < dim(SU(3))=8; no derived SU(3)_c subgroup",
    }

    print("\nATTEMPT B — N_gen=3 as three colors?")
    print("  N_gen=3 is Module A generation count, not three colors.")
    aB = {
        "id": "B",
        "leftover_picks": ["identify generations with colors"],
        "new_names_not_on_menu": [],
        "gates": ["R-color-lock"],
        "live_bin": "REFUSED",
        "why": "N_gen=3 does not force three colors",
    }

    print("\nATTEMPT C — C2(3)=4/3 in 8πG_eff as SU(3)_c?")
    print("  Locked identity is σ*²/C2 as a number 9/16. C2(3) is a Casimir symbol,")
    print("  burned as a color proof. Does not force SU(3)_c.")
    aC = {
        "id": "C",
        "leftover_picks": ["read C2(3) as QCD"],
        "new_names_not_on_menu": [],
        "gates": ["R-color-lock", "R-burn-list"],
        "live_bin": "REFUSED",
        "why": "C2(3) in G_eff identity is not a color lock",
    }

    print("\nATTEMPT D — b2=b3=1 as color/hypercharge flux?")
    print("  P1: topology, not flux. b2=1 does not force color or hypercharge flux.")
    aD = {
        "id": "D",
        "leftover_picks": ["read Betti as flux"],
        "new_names_not_on_menu": [],
        "gates": ["R-map-called-lock"],
        "live_bin": "REFUSED",
        "why": "b2=b3=1 is topology; flux reading FORBIDDEN",
    }

    print("\nATTEMPT E — leftover X^4 or CP²/K3 unique color?")
    print("  leftover X^4 is CLASS. CP²/K3 as THE 4-fold is FORBIDDEN.")
    aE = {
        "id": "E",
        "leftover_picks": ["CP2", "K3"],
        "new_names_not_on_menu": [],
        "gates": ["R-weld"],
        "live_bin": "REFUSED",
        "why": "CLASS family; named pick not unique color",
    }

    print("\nATTEMPT F — Iso joined to something = G_SM?")
    print("  Weld not a locked identity. Extra U(1)_X / GUT integers / Wilson coupling unlisted.")
    aF = {
        "id": "F",
        "leftover_picks": ["GUT embedding", "U(1)_X"],
        "new_names_not_on_menu": ["U1_X", "GUT_integers", "Wilson_color"],
        "gates": ["R-weld", "R-unlisted-modulus"],
        "live_bin": "REFUSED",
        "why": "G_SM weld not locked; extra factors are knobs/picks",
    }

    print("\nATTEMPT G — Z/24 circulant / Fourier as color or G_SM?")
    print("  Graph lock kept; Aut 2-planes are not SM generations (weld retirement FAIL).")
    aG = {
        "id": "G",
        "leftover_picks": ["Fourier = color"],
        "new_names_not_on_menu": [],
        "gates": ["R-weld"],
        "live_bin": "REFUSED",
        "why": "MAP != LOCK; graph eigenspaces not color/G_SM",
    }

    print("\nATTEMPT H — CLASS color pipes: unique member?")
    print("  On disk: Track A Chern family; leftover X^4 CLASS. Family remains.")
    print("  No pipe picks a unique member. CLASS stays CLASS.")
    aH = {
        "id": "H",
        "pipes_on_disk": ["Track A external SU(3) Chern family", "leftover X^4 family"],
        "unique_member": False,
        "leftover_picks": ["which Chern (c2,rank,k)", "which 4-fold"],
        "new_names_not_on_menu": [],
        "gates": [],
        "live_bin": "CLASS",
        "why": "CLASS pipes remain a family; unique member not forced",
    }

    attempts = [aA, aB, aC, aD, aE, aF, aG, aH]

    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": menu_rows,
        "dim_iso": dim_iso,
        "dim_su3": dim_su3,
        "iso_contains_su3": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "sigma_star_locked": True,
        "unique_4fold": False,
        "warp_forced": False,
        "isolate_written": False,
        "t_wall_n": "13/2",
        "t_wall_lam": "13/2",
    }

    c_claims = [
        {
            "id": "C1",
            "text": "unique SU(3)_c already in the atoms as a derived group",
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True},
        },
        {
            "id": "C2",
            "text": "Iso contains SU(3) as a Lie subgroup or forces SU(3)_c",
            "kind": "iso_contains_su3",
        },
        {
            "id": "C3",
            "text": "N_gen=3 forces three colors",
            "yes_as_lock": {"n_gen_as_colors": True},
        },
        {
            "id": "C4",
            "text": "C2(3)=4/3 in 8πG_eff forces SU(3)_c",
            "yes_as_lock": {"c2_as_color": True, "burned": True},
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "C5",
            "text": "b2=1 and b3=1 force color or hypercharge flux",
            "uses_modulus": "b2_b3_as_flux",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "C6",
            "text": "unique color embedding from locked atoms only",
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True},
        },
        {
            "id": "C7",
            "text": "CP^2 or K3 is THE color space / THE 4-fold",
            "yes_as_lock": {"weld_class_to_lock": True},
            "uses_modulus": "CP2_as_the_4fold",
            "labels_modulus_as": "the 4-fold",
        },
        {
            "id": "C8",
            "text": "G_SM / GUT weld forced from the isolate",
            "yes_as_lock": {"weld_class_to_lock": True},
            "uses_modulus": "G_SM_from_isolate",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "C9",
            "text": "Z/24 circulant / Fourier eigenspaces force color or G_SM",
            "yes_as_lock": {"weld_class_to_lock": True, "burned": True},
        },
        {
            "id": "C10",
            "text": "CLASS color pipes force a unique member",
            "kind": "class_pipes",
        },
        {
            "id": "C11",
            "text": "alpha_s / a color coupling forced",
            "yes_as_lock": {"free_real": True, "new_real": True},
            "uses_modulus": "alpha_s",
        },
    ]

    c_live = []
    print("\nid | question | unique? | live_bin | gates | why")
    for c in c_claims:
        live = runCheck(c, facts)
        if live["bin"] not in LEGAL:
            fail(f"{c['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{c['id']} refuse-gate did not produce REFUSED")
        unique = live["bin"] == "FORCED"
        c_live.append({"id": c["id"], "text": c["text"], "unique": unique, **live})
        print(
            f"{c['id']} | {c['text'][:42]} | {unique} | {live['bin']} | {live['gates']} | {'; '.join(live['reasons'])[:70]}"
        )

    c6 = next(x for x in c_live if x["id"] == "C6")
    promote = c6["bin"] == "FORCED" and knobs == 0
    uc_type = "FORCED" if promote else uc["type"]
    if promote:
        uc["type"] = "FORCED"
        uc["value_forced"] = True
        with open(MENU_PATH, "w", encoding="utf-8") as f:
            json.dump(menu_doc, f, indent=2)
            f.write("\n")
    else:
        if uc.get("type") != "FORBIDDEN":
            fail("unique color changed without promotion rule")
        if iso_row and iso_row.get("type") != iso_type_before:
            fail("Iso type must stay FORCED as group")
        if warp and warp.get("type") != warp_type:
            fail("warp type must not change")
        if gmn and gmn.get("type") != gmn_type:
            fail("g_mu_nu type must not change")

    # update h1_pipes live bins without closing pipes
    pipes = load_json(PIPES_PATH) if os.path.isfile(PIPES_PATH) else {}
    pipes["H1_color_value_probe"] = {
        "C6": c6["bin"],
        "unique_color_forced": promote,
        "pipes_remain_open": True,
        "C10": next(x for x in c_live if x["id"] == "C10")["bin"],
    }
    with open(PIPES_PATH, "w", encoding="utf-8") as f:
        json.dump(pipes, f, indent=2)
        f.write("\n")

    payload = {
        "module": "h1_color_probe",
        "continuous_knobs": 0,
        "N_gen": 3,
        "dim_iso": dim_iso,
        "dim_su3": dim_su3,
        "iso_contains_SU3": False,
        "promote": promote,
        "unique_color_type_after": uc_type,
        "iso_type": iso_row.get("type") if iso_row else None,
        "G_SM_type": gsm.get("type") if gsm else None,
        "attempts": attempts,
        "C": c_live,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "isolate_written": False,
    }
    with open(ATTEMPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\nH1 COLOR VALUE PROBE - ELIGIBLE FAMILY != DETERMINED MEMBER - ZERO KNOBS")
    print("Is unique color FORCED?", "Yes" if promote else "No")
    print(f"Iso          | {iso_row.get('type')} | {iso_row.get('value_forced')} | group not color")
    print(f"unique color | {uc_type} | {bool(promote)} | not derived")
    print(f"G_SM         | {gsm.get('type') if gsm else None} | {gsm.get('value_forced') if gsm else None} | not forced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
