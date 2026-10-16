#!/usr/bin/env python3
"""
H1 color-bundle probe: unique SU(3)_c / ADE from locked isolate atoms?

Three distinct attempts. No burned welds. No SM-looking pick.
MAP ≠ LOCK. CLASS names are scaffolding and are withdrawn before any lock.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(ARTIFACT_DIR, "h1_color_bundle.json")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
BRIDGE_PATH = os.path.join(ARTIFACT_DIR, "physical_bridge.json")
NATIVE_PATH = os.path.join(ARTIFACT_DIR, "native_aps_index.py")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ade_simply_laced() -> List[Dict[str, Any]]:
    rows = []
    for n in range(1, 25):
        rows.append({"name": f"A{n}", "rank": n, "coxeter": n + 1, "family": "A"})
    for n in range(4, 25):
        rows.append({"name": f"D{n}", "rank": n, "coxeter": 2 * n - 2, "family": "D"})
    rows.extend(
        [
            {"name": "E6", "rank": 6, "coxeter": 12, "family": "E"},
            {"name": "E7", "rank": 7, "coxeter": 18, "family": "E"},
            {"name": "E8", "rank": 8, "coxeter": 30, "family": "E"},
        ]
    )
    return rows


def attempt1_iso() -> Dict[str, Any]:
    # Files: SU(2)×SU(2) from T^{1,1} isometry lattice; briefing adds U(1).
    iso_files = "SU(2)×SU(2) lattice from T^{1,1} isometry (native_aps_index.py)"
    iso_briefing = "Iso(T^{1,1})=SU(2)×SU(2)×U(1) (ingested briefing; not SU(3)_c)"
    contains_su3c = False
    burned = "Iso(T^{1,1})=SU(3)_c is burned; not retried as the proof"
    return {
        "attempt": 1,
        "mechanism": "Iso of locked space",
        "iso_from_files": iso_files,
        "iso_from_briefing": iso_briefing,
        "contains_SU3_c": contains_su3c,
        "unique_SU3_c_or_ADE": False,
        "bin": "REFUSED",
        "why": (
            "Locked T^{1,1} isometry algebra cited in-repo is SU(2)×SU(2) "
            "(plus briefing U(1)). That group does not contain SU(3)_c as a "
            "simple factor. Enlarging the group by hand is forbidden. "
            + burned
        ),
        "scaffolding_withdrawn": True,
    }


def attempt2_x4() -> Dict[str, Any]:
    named = ["CP^2 (KK color, scaffolding)", "K3 (Einstein / existing 7-form, scaffolding)"]
    return {
        "attempt": 2,
        "mechanism": "Unique leftover X^4",
        "named_classes_scaffolding": named,
        "unique_X4_forced": False,
        "unique_SU3_c_or_ADE": False,
        "bin": "CLASS",
        "why": (
            "Locked atoms do not force a unique leftover 4-fold. CP^2 and K3 "
            "are named classes only; neither is selected without an extra "
            "choice. Picking CP^2 because QCD wants SU(3) is forbidden. "
            "physical_bridge.json: no locked map to a SM gauge coupling. "
            "H0 metric reduction is a one-line dependency, not performed."
        ),
        "h0_dependency_note": (
            "A unique X^4 would need a unique Y^{14}→M^4×X^{10} reduction (H0), "
            "which is not in the isolate."
        ),
        "scaffolding_withdrawn": True,
    }


def attempt3_ade(locked: Dict[str, Any]) -> Dict[str, Any]:
    n_gen = 3
    n_eta = locked["n_eta"]
    monodromy = 24
    t_wall = 13.0 / 2.0
    integers = {
        "N_gen": n_gen,
        "n1": n_eta[0],
        "n2": n_eta[1],
        "n3": n_eta[2],
        "sum_n_eta": sum(n_eta),
        "monodromy": monodromy,
    }
    ade = ade_simply_laced()
    hits: List[Dict[str, Any]] = []
    for row in ade:
        reasons = []
        if row["rank"] == n_gen:
            reasons.append("rank=N_gen=3")
        if row["coxeter"] == n_gen:
            reasons.append("coxeter=N_gen=3")
        if row["rank"] == monodromy:
            reasons.append("rank=monodromy=24")
        if row["coxeter"] == monodromy:
            reasons.append("coxeter=monodromy=24")
        if row["rank"] == n_eta[0]:
            reasons.append("rank=n1=3")
        if row["coxeter"] == n_eta[0]:
            reasons.append("coxeter=n1=3")
        if row["coxeter"] == n_eta[1]:
            reasons.append("coxeter=n2=8")
        if row["rank"] == n_eta[1]:
            reasons.append("rank=n2=8")
        if row["coxeter"] == n_eta[2]:
            reasons.append("coxeter=n3=15")
        if abs(row["coxeter"] - t_wall) < 1e-12:
            reasons.append("coxeter=T_wall")
        if reasons:
            hits.append({"ade": row["name"], "rank": row["rank"], "coxeter": row["coxeter"], "matches": reasons})
    a2 = [h for h in hits if h["ade"] == "A2"]
    a3 = [h for h in hits if h["ade"] == "A3"]
    return {
        "attempt": 3,
        "mechanism": "ADE from locked integers only",
        "locked_integers": integers,
        "T_wall": "13/2 (not an integer Coxeter number)",
        "n_ADE_hits_any_single_integer": len(hits),
        "sample_hits": hits[:12],
        "A2_and_A3_both_hit_integer_3": bool(a2) and bool(a3),
        "unique_SU3_c_or_ADE": False,
        "bin": "REFUSED",
        "why": (
            "The same integer 3 matches A2 (coxeter=N_gen) and A3 (rank=N_gen). "
            "Monodromy 24 matches A23 (coxeter) and other diagrams. Several ADE "
            "fit the same locked integers depending on an extra map (rank vs "
            "coxeter vs dim of 3). Uniqueness refused. C2(3)=4/3 in V(σ) is "
            "burned as a color proof."
        ),
        "scaffolding_withdrawn": True,
    }


def main() -> int:
    baseline = load_json(BASELINE_PATH)
    proven = {row["id"]: row for row in baseline["status_classification"]["proven"]}
    bridge = load_json(BRIDGE_PATH)
    locked = {
        "N_gen": proven["native_N_gen_3"]["value"],
        "n_eta": proven["n_eta_delta_eta"]["n_eta"],
        "r": proven["beta_residual_higher_res_computational_lock"]["value"],
        "sigma_star": proven["sigma_star_shape_stabilized"]["value"],
        "theta13_deg": proven["residual_NLO_A4_flavor_high_scale"]["theta13_deg"],
    }
    a1 = attempt1_iso()
    a2 = attempt2_x4()
    a3 = attempt3_ade(locked)
    attempts = [a1, a2, a3]
    forced = [a for a in attempts if a["bin"] == "FORCED"]
    h1_forced = len(forced) == 1 and forced[0]["unique_SU3_c_or_ADE"]
    rec = {
        "module": "h1_color_bundle",
        "target": "unique gauge bundle containing SU(3)_c or unique ADE reducing to G_SM",
        "continuous_knobs": 0,
        "N_gen_stands": True,
        "N_gen": 3,
        "locked_snapshot_unchanged": True,
        "h0_metric_reduction": "dependency note only; not performed",
        "burned_not_retried": [
            "Iso(T^{1,1})=SU(3)_c",
            "holonomy SU(3)=QCD",
            "chi=N_gen welded to CP2",
            "N_gen=dim of the 3 of SU(3)",
            "3 APS modes=45 SM Weyl",
            "C2(3)=4/3 in V(sigma) as proof of color",
            "graph orbits=color or SM gens",
        ],
        "physical_bridge_no_SM_gauge": next(
            q for q in bridge["not_determined_by_locked_geometry"] if "alpha" in q["quantity"] or "G_F" in q["quantity"]
        ),
        "attempts": attempts,
        "h1_forced": h1_forced,
        "final_bin": "OPEN_LEMMA" if not h1_forced else "FORCED",
        "lemma": {
            "name": "H1_unique_color_bundle",
            "status": "open",
            "required_theorem": (
                "A unique functor from locked isolate atoms to a principal "
                "bundle P→compact space with Aut(P) containing SU(3)_c "
                "(or a unique ADE that reduces to G_SM) with no free rank, "
                "Wilson line, or flux."
            ),
            "next_experiment": (
                "Do not pick CP^2. Either derive a unique leftover 4-fold from "
                "a completed H0 reduction without knobs, or prove no such bundle "
                "exists in this isolate (negative lemma)."
            ),
        },
        "MAP_NOT_LOCK": "stays",
        "complete_baseline_rewritten": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print("h1_forced", rec["h1_forced"], rec["final_bin"])
    for a in attempts:
        print(a["attempt"], a["bin"], a["unique_SU3_c_or_ADE"])
    print("wrote", OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
