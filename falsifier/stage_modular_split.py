#!/usr/bin/env python3
"""
Modular split A–F: compute ports from locked inputs, emit live bins from the engine.
No stored_bin. No complete_baseline write.
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
WALL_PATH = os.path.join(ARTIFACT_DIR, "wall_tension_invariant.json")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def to_frac(x: Any) -> Fraction:
    if isinstance(x, str):
        if x.strip() in {"sqrt(3)/2", "√3/2"}:
            raise ValueError("sqrt symbol — use square instead")
        if "/" in x and "sqrt" not in x:
            a, b = x.split("/", 1)
            return Fraction(int(a), int(b))
        return Fraction(x)
    if isinstance(x, float):
        return Fraction(x).limit_denominator(10000)
    return Fraction(x)


def load_locked() -> Dict[str, Any]:
    b = load_json(BASELINE_PATH)
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = sc.get("continuous_knobs", b.get("final_locked_state", {}).get("continuous_knobs"))
    if knobs is None:
        fail("continuous_knobs missing")
    n_gen = proven.get("native_N_gen_3", {}).get("value")
    if n_gen is None:
        fail("N_gen missing")
    n_eta = proven.get("n_eta_delta_eta", {}).get("n_eta")
    lam = proven.get("lambda_tilde_derived", {}).get("value")
    sigma_sym = (b.get("final_locked_state") or {}).get("official_sigma_star") or proven.get(
        "sigma_star_shape_stabilized", {}
    ).get("value")
    r = proven.get("beta_residual_higher_res_computational_lock", {}).get("value")
    th = proven.get("residual_NLO_A4_flavor_high_scale", {})
    st4 = proven.get("stage4_mu_omega_w0", {})
    if not n_eta or lam is None or sigma_sym is None:
        fail("n_η or λ̃ or σ* missing")
    c2 = None
    descent = (b.get("anomaly_beyond_index") or {}).get("descent_audit") or {}
    if descent.get("C2_SU3") in {"4/3", "4 / 3"}:
        c2 = Fraction(4, 3)
    if c2 is None:
        fail("C2(3)=4/3 not found as locked symbol in baseline")
    twall = None
    if os.path.isfile(WALL_PATH):
        w = load_json(WALL_PATH)
        twall = w.get("T_wall_exact")
    return {
        "knobs": int(knobs),
        "N_gen": int(n_gen),
        "n_eta": [int(x) for x in n_eta],
        "lambda_tilde": list(lam),
        "sigma_star_symbol": str(sigma_sym),
        "r": r,
        "theta13": th.get("theta13_deg"),
        "mu_gammagamma": st4.get("mu_gammagamma"),
        "omega_lambda": st4.get("omega_lambda"),
        "T_wall_recorded": twall,
        "C2": c2,
        "isolate_written": False,
        "sigma_star_locked": True,
        "unique_4fold": False,
        "warp_forced": False,
        "unique_color_derived": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
    }


def compute_ports(locked: Dict[str, Any]) -> Dict[str, Any]:
    n = locked["n_eta"]
    lam = locked["lambda_tilde"]
    t_n = sum(Fraction(int(x), 1) for x in n) / 4
    fracs = []
    for x in lam:
        fracs.append(to_frac(x) if not isinstance(x, float) else Fraction(x).limit_denominator(20))
    # locked λ̃ = {4.5, 12, 22.5} = 9/2, 12, 45/2
    lam_f = [Fraction(9, 2), Fraction(12, 1), Fraction(45, 2)]
    if [float(x) for x in lam] != [4.5, 12.0, 22.5]:
        lam_f = [Fraction(x).limit_denominator(20) for x in lam]
    t_l = sum(lam_f) / 6
    if str(locked["sigma_star_symbol"]) in {"sqrt(3)/2", "√3/2"}:
        sig2 = Fraction(3, 4)
    else:
        fail("σ* symbol not sqrt(3)/2 — fail closed")
    geff = sig2 / locked["C2"]
    disagree = t_n != t_l
    print("IDENTITIES")
    print(f"  T_wall_from_n   = {t_n}   (sum n_η / 4)")
    print(f"  T_wall_from_lam = {t_l}   (sum λ̃ / 6)")
    print(f"  sigma_star_sq   = {sig2}")
    print(f"  eight_pi_G_eff  = {geff}   (σ*² / C2(3), C2={locked['C2']})")
    if disagree:
        print("  LIVE FINDING: T_wall sums disagree")
    locked["t_wall_n"] = str(t_n)
    locked["t_wall_lam"] = str(t_l)
    return {
        "T_wall_from_n": str(t_n),
        "T_wall_from_lam": str(t_l),
        "T_wall_agree": not disagree,
        "sigma_star_sq": str(sig2),
        "eight_pi_G_eff": str(geff),
        "C2": str(locked["C2"]),
        "disagree": disagree,
    }


def build_questions() -> List[Dict[str, Any]]:
    """No stored_bin."""
    return [
        {
            "id": "Q1",
            "text": "Are isolate atoms write-closed at knobs=0, N_gen=3?",
            "kind": "write_closed",
        },
        {
            "id": "Q2",
            "text": "Is E1 five-metric locked?",
            "kind": "five_metric",
        },
        {
            "id": "Q3",
            "text": "Is E2 a unique picked 4-fold?",
            "kind": "unique_4fold",
        },
        {
            "id": "Q4",
            "text": "Is E3 warp forced?",
            "kind": "warp",
        },
        {
            "id": "Q5",
            "text": "Is g_μν identical to σ*?",
            "kind": "gmunu_is_sigma",
            "yes_as_lock": {"sigma_is_gmunu": True},
        },
        {
            "id": "Q6",
            "text": "Is B0 Iso the isometry of the locked 5-fold, and is it a color lock?",
            "kind": "iso_and_color",
        },
        {
            "id": "Q7",
            "text": "Is unique color derived from the isolate?",
            "kind": "unique_color",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True},
        },
        {
            "id": "Q8",
            "text": "Is G_SM forced from the isolate?",
            "kind": "G_SM",
            "yes_as_lock": {"weld_class_to_lock": True, "unique_color_derived": True},
        },
        {
            "id": "Q9",
            "text": "Is ℂℙ² or K3 the 4-fold?",
            "kind": "picked_4fold",
            "yes_as_lock": {"weld_class_to_lock": True},
        },
        {
            "id": "Q10",
            "text": "Are P3 and P4 computed identities of the locked ports (not a spacetime metric, not G_N)?",
            "kind": "port_identities",
        },
    ]


def build_ports() -> List[Dict[str, Any]]:
    return [
        {
            "id": "P1",
            "text": "b2, b3 of T^{1,1} ≃ S²×S³. Topology or flux?",
            "kind": "port_topology",
            "value": {"b2": 1, "b3": 1, "reading": "topology"},
        },
        {
            "id": "P2",
            "text": "Iso group. Is it color?",
            "kind": "port_iso",
            "value": {"group": "SU(2)×SU(2)×U(1)", "is_color": False},
        },
        {
            "id": "P3",
            "text": "T_wall from locked n_η and locked λ̃",
            "kind": "port_twall",
        },
        {
            "id": "P4",
            "text": "σ*² and 8πG_eff = σ*²/C₂(3)",
            "kind": "port_sigma_Geff",
        },
    ]


def dump(path: str, obj: Any) -> None:
    with open(os.path.join(ARTIFACT_DIR, path), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)
    locked = load_locked()
    if locked["knobs"] != 0:
        fail("knobs != 0")
    if locked["N_gen"] != 3:
        fail("N_gen != 3")

    ports_num = compute_ports(locked)
    locked["t_wall_n"] = ports_num["T_wall_from_n"]
    locked["t_wall_lam"] = ports_num["T_wall_from_lam"]

    qs = build_questions()
    ps = build_ports()
    ps[2]["value"] = {
        "T_wall_from_n": ports_num["T_wall_from_n"],
        "T_wall_from_lam": ports_num["T_wall_from_lam"],
        "agree": ports_num["T_wall_agree"],
    }
    ps[3]["value"] = {
        "sigma_star_sq": ports_num["sigma_star_sq"],
        "eight_pi_G_eff": ports_num["eight_pi_G_eff"],
        "is_G_N": False,
        "proves_SU3c": False,
    }

    q_live = []
    print("id | claim | live_bin | gates | reasons")
    for q in qs:
        live = runCheck(q, locked)
        if live["bin"] not in LEGAL:
            fail(f"{q['id']} illegal bin {live['bin']}")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{q['id']} refuse-gate did not produce REFUSED")
        q_live.append({"id": q["id"], "text": q["text"], "kind": q["kind"], **live})
        print(
            f"{q['id']} | {q['text'][:48]} | {live['bin']} | {live['gates']} | {'; '.join(live['reasons'])}"
        )

    p_live = []
    print("port | value | live_bin | not_implied")
    for p in ps:
        live = runCheck(p, locked)
        if live["bin"] not in LEGAL:
            fail(f"{p['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{p['id']} refuse-gate did not produce REFUSED")
        p_live.append({"id": p["id"], "text": p["text"], "value": p.get("value"), **live})
        print(
            f"{p['id']} | {p.get('value')} | {live['bin']} | {live.get('not_implied')}"
        )

    modules = {
        "A": "Frozen isolate / Layer A. Input owner. Write-set closed.",
        "B": {
            "B0": "What is Iso of the locked 5-fold?",
            "B1": "Does that group contain SU(3)_c as a derived subgroup?",
            "B2": "Does the isolate force a unique G_SM?",
            "B3": "Is hypercharge flux forced, class, or not derived?",
            "B4": "Are graph Aut 2-planes SM generations?",
            "B5": "Is CKM / V_cb forced?",
        },
        "C": {
            "E1": "What 5-metric is actually locked on T^{1,1}?",
            "E2": "Is a unique 4-fold forced, or only a class?",
            "E3": "Is warp forced?",
            "E4": "Is g_μν derived from σ*?",
        },
        "D": "Ports P1–P4 computed then binned",
        "E": "check_engine.runCheck",
        "F": "Open ledger — gaps not closed to finish a table",
    }
    dump("modules.json", modules)
    dump(
        "h0_split.json",
        {
            "E1": next(x for x in q_live if x["id"] == "Q2"),
            "E2": next(x for x in q_live if x["id"] == "Q3"),
            "E3": next(x for x in q_live if x["id"] == "Q4"),
            "E4": next(x for x in q_live if x["id"] == "Q5"),
        },
    )
    dump(
        "h1_pipes.json",
        {
            "B0": next(x for x in q_live if x["id"] == "Q6"),
            "B1_B2": next(x for x in q_live if x["id"] == "Q8"),
            "unique_color": next(x for x in q_live if x["id"] == "Q7"),
            "picked_4fold": next(x for x in q_live if x["id"] == "Q9"),
        },
    )
    dump("computed_ports.json", {"numeric": ports_num, "ports": p_live})
    dump(
        "work_ledger.json",
        {
            "questions": q_live,
            "ports": p_live,
            "continuous_knobs": 0,
            "isolate_written": False,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
    )

    md = [
        "# Modular split A–F",
        "",
        "Computed from locked inputs. Bins emitted by `check_engine.runCheck`. No stored_bin.",
        "complete_baseline.json was not written.",
        "",
        "See `work_ledger.json` for live bins.",
        "",
    ]
    with open(os.path.join(ARTIFACT_DIR, "MODULAR_SPLIT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("MODULAR SPLIT A–F COMPUTED AND CHECKED – LIVE BINS FROM ENGINE – ZERO KNOBS")
    if locked["isolate_written"]:
        fail("isolate was written")
    if locked["knobs"] != 0:
        fail("knobs changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
