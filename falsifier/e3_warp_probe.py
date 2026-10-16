#!/usr/bin/env python3
"""
E3 warp-value probe. Warp is OPEN-FIELD; this asks if Layer A forces the value.
Do not pre-assign Yes. Do not promote unless W4 and W5 are both FORCED.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List

from check_engine import LEGAL, runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
PORTS_PATH = os.path.join(ARTIFACT_DIR, "computed_ports.json")
ATTEMPTS_PATH = os.path.join(ARTIFACT_DIR, "e3_warp_attempts.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "E3_WARP_REPORT.md")


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

    menu_rows = menu_doc.get("rows") or []
    warp_row = next((r for r in menu_rows if r.get("name") == "warp_factor"), None)
    g_row = next((r for r in menu_rows if r.get("name") == "g_mu_nu"), None)
    if warp_row is None:
        fail("warp not on the menu")
    if warp_row.get("type") not in {"FORCED", "GAUGE", "CLASS", "OPEN-FIELD", "FORBIDDEN"}:
        fail("warp type illegal")

    num = ports.get("numeric") or {}
    t_n = Fraction(num.get("T_wall_from_n", "13/2"))
    t_l = Fraction(num.get("T_wall_from_lam", "13/2"))
    sig2 = Fraction(num.get("sigma_star_sq", "3/4"))
    geff = Fraction(num.get("eight_pi_G_eff", "9/16"))
    print("FRACTIONS")
    print(f"  T_wall = {t_n} (n) = {t_l} (λ̃)")
    print(f"  σ*² = {sig2}")
    print(f"  8πG_eff number = {geff}")

    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": menu_rows,
        "sigma_star_locked": True,
        "warp_forced": False,
        "unique_4fold": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "t_wall_n": str(t_n),
        "t_wall_lam": str(t_l),
        "isolate_written": False,
    }

    # --- derivation attempts (print + record) ---
    attempts: List[Dict[str, Any]] = []

    print("\nATTEMPT A — Direct scalars → A(y)")
    print("  Locked scalars: σ*, T_wall=13/2, 8πG_eff=9/16 (number).")
    print("  No extra-dimension coordinate y is discretized in isolate files.")
    print("  Cannot write A as a function of y without introducing y and a length.")
    aA = {
        "id": "A",
        "title": "Direct: locked scalars determine A(y) with no extra structure",
        "equation": None,
        "leftover_constants": ["y-interval", "A(y) functional form"],
        "new_names_not_on_menu": ["y", "A(y)"],
        "gates": ["R-unlisted-modulus", "R-knobs"],
        "live_bin": "REFUSED",
        "why": "No y in isolate atoms; A(y) not determined by scalars alone",
    }
    attempts.append(aA)
    print("  leftover:", aA["leftover_constants"], "bin", aA["live_bin"])

    print("\nATTEMPT B — Compact conformal factor φ(θ,ψ) vs A(y)")
    print("  stage2b_beta_variational.py (2B.5): g_ij = e^{2φ(θ,ψ)} ḡ_ij,")
    print("  ḡ = diag(σ*²,σ*²,1,1,1). φ depends on T^{1,1} angles, not y.")
    print("  That object is the compact conformal factor, not a 4D warp A(y).")
    aB = {
        "id": "B",
        "title": "Is φ(θ,ψ) the same object as A(y)?",
        "equation": "g_ij = e^{2φ(θ,ψ)} ḡ_ij  (coded; compact 5-metric)",
        "phi_depends_on": ["theta", "psi"],
        "forces_A_of_y": False,
        "leftover_constants": [],
        "new_names_not_on_menu": [],
        "gates": [],
        "live_bin": "REFUSED",
        "why": "φ(θ,ψ) is not A(y); y is not an isolate coordinate",
    }
    attempts.append(aB)
    print("  φ depends on", aB["phi_depends_on"], "bin", aB["live_bin"])

    print("\nATTEMPT C — If T_wall were an Israel jump (then apply gates)")
    print("  Hypothetical: [A'] = - (const) * T_wall * 8πG")
    print("  Would need G_N, a y-normal, and T_wall as GeV^3 tension.")
    print("  T_wall=13/2 is a discrete spectral identity, not a brane tension.")
    aC = {
        "id": "C",
        "title": "Tension reading: T_wall as Israel jump for [A']",
        "equation": "[A'] =? -κ T_wall  (NOT accepted: tension reading not locked)",
        "leftover_constants": ["κ or G_N", "normal y", "brane location"],
        "new_names_not_on_menu": ["Israel_jump", "kappa"],
        "gates": ["R-scale", "R-knobs", "R-unlisted-modulus"],
        "live_bin": "REFUSED",
        "why": "T_wall as 4D/5D brane tension is FORBIDDEN; equation not accepted",
    }
    attempts.append(aC)
    print("  leftover:", aC["leftover_constants"], "bin", aC["live_bin"])

    print("\nATTEMPT D — If σ* were A or A' (then apply gates)")
    print("  Hypothetical: A = σ* or A' = σ*. σ* is a locked constant (√3/2).")
    print("  A constant A is not a warp profile in y; identifying σ* with A/A' is illegal.")
    aD = {
        "id": "D",
        "title": "Shape reading: σ* = A or A'",
        "equation": "A=?σ* or A'=?σ*  (NOT accepted)",
        "leftover_constants": [],
        "new_names_not_on_menu": [],
        "gates": ["R-metric-swap"],
        "live_bin": "REFUSED",
        "why": "σ* is T^{1,1} squashing, not A(y) or A'(y)",
    }
    attempts.append(aD)
    print("  bin", aD["live_bin"])

    # W1–W5 via engine (no stored_bin)
    w_claims = [
        {
            "id": "W1",
            "text": "Layer A already contains warped-product A(y) multiplying a 4D metric",
            "yes_as_lock": {"map_called_lock": True},
            "uses_modulus": "warp_factor",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "W2",
            "text": "sigma* identifies with A(y) or A'(y)",
            "yes_as_lock": {"sigma_is_A": True},
        },
        {
            "id": "W3",
            "text": "T_wall=13/2 sources A''(y) or [A'] as brane tension",
            "yes_as_lock": {"t_wall_as_tension": True, "geff_as_GN": True},
            "uses_modulus": "T_wall_as_GeV3",
            "labels_modulus_as": "G_N",
        },
        {
            "id": "W4",
            "text": "unique zero-knob ODE for A(y) from locked atoms only",
            "yes_as_lock": {"new_real": True, "integration_C": True, "free_real": True},
            "uses_modulus": "y_interval_L",
        },
        {
            "id": "W5",
            "text": "unique profile A(y) forced modulo GAUGE/Weyl only",
            "yes_as_lock": {"modulus_called_lock": True},
            "uses_modulus": "warp_factor",
            "labels_modulus_as": "FORCED",
        },
    ]

    w_live = []
    print("\nid | question | unique? | live_bin | gates | why")
    for w in w_claims:
        live = runCheck(w, facts)
        if live["bin"] not in LEGAL:
            fail(f"{w['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{w['id']} refuse-gate did not produce REFUSED")
        unique = live["bin"] == "FORCED"
        w_live.append({"id": w["id"], "text": w["text"], "unique": unique, **live})
        print(
            f"{w['id']} | {w['text'][:40]} | {unique} | {live['bin']} | {live['gates']} | {'; '.join(live['reasons'])[:80]}"
        )

    w4 = next(x for x in w_live if x["id"] == "W4")
    w5 = next(x for x in w_live if x["id"] == "W5")
    promote = w4["bin"] == "FORCED" and w5["bin"] == "FORCED" and knobs == 0
    warp_type = "FORCED" if promote else warp_row["type"]
    value_forced = bool(promote)
    if promote:
        warp_row["type"] = "FORCED"
        warp_row["value_forced"] = True
        warp_row["notes"] = "E3 promotion: unique A(y) from locked atoms"
        with open(MENU_PATH, "w", encoding="utf-8") as f:
            json.dump(menu_doc, f, indent=2)
            f.write("\n")
    else:
        # leave OPEN-FIELD, value_forced=false
        if warp_row.get("type") != "OPEN-FIELD" or warp_row.get("value_forced"):
            fail("warp type changed without promotion rule")

    payload = {
        "module": "e3_warp_probe",
        "continuous_knobs": 0,
        "N_gen": 3,
        "isolate_written": False,
        "promote": promote,
        "warp_type_after": warp_type,
        "value_forced": value_forced,
        "attempts": attempts,
        "W": w_live,
        "fractions": {
            "T_wall": str(t_n),
            "sigma_star_sq": str(sig2),
            "eight_pi_G_eff": str(geff),
        },
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(ATTEMPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\nE3 WARP VALUE PROBE - ELIGIBLE != DETERMINED - ZERO KNOBS")
    print("Is warp value FORCED?", "Yes" if promote else "No")
    print(f"warp | {warp_type} | {value_forced}")

    if facts["isolate_written"]:
        fail("isolate written")
    if knobs != 0:
        fail("knobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
