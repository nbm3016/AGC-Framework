#!/usr/bin/env python3
"""
E4 4D-metric value probe. g_mu_nu is OPEN-FIELD; this asks if Layer A forces the value.
Do not pre-assign Yes. Do not promote unless M5 and M6 are both FORCED.
Do not change warp menu type. Do not start H1.
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
ATTEMPTS_PATH = os.path.join(ARTIFACT_DIR, "e4_metric_attempts.json")


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
    g_row = next((r for r in menu_rows if r.get("name") == "g_mu_nu"), None)
    warp_row = next((r for r in menu_rows if r.get("name") == "warp_factor"), None)
    if g_row is None:
        fail("g_mu_nu not on the menu")
    warp_type_before = warp_row.get("type") if warp_row else None

    num = ports.get("numeric") or {}
    t_n = Fraction(num.get("T_wall_from_n", "13/2"))
    sig2 = Fraction(num.get("sigma_star_sq", "3/4"))
    geff = Fraction(num.get("eight_pi_G_eff", "9/16"))
    print("FRACTIONS")
    print(f"  T_wall = {t_n}")
    print(f"  σ*² = {sig2}")
    print(f"  8πG_eff number = {geff}")

    st4 = proven.get("stage4_mu_omega_w0") or {}
    print(f"  Stage-4 scalars μ_γγ={st4.get('mu_gammagamma')} Ω_Λ={st4.get('omega_lambda')} w0={st4.get('w0')}")

    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": menu_rows,
        "sigma_star_locked": True,
        "warp_forced": False,
        "unique_4fold": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "t_wall_n": str(t_n),
        "t_wall_lam": str(t_n),
        "isolate_written": False,
    }

    attempts: List[Dict[str, Any]] = []

    print("\nATTEMPT A — Direct scalars → g_μν(x)")
    print("  Locked scalars do not include t,x,y,z or a 4D mesh (DIMENSIONAL_SCOPE / M4_BRIDGE).")
    print("  Cannot write g_μν(x) as a field without introducing spacetime arguments.")
    aA = {
        "id": "A",
        "equation": None,
        "leftover_constants": ["t,x,y,z", "line element"],
        "new_names_not_on_menu": ["t", "x", "y", "z", "4D_mesh"],
        "gates": ["R-unlisted-modulus", "R-knobs"],
        "live_bin": "REFUSED",
        "why": "no M^4 coordinates in isolate atoms",
    }
    attempts.append(aA)
    print("  leftover", aA["leftover_constants"], "bin", aA["live_bin"])

    print("\nATTEMPT B — Compact objects vs g_μν")
    print("  σ* is T^{1,1} squashing (constant). φ(θ,ψ) is compact conformal factor on ḡ_ij.")
    print("  Neither is a live metric on M^4.")
    aB = {
        "id": "B",
        "equation": "g_ij = e^{2φ(θ,ψ)} ḡ_ij  (compact 5-metric, not g_μν(x))",
        "depends_on": ["theta", "psi", "sigma_star"],
        "leftover_constants": [],
        "new_names_not_on_menu": [],
        "gates": ["R-metric-swap"],
        "live_bin": "REFUSED",
        "why": "σ* and φ(θ,ψ) are not g_μν(x)",
    }
    attempts.append(aB)
    print("  depends_on", aB["depends_on"], "bin", aB["live_bin"])

    print("\nATTEMPT C — If 9/16 were G_N and an EH term existed (then gates)")
    print("  Hypothetical: G_μν = (9/16) T_μν or R_μν - ½g_μν R = 8π G_N T_μν.")
    print("  Would need G_N, an EH integrand, and 4D coordinates. Reading not locked.")
    aC = {
        "id": "C",
        "equation": "G_μν =? (9/16) T_μν  (NOT accepted: 9/16 is not G_N)",
        "leftover_constants": ["G_N", "EH integrand", "T_μν", "4D coords"],
        "new_names_not_on_menu": ["Einstein_Hilbert", "Lambda_4", "G_N"],
        "gates": ["R-modulus-called-lock", "R-unlisted-modulus", "R-knobs"],
        "live_bin": "REFUSED",
        "why": "9/16 is a compact ratio; EH term not coded; equation not accepted",
    }
    attempts.append(aC)
    print("  leftover", aC["leftover_constants"], "bin", aC["live_bin"])

    print("\nATTEMPT D — Stage-4 scalars → unique FRW line element?")
    print("  Ω_Λ, w0, μ_γγ are dimensionless isolate maps, not a 4D ds².")
    print("  FRW would need a(t), k, coordinates. Not forced.")
    aD = {
        "id": "D",
        "equation": None,
        "leftover_constants": ["a(t)", "k_curvature", "t"],
        "new_names_not_on_menu": ["FRW_scale_factor", "t"],
        "gates": ["R-unlisted-modulus", "R-knobs"],
        "live_bin": "REFUSED",
        "why": "Stage-4 scalars do not force a unique 4D line element",
    }
    attempts.append(aD)
    print("  leftover", aD["leftover_constants"], "bin", aD["live_bin"])

    print("\nATTEMPT E — Vacuum pick because E3 returned No?")
    print("  E3: warp OPEN-FIELD, A(y) not forced. That does not force η_μν.")
    print("  Minkowski/FLRW/RS/Schwarzschild as THE metric is a pick.")
    aE = {
        "id": "E",
        "equation": None,
        "leftover_constants": ["choice of vacuum metric"],
        "new_names_not_on_menu": ["eta_mu_nu"],
        "gates": ["R-weld"],
        "live_bin": "REFUSED",
        "why": "failed warp uniqueness does not force Minkowski; pick forbidden",
    }
    attempts.append(aE)
    print("  bin", aE["live_bin"])

    print("\nATTEMPT F — Yardstick as g_μν?")
    print("  Observational conversion is GAUGE; stick is withdrawn. Not a metric atom.")
    aF = {
        "id": "F",
        "equation": None,
        "leftover_constants": [],
        "new_names_not_on_menu": [],
        "gates": ["R-stick-left-in", "R-scale"],
        "live_bin": "REFUSED",
        "why": "yardstick is GAUGE conversion, not g_μν",
    }
    attempts.append(aF)
    print("  bin", aF["live_bin"])

    m_claims = [
        {
            "id": "M1",
            "text": "g_mu_nu(x) is already a coded live field on M^4",
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "M2",
            "text": "sigma* or compact phi identifies with g_mu_nu",
            "yes_as_lock": {"sigma_is_gmunu": True, "phi_is_gmunu": True},
        },
        {
            "id": "M3",
            "text": "9/16 forces G_N as an Einstein-Hilbert coefficient",
            "yes_as_lock": {"geff_as_GN": True},
            "uses_modulus": "eight_pi_G_eff_as_G_N",
            "labels_modulus_as": "G_N",
        },
        {
            "id": "M4",
            "text": "Stage-4 scalars force a unique 4D line element",
            "yes_as_lock": {"new_real": True, "free_real": True},
            "uses_modulus": "FRW_line_element",
        },
        {
            "id": "M5",
            "text": "unique zero-knob 4D Einstein equation from locked atoms only",
            "yes_as_lock": {"new_real": True, "geff_as_GN": True, "free_real": True},
            "uses_modulus": "Einstein_Hilbert",
        },
        {
            "id": "M6",
            "text": "unique g_mu_nu(x) forced modulo diffeomorphism and Weyl",
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "M7",
            "text": "eta_mu_nu / FLRW / RS / Schwarzschild is THE metric",
            "yes_as_lock": {"weld_class_to_lock": True},
            "uses_modulus": "eta_mu_nu",
        },
        {
            "id": "M8",
            "text": "observational conversion / yardstick is g_mu_nu",
            "yes_as_lock": {"stick_left_in": True, "stick_as_R": True},
            "uses_modulus": "overall_R",
            "labels_modulus_as": "FORCED",
        },
    ]

    m_live = []
    print("\nid | question | unique? | live_bin | gates | why")
    for m in m_claims:
        live = runCheck(m, facts)
        if live["bin"] not in LEGAL:
            fail(f"{m['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{m['id']} refuse-gate did not produce REFUSED")
        unique = live["bin"] == "FORCED"
        m_live.append({"id": m["id"], "text": m["text"], "unique": unique, **live})
        print(
            f"{m['id']} | {m['text'][:44]} | {unique} | {live['bin']} | {live['gates']} | {'; '.join(live['reasons'])[:72]}"
        )

    m5 = next(x for x in m_live if x["id"] == "M5")
    m6 = next(x for x in m_live if x["id"] == "M6")
    promote = m5["bin"] == "FORCED" and m6["bin"] == "FORCED" and knobs == 0
    g_type = "FORCED" if promote else g_row["type"]
    value_forced = bool(promote)
    if promote:
        g_row["type"] = "FORCED"
        g_row["value_forced"] = True
        with open(MENU_PATH, "w", encoding="utf-8") as f:
            json.dump(menu_doc, f, indent=2)
            f.write("\n")
    else:
        if g_row.get("type") != "OPEN-FIELD" or g_row.get("value_forced"):
            fail("g_mu_nu type changed without promotion rule")
        if warp_row and warp_row.get("type") != warp_type_before:
            fail("warp menu type must not change")

    payload = {
        "module": "e4_metric_probe",
        "continuous_knobs": 0,
        "N_gen": 3,
        "isolate_written": False,
        "promote": promote,
        "g_mu_nu_type_after": g_type,
        "value_forced": value_forced,
        "warp_type_unchanged": warp_type_before,
        "attempts": attempts,
        "M": m_live,
        "fractions": {"T_wall": str(t_n), "sigma_star_sq": str(sig2), "eight_pi_G_eff": str(geff)},
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(ATTEMPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\nE4 METRIC VALUE PROBE - ELIGIBLE != DETERMINED - ZERO KNOBS")
    print("Is g_mu_nu value FORCED?", "Yes" if promote else "No")
    print(f"g_mu_nu | {g_type} | {value_forced}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
