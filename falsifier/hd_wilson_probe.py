#!/usr/bin/env python3
"""
HD Wilson probe: form-forced is not coefficient-forced.
Do not invent alpha_k. Do not reopen warp / g_mu_nu / unique color.
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
HD_PATH = os.path.join(ARTIFACT_DIR, "controlled_hd_sector.json")
UV_PATH = os.path.join(ARTIFACT_DIR, "hd_uv_probe.json")
TEST_PATH = os.path.join(ARTIFACT_DIR, "higher_derivative_test.json")
ATTEMPTS_PATH = os.path.join(ARTIFACT_DIR, "hd_wilson_attempts.json")


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
    hd = load_json(HD_PATH)
    uv = load_json(UV_PATH) if os.path.isfile(UV_PATH) else {}
    test = load_json(TEST_PATH) if os.path.isfile(TEST_PATH) else {}
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    r = proven["beta_residual_higher_res_computational_lock"]["value"]
    th13 = proven["residual_NLO_A4_flavor_high_scale"]["theta13_deg"]
    if knobs != 0:
        fail("knobs != 0")
    if n_gen != 3:
        fail("N_gen != 3")

    lemma = hd.get("eligibility_lemma") or []
    form_forced = [x for x in lemma if x.get("form_forced")]
    coeff_forced = [x for x in lemma if x.get("coefficient_forced")]
    n_form = len(form_forced)
    n_coeff = len(coeff_forced)
    n_uv_forced = int(uv.get("n_coefficients_forced") or 0)
    n_test_forced = 0
    if isinstance(test.get("candidates_examined"), list):
        n_test_forced = sum(1 for c in test["candidates_examined"] if c.get("forced_by_geometry"))

    print("READ")
    print(f"  n_form_forced={n_form} {[x['operator'] for x in form_forced]}")
    print(f"  n_coeff_forced_lemma={n_coeff} uv={n_uv_forced} test={n_test_forced}")
    print(f"  r={r} theta13={th13} knobs={knobs}")
    print(f"  residual_NNLO eligible={next((x.get('eligible') for x in lemma if x.get('operator')=='residual_NNLO_r_powers'), None)}")
    print(f"  alpha_prime_unit_maps eligible={next((x.get('eligible') for x in lemma if x.get('operator')=='alpha_prime_unit_maps'), None)}")

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
        "n_form_forced": n_form,
        "n_coeff_forced": n_coeff + n_uv_forced + n_test_forced,
    }

    # H1 form: compute from n_form_forced. Any form-forced, not unique among HD ops.
    h_claims = [
        {
            "id": "H1",
            "text": "any HD form (Lovelock/GB/C^2/R^2) forced as a form",
            "kind": "hd_form",
        },
        {
            "id": "H2",
            "text": "unique coefficient alpha_k forced by locked atoms",
            "kind": "hd_coeff",
        },
        {
            "id": "H3",
            "text": "official r=0.095716 fixes a new alpha_k (leftover residual as Wilson knob)",
            "yes_as_lock": {"free_real": True, "new_real": True},
            "uses_modulus": "alpha_k_from_r",
        },
        {
            "id": "H4",
            "text": "alpha-prime / GeV unit map forces a Wilson coefficient",
            "yes_as_lock": {"lambda_is_R_meters": True, "stick_as_R": True},
            "uses_modulus": "alpha_prime_unit_map",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "H5",
            "text": "wall K^3 / torsion HD coefficient uniquely forced",
            "kind": "hd_wall",
        },
        {
            "id": "H6",
            "text": "forced form promotes a coefficient to FORCED",
            "yes_as_lock": {"map_called_lock": True, "modulus_called_lock": True},
            "uses_modulus": "warp_factor",
            "labels_modulus_as": "FORCED",
        },
    ]

    def bin_h1():
        if n_form == 0:
            return {
                "bin": "REFUSED",
                "gates": [],
                "reasons": ["no form_forced operator in locked HD files"],
            }
        if n_form == 1:
            return {
                "bin": "CLASS",
                "gates": [],
                "reasons": [f"one form_forced operator: {form_forced[0]['operator']}; coefficient_forced false"],
            }
        return {
            "bin": "CLASS",
            "gates": [],
            "reasons": [
                f"{n_form} form_forced operators { [x['operator'] for x in form_forced] }; form != unique alpha_k"
            ],
        }

    def bin_h2():
        n = n_coeff + n_uv_forced + n_test_forced
        if n == 1:
            return {"bin": "FORCED", "gates": [], "reasons": ["exactly one coefficient_forced"]}
        if n == 0:
            return {
                "bin": "REFUSED",
                "gates": [],
                "reasons": ["n_forced_coefficients=0 in locked HD files; eligible form != unique alpha_k"],
            }
        return {
            "bin": "REFUSED",
            "gates": [],
            "reasons": [f"{n} coefficient_forced flags — not unique"],
        }

    def bin_h5():
        wall = next((x for x in lemma if x.get("operator") == "domain_wall_K_K3"), None)
        tors = next((x for x in lemma if x.get("operator") == "self_dual_torsion_HD"), None)
        if wall and wall.get("coefficient_forced"):
            return {"bin": "FORCED", "gates": [], "reasons": ["wall coeff forced in file"]}
        return {
            "bin": "REFUSED",
            "gates": [],
            "reasons": [
                "wall K^3 needs_length; torsion source_vanishes; coefficient_forced false"
            ],
        }

    h_live = []
    print("\nid | question | unique? | live_bin | gates | why")
    for c in h_claims:
        if c["id"] == "H1":
            live = bin_h1()
        elif c["id"] == "H2":
            live = bin_h2()
        elif c["id"] == "H5":
            live = bin_h5()
        else:
            live = runCheck(c, facts)
        if live["bin"] not in LEGAL:
            fail(f"{c['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{c['id']} refuse-gate did not produce REFUSED")
        unique = live["bin"] == "FORCED"
        h_live.append({"id": c["id"], "text": c["text"], "unique": unique, **live})
        print(
            f"{c['id']} | {c['text'][:36]} | {unique} | {live['bin']} | {live.get('gates', [])} | {'; '.join(live['reasons'])[:70]}"
        )

    h2 = next(x for x in h_live if x["id"] == "H2")
    promote = h2["bin"] == "FORCED" and knobs == 0
    if promote:
        fail("would promote alpha_k — unexpected; do not invent")
    if next(r["type"] for r in rows if r["name"] == "warp_factor") != warp_t:
        fail("warp type changed")
    if next(r["type"] for r in rows if r["name"] == "g_mu_nu") != g_t:
        fail("g_mu_nu type changed")
    if next(r["type"] for r in rows if r["name"] == "unique_color") != uc_t:
        fail("unique_color type changed")

    payload = {
        "module": "hd_wilson_probe",
        "continuous_knobs": 0,
        "N_gen": 3,
        "r": r,
        "theta13_deg": th13,
        "n_form_forced": n_form,
        "n_coeff_forced": n_coeff + n_uv_forced + n_test_forced,
        "form_forced_operators": [x["operator"] for x in form_forced],
        "promote_alpha_k": False,
        "H": h_live,
        "isolate_written": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(ATTEMPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print("\nHD WILSON PROBE - FORM != COEFFICIENT - ZERO KNOBS")
    print("Is any unique HD coefficient FORCED?", "Yes" if promote else "No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
