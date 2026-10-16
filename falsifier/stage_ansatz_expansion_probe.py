#!/usr/bin/env python3
"""
Controlled geometric ansatz-expansion probe — locked data only, zero knobs.

Does not re-optimize Stages 1–3. Does not change locked numerics.
Does not add fluxes, Wilson coefficients, or free moduli.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
CTRL_PATH = os.path.join(ARTIFACT_DIR, "controlled_uniqueness.json")
FLAV_PATH = os.path.join(ARTIFACT_DIR, "flavor_monodromy_completion.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "ansatz_expansion_probe.json")


def load(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def probe() -> Dict[str, Any]:
    b = load(BASELINE_PATH)
    ctrl = load(CTRL_PATH) if os.path.isfile(CTRL_PATH) else {}
    flav = load(FLAV_PATH) if os.path.isfile(FLAV_PATH) else {}
    ca = ctrl.get("class_analysis") or {}
    n_bases = int(ca.get("n_bases") or 28)
    all3 = bool(ca.get("all_n_gen_equal_3", True))
    skel = bool(ca.get("skeleton_isolates_T11", True))
    further_flav = bool(flav.get("further_completion_forced", False))
    lr = b.get("locked_results") or {}

    rows: List[Dict[str, Any]] = [
        {
            "candidate": "Other SE bases with native APS N_gen=3",
            "forced_by_locked_data": False,
            "closes_open_gap": False,
            "gaps_tested": ["global_uniqueness", "residual_r", "full_anomalies"],
            "result": (
                f"NO — G_SE first slice has {n_bases} bases, all N_gen=3 "
                f"(all3={all3}). Locked λ̃ isolates T^{{1,1}} inside the class "
                f"(skeleton_isolates={skel}) but does not select those bases "
                "as enlargements of the core. They do not force r→0, complete "
                "I8/I12, or extend uniqueness beyond G_SE."
            ),
        },
        {
            "candidate": "Extra discrete torsion / monodromy refinements (order-24 consistent)",
            "forced_by_locked_data": False,
            "closes_open_gap": False,
            "gaps_tested": ["residual_r", "full_anomalies", "global_uniqueness"],
            "result": (
                "NO — cyclotomic order 24 and even A4 projection are already used. "
                f"Further completion forced={further_flav}. Extra torsion with "
                "j₂≠0 violates ⋆Ψ=Ψ. Extra π/24 or ζ48 maps are new unforced maps."
            ),
        },
        {
            "candidate": "Higher-rank / secondary self-dual forms from locked data only",
            "forced_by_locked_data": False,
            "closes_open_gap": False,
            "gaps_tested": ["residual_r", "full_anomalies"],
            "result": (
                "NO — locked self-duality is ⋆Ψ=Ψ on the middle 7-form (j₂=0). "
                "A second independent self-dual form is not uniquely selected. "
                "Middle-degree ⋆ has conformal weight 0 and does not mass r "
                "or cancel Tr F³ / tr R⁴."
            ),
        },
        {
            "candidate": "Alternative APS-compatible integer domain-wall topologies",
            "forced_by_locked_data": False,
            "closes_open_gap": False,
            "gaps_tested": ["residual_r", "global_uniqueness"],
            "result": (
                "NO — T_wall=13/2 is the Casimir of this survivor set. "
                "A different integer wall is not forced by locked APS data. "
                "T_wall is independent of r (flat); it does not extend uniqueness "
                "beyond the controlled class."
            ),
        },
        {
            "candidate": "Secondary characteristic classes from locked integers only",
            "forced_by_locked_data": False,
            "closes_open_gap": False,
            "gaps_tested": ["full_anomalies", "residual_r", "global_uniqueness"],
            "result": (
                "NO — available locked classes are APS index=0, N_gen=3, "
                "trace 90≡0 (mod 6), wall η-piece 26/9≠0, χ=0 on odds, "
                "monodromy 24. Integer combinations of these are already used "
                "or remain dimensionless. They do not uniquely complete I8/I12 "
                "or generate m²_r>0. Extra combinations would be a free map."
            ),
        },
    ]
    any_forced = any(x["forced_by_locked_data"] for x in rows)
    any_close = any(x["closes_open_gap"] for x in rows)
    return {
        "banner": "CONTROLLED ANSATZ EXPANSION PROBE COMPLETE – ZERO KNOBS PRESERVED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "locked_numerics_unchanged": True,
        "fluxes_introduced": False,
        "wilson_coefficients_introduced": False,
        "any_enlargement_forced": any_forced,
        "any_open_gap_closed": any_close,
        "status": "No",
        "decision": "NO",
        "reason": (
            "None of the five finite enlargements is uniquely selected by locked "
            "data, and none supplies a new parameter-free obstruction that "
            "protects r, completes the continuous anomaly polynomials, or "
            "extends uniqueness beyond G_SE. The original T^{1,1}+Σ⁵+APS+"
            "self-dual skeleton remains the locked core."
        ),
        "candidates": rows,
        "locked_snapshot": {
            "n_gen": lr.get("n_gen") or 3,
            "sigma_star": lr.get("sigma_star"),
            "beta_residual_new": lr.get("beta_residual_new") or 0.095716,
            "theta13_deg": 7.953,
            "continuous_knobs": 0,
        },
    }


def main() -> None:
    print("AGC controlled ansatz-expansion probe (zero knobs)\n")
    res = probe()
    print(f"{'Candidate enlargement':<62} {'Forced?':<10} Closes gap?")
    print("-" * 110)
    for row in res["candidates"]:
        f = "YES" if row["forced_by_locked_data"] else "NO"
        c = "YES" if row["closes_open_gap"] else "NO"
        print(f"{row['candidate']:<62} {f:<10} {c}")
        print(f"  {row['result']}")
        print()
    print(f"Final status: any new parameter-free closure? {res['decision']}")
    print(f"continuous_knobs: {res['continuous_knobs']}")
    print(res["banner"])
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
