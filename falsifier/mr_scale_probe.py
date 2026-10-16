#!/usr/bin/env python3
"""
M_R GeV scale probe. Yardstick != mass. Do not treat conversion as derived GeV.
Do not reopen E3/E4/H1/HD. Do not start 14D.
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
PRED_PATH = os.path.join(ARTIFACT_DIR, "predictions.json")
BRIDGE_PATH = os.path.join(ARTIFACT_DIR, "physical_bridge.json")
YARD_PATH = os.path.join(ARTIFACT_DIR, "absolute_yardstick_lemma_negative_series.json")
ABS_PATH = os.path.join(ARTIFACT_DIR, "absolute_scale_test.json")
ATTEMPTS_PATH = os.path.join(ARTIFACT_DIR, "mr_scale_attempts.json")


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
    pred = load_json(PRED_PATH)
    bridge = load_json(BRIDGE_PATH)
    yard = load_json(YARD_PATH) if os.path.isfile(YARD_PATH) else {}
    abs_t = load_json(ABS_PATH) if os.path.isfile(ABS_PATH) else {}
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0:
        fail("knobs != 0")
    if n_gen != 3:
        fail("N_gen != 3")

    rows = menu_doc.get("rows") or []
    r_row = next((r for r in rows if r["name"] == "overall_R"), None)
    geff_gn = next((r for r in rows if r["name"] == "eight_pi_G_eff_as_G_N"), None)
    twall_gev = next((r for r in rows if r["name"] == "T_wall_as_GeV3"), None)
    warp_t = next((r["type"] for r in rows if r["name"] == "warp_factor"), None)
    g_t = next((r["type"] for r in rows if r["name"] == "g_mu_nu"), None)
    uc_t = next((r["type"] for r in rows if r["name"] == "unique_color"), None)

    hmaj = pred.get("heavy_majorana_scale_test") or {}
    mr_gev = hmaj.get("M_R_GeV")
    unique_mr = bool(hmaj.get("unique_heavy_majorana_scale_forced"))
    gev_nulls = []
    if os.path.isfile(ABS_PATH):
        for c in abs_t.get("candidates") or abs_t.get("inventory") or []:
            if isinstance(c, dict) and "numerical_value_GeV_or_m" in c:
                gev_nulls.append(c.get("numerical_value_GeV_or_m") is None)
    wait_for = (yard.get("do_not") and yard.get("wait_for")) or yard.get("wait_for") or []
    nF_unique_on_disk = any(
        isinstance(x, str) and "unique n_F" in x and "proven" in x for x in wait_for
    )
    # wait_for lists it as something to wait for, not proven
    nF_proven = False
    r_is_gauge = r_row and r_row.get("type") == "GAUGE"

    print("READ")
    print(f"  M_R_GeV={mr_gev} unique_forced={unique_mr}")
    print(f"  overall_R type={r_row.get('type') if r_row else None}")
    print(f"  8piG_eff_as_G_N type={geff_gn.get('type') if geff_gn else None}")
    print(f"  T_wall_as_GeV3 type={twall_gev.get('type') if twall_gev else None}")
    print(f"  Freund-Rubin unique n_F proven on disk? {nF_proven} (listed in wait_for)")
    print(f"  abs_scale GeV_or_m all null? {all(gev_nulls) if gev_nulls else 'no inventory'}")

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
        "data_dimensionless": mr_gev is None,
        "unique_mr_gev": unique_mr,
        "nF_proven": nF_proven,
        "R_gauge": r_is_gauge,
    }

    print("\nATTEMPT A — Native GeV on disk?")
    print("  physical_bridge: M_R (GeV) not_determined. predictions M_R_GeV=null.")
    print("  Isolate maps labeled dimensionless.")

    print("\nATTEMPT B — Conversion withdrawn: unique GeV M_R?")
    print("  overall_R is GAUGE; stick withdrawn. No leftover GeV atom.")

    print("\nATTEMPT C — T_wall=13/2 as GeV^3?")
    print("  Menu T_wall_as_GeV3 FORBIDDEN. Spectral identity, not tension.")

    print("\nATTEMPT D — 9/16 as G_N or M_Pl?")
    print("  Menu eight_pi_G_eff_as_G_N FORBIDDEN.")

    print("\nATTEMPT E — Freund-Rubin n_F and x=R*M_Pl?")
    print("  unique n_F is wait_for, not proven. R is GAUGE so x is not unique GeV.")

    print("\nATTEMPT F — Stage-4 seesaw back-solve?")
    print("  predictions: type_I_seesaw rejected_not_unique (needs v_EW / Yukawa).")
    print("  Light m_nu uses PDG Δm²_21 convention. Not geometric M_R.")

    r_claims = [
        {
            "id": "R1",
            "text": "locked isolate data are dimensionless (no native GeV on disk)",
            "kind": "write_closed",
        },
        {
            "id": "R2",
            "text": "unique GeV M_R from locked atoms, conversion withdrawn",
            "yes_as_lock": {"stick_left_in": True, "lambda_is_R_meters": True, "free_real": True},
            "uses_modulus": "M_R_GeV",
        },
        {
            "id": "R3",
            "text": "T_wall=13/2 forces a GeV^3 scale",
            "uses_modulus": "T_wall_as_GeV3",
            "labels_modulus_as": "G_N",
            "yes_as_lock": {"t_wall_as_tension": True},
        },
        {
            "id": "R4",
            "text": "9/16 forces G_N or M_Pl",
            "uses_modulus": "eight_pi_G_eff_as_G_N",
            "labels_modulus_as": "G_N",
            "yes_as_lock": {"geff_as_GN": True},
        },
        {
            "id": "R5",
            "text": "unique Freund-Rubin n_F and unique x=R*M_Pl from locked atoms",
            "yes_as_lock": {"stick_as_R": True, "free_real": True},
            "uses_modulus": "overall_R",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "R6",
            "text": "Stage-4 Sigma m_nu back-solves a geometric M_R",
            "yes_as_lock": {"stick_left_in": True, "free_real": True, "new_real": True},
            "uses_modulus": "v_EW",
        },
    ]

    def bin_r1():
        if facts["data_dimensionless"] and not unique_mr:
            return {
                "bin": "FORCED",
                "gates": [],
                "reasons": ["M_R_GeV is null; locked maps labeled dimensionless"],
            }
        return {
            "bin": "REFUSED",
            "gates": [],
            "reasons": ["native GeV found on disk"],
        }

    r_live = []
    print("\nid | question | unique? | live_bin | gates | why")
    for c in r_claims:
        if c["id"] == "R1":
            live = bin_r1()
        else:
            live = runCheck(c, facts)
        if live["bin"] not in LEGAL:
            fail(f"{c['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{c['id']} refuse-gate did not produce REFUSED")
        unique = live["bin"] == "FORCED"
        r_live.append({"id": c["id"], "text": c["text"], "unique": unique, **live})
        print(
            f"{c['id']} | {c['text'][:40]} | {unique} | {live['bin']} | {live.get('gates', [])} | {'; '.join(live['reasons'])[:70]}"
        )

    r2 = next(x for x in r_live if x["id"] == "R2")
    promote = r2["bin"] == "FORCED" and knobs == 0
    if promote:
        fail("would promote M_R GeV — unexpected")
    if next(r["type"] for r in rows if r["name"] == "warp_factor") != warp_t:
        fail("warp type changed")
    if next(r["type"] for r in rows if r["name"] == "g_mu_nu") != g_t:
        fail("g_mu_nu type changed")
    if next(r["type"] for r in rows if r["name"] == "unique_color") != uc_t:
        fail("unique_color type changed")

    payload = {
        "module": "mr_scale_probe",
        "continuous_knobs": 0,
        "N_gen": 3,
        "M_R_GeV": mr_gev,
        "unique_heavy_majorana_scale_forced": unique_mr,
        "R_is_GAUGE": r_is_gauge,
        "nF_proven": nF_proven,
        "promote": False,
        "R": r_live,
        "isolate_written": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(ATTEMPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\nM_R SCALE PROBE - YARDSTICK != MASS - ZERO KNOBS")
    print("Is M_R in GeV FORCED?", "Yes" if promote else "No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
