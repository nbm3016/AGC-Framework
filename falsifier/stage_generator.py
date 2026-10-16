#!/usr/bin/env python3
"""Type Layer-A modulus menu and stress-check claims. No stored types."""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from typing import Any, Dict

from check_engine import LEGAL, LEGAL_MODULUS_TYPES, runCheck
from layer_a_generator import type_menu

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
PORTS_PATH = os.path.join(ARTIFACT_DIR, "computed_ports.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def recompute_p3_p4(n_eta, lam, c2: Fraction) -> Dict[str, str]:
    t_n = sum(Fraction(int(x), 1) for x in n_eta) / 4
    lam_f = [Fraction(9, 2), Fraction(12, 1), Fraction(45, 2)]
    if [float(x) for x in lam] != [4.5, 12.0, 22.5]:
        lam_f = [Fraction(x).limit_denominator(20) for x in lam]
    t_l = sum(lam_f) / 6
    sig2 = Fraction(3, 4)
    geff = sig2 / c2
    print("IDENTITIES")
    print(f"  T_wall_from_n   = {t_n}")
    print(f"  T_wall_from_lam = {t_l}")
    print(f"  sigma_star_sq   = {sig2}")
    print(f"  eight_pi_G_eff  = {geff}")
    return {
        "T_wall_from_n": str(t_n),
        "T_wall_from_lam": str(t_l),
        "sigma_star_sq": str(sig2),
        "eight_pi_G_eff": str(geff),
    }


def stress_claims() -> list:
    return [
        {
            "id": "S1",
            "text": "free fit alpha is an allowed Layer-A modulus",
            "uses_modulus": "free_fit_alpha",
        },
        {
            "id": "S2",
            "text": "warp factor is FORCED by Layer A",
            "uses_modulus": "warp_factor",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "S3",
            "text": "g_mu_nu is FORCED by identifying it with sigma*",
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
            "yes_as_lock": {"sigma_is_gmunu": True},
        },
        {
            "id": "S4",
            "text": "8 pi G_eff = 9/16 is G_N",
            "uses_modulus": "eight_pi_G_eff_as_G_N",
            "labels_modulus_as": "G_N",
        },
        {
            "id": "S5",
            "text": "unique color is a FORCED modulus",
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True},
        },
        {
            "id": "S6",
            "text": "Weyl lambda is an adjuster for R in meters",
            "uses_modulus": "Weyl_lambda",
            "labels_modulus_as": "FORCED",
            "yes_as_lock": {"lambda_is_R_meters": True, "stick_as_R": True},
        },
        {
            "id": "S7",
            "text": "T_wall identity is a computed identity of locked n_eta / tilde_lambda",
            "kind": "port_twall",
        },
        {
            "id": "S8",
            "text": "Iso group of the locked 5-fold is the isometry (not color)",
            "kind": "port_iso",
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
    b = load_json(BASELINE_PATH)
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    n_eta = proven["n_eta_delta_eta"]["n_eta"]
    sigma = proven.get("sigma_star_shape_stabilized", {}).get("value") or (
        b.get("final_locked_state") or {}
    ).get("official_sigma_star")
    lam = proven["lambda_tilde_derived"]["value"]
    if knobs != 0:
        fail("knobs != 0")
    if n_gen != 3:
        fail("N_gen != 3")
    if not n_eta or sigma is None:
        fail("n_eta or sigma_star missing")
    c2_s = (b.get("anomaly_beyond_index") or {}).get("descent_audit", {}).get("C2_SU3")
    if c2_s not in {"4/3", "4 / 3"}:
        fail("C2(3) not a locked symbol")
    c2 = Fraction(4, 3)

    ports_file = load_json(PORTS_PATH) if os.path.isfile(PORTS_PATH) else {}
    numeric = recompute_p3_p4(n_eta, lam, c2)
    if ports_file.get("numeric"):
        numeric = {**ports_file["numeric"], **numeric}

    locked = {
        "knobs": knobs,
        "N_gen": n_gen,
        "sigma_star_locked": True,
        "unique_4fold": False,
        "warp_forced": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "isolate_written": False,
        "t_wall_n": numeric.get("T_wall_from_n"),
        "t_wall_lam": numeric.get("T_wall_from_lam"),
    }

    menu = type_menu(locked, numeric)
    names = [r["name"] for r in menu]
    if "free_fit_alpha" in names:
        fail("free_fit_alpha must not be on the menu")
    for r in menu:
        if r["type"] not in LEGAL_MODULUS_TYPES:
            fail(f"illegal type {r['type']} on {r['name']}")
        if r["name"] == "free_fit_alpha" and r["type"] in {"OPEN-FIELD", "FORCED"}:
            fail("alpha listed as allowed")
        if r["type"] != "FORCED" and r["value_forced"]:
            fail(f"value_forced on non-FORCED {r['name']}")

    with open(MENU_PATH, "w", encoding="utf-8") as f:
        json.dump({"continuous_knobs": 0, "isolate_written": False, "rows": menu}, f, indent=2)
        f.write("\n")

    locked["modulus_menu"] = menu

    print("name | type | value_forced | physics_reading")
    for r in menu:
        print(f"{r['name']} | {r['type']} | {r['value_forced']} | {r['physics_reading']}")

    print("id | claim | live_bin | gates")
    for s in stress_claims():
        live = runCheck(s, locked)
        if live["bin"] not in LEGAL:
            fail(f"{s['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{s['id']} refuse-gate did not produce REFUSED")
        print(f"{s['id']} | {s['text'][:56]} | {live['bin']} | {live['gates']}")
        s["live"] = live

    with open(os.path.join(ARTIFACT_DIR, "_generator_live.json"), "w", encoding="utf-8") as f:
        json.dump({"menu": menu, "stress": [{k: v for k, v in s.items() if k != "yes_as_lock"} for s in stress_claims()]}, f, indent=2)

    # rewrite stress with live
    live_stress = []
    for s in stress_claims():
        live = runCheck(s, locked)
        live_stress.append({"id": s["id"], "text": s["text"], **live})
    with open(os.path.join(ARTIFACT_DIR, "_generator_live.json"), "w", encoding="utf-8") as f:
        json.dump({"menu": menu, "stress": live_stress, "numeric": numeric}, f, indent=2)

    print("LAYER-A GENERATOR TYPED AND CHECKED - ELIGIBLE != DETERMINED - ZERO KNOBS")
    if knobs != 0:
        fail("knobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
