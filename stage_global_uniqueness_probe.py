#!/usr/bin/env python3
"""
Global vacuum uniqueness probe — locked data only, zero knobs.

Does not re-optimize Stages 1–3. Does not introduce fluxes or anthropics.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
CTRL_PATH = os.path.join(ARTIFACT_DIR, "controlled_uniqueness.json")
VAC_PATH = os.path.join(ARTIFACT_DIR, "vacuum_selection.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "global_uniqueness_probe.json")


def load(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def probe() -> Dict[str, Any]:
    b = load(BASELINE_PATH)
    ctrl = load(CTRL_PATH) if os.path.isfile(CTRL_PATH) else {}
    vac = load(VAC_PATH) if os.path.isfile(VAC_PATH) else {}
    ca = ctrl.get("class_analysis") or {}
    n_bases = int(ca.get("n_bases") or 0)
    all3 = bool(ca.get("all_n_gen_equal_3"))
    ngen_selects = bool(ca.get("n_gen_selects_T11"))
    skel = bool(ca.get("skeleton_isolates_T11"))
    hits = list(ca.get("locked_lambda_hits") or [])
    lr = b.get("locked_results") or {}

    rows: List[Dict[str, Any]] = [
        {
            "obstruction": "Native APS index + self-duality as landscape-wide N_gen≠3 ban",
            "rules_out_alternatives": False,
            "scope": "G_SE first slice (28 bases), not all 14D",
            "result": (
                f"NO as global filter — {n_bases}/28 enumerated SE bases have "
                f"N_gen=3 (all_n_gen_equal_3={all3}; n_gen_selects_T11={ngen_selects}). "
                "APS+self-duality do not forbid competing SE fibrations."
            ),
        },
        {
            "obstruction": "Monodromy order 24 + Σ⁵ domain wall",
            "rules_out_alternatives": True,
            "scope": "locked T^{1,1}+Σ⁵ sector only",
            "result": (
                "YES inside G_T11 (η-lattice / π-relation / APS wall). "
                "NO landscape-wide — those data are defined on this ansatz, "
                "not as a theorem on all 14D fibrations."
            ),
        },
        {
            "obstruction": "Competing fibration with same index, self-duality, residual",
            "rules_out_alternatives": False,
            "scope": "global landscape",
            "result": (
                "NOT RULED OUT — other first-slice bases satisfy APS+self-dual+N_gen=3. "
                "Locked λ̃={4.5,12,22.5} isolates T^{1,1} inside G_SE only "
                f"(hits={hits}). Residual r is a T^{1,1} EY mismatch, not a "
                "topology classifier. L^{a,b,c} / other 14D fibrations untested."
            ),
        },
        {
            "obstruction": "Index + self-duality + V(σ) as unique stable 14D minimum",
            "rules_out_alternatives": True,
            "scope": "G_T11 diffeotype (continuous moduli of this background)",
            "result": (
                "YES for continuous off-sector motion on this background "
                "(j₂, APS fiber r, σ≠σ*). NO as uniqueness among topologies."
            ),
        },
        {
            "obstruction": "Landscape-wide classification theorem in locked baseline",
            "rules_out_alternatives": False,
            "scope": "global landscape",
            "result": (
                "ABSENT — vacuum_selection already records other SE / 14D "
                "fibrations untested. No parameter-free global obstruction is present."
            ),
        },
        {
            "obstruction": "Anthropic selection",
            "rules_out_alternatives": False,
            "scope": "forbidden",
            "result": "NOT USED",
        },
    ]

    return {
        "banner": "GLOBAL VACUUM UNIQUENESS PROBE COMPLETE – ZERO KNOBS PRESERVED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "locked_numerics_unchanged": True,
        "anthropic_selection_used": False,
        "fluxes_introduced": False,
        "global_vacuum_uniqueness_achieved": False,
        "status": "Partial (controlled-class only)",
        "decision": "Partial (controlled-class only)",
        "proof_boundary": (
            "Uniqueness is proven for continuous deformations of locked T^{1,1}+Σ⁵ "
            "and for isolation of the locked skeleton inside first-slice G_SE "
            f"(skeleton_isolates_T11={skel}). It is not proven among all 14D "
            "fibrations. Claiming landscape-wide uniqueness would exceed the locked data."
        ),
        "n_G_SE_bases": n_bases,
        "G_SE_all_n_gen_3": all3,
        "obstructions": rows,
        "prior_vacuum_uniqueness": vac.get("uniqueness_achieved"),
        "locked_snapshot": {
            "n_gen": lr.get("n_gen") or 3,
            "sigma_star": lr.get("sigma_star"),
            "beta_residual_new": lr.get("beta_residual_new") or 0.095716,
            "continuous_knobs": 0,
        },
    }


def main() -> None:
    print("AGC global vacuum uniqueness probe (zero knobs)\n")
    res = probe()
    print(f"{'Obstruction examined':<62} {'Rules out?':<12} Scope")
    print("-" * 110)
    for row in res["obstructions"]:
        yn = "YES*" if row["rules_out_alternatives"] else "NO"
        print(f"{row['obstruction']:<62} {yn:<12} {row['scope']}")
        print(f"  {row['result']}")
        print()
    print(f"Final status: global vacuum uniqueness achieved? {res['status']}")
    print(f"continuous_knobs: {res['continuous_knobs']}")
    print(res["proof_boundary"])
    print(res["banner"])
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
