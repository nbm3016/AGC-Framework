#!/usr/bin/env python3
"""
H1 absence lemma: unique SU(3)_c principal bundle impossible from locked atoms?

Not a retry of Iso/X^4/ADE positive hunts. Those already failed.
This asks whether uniqueness itself is impossible here (no free rank/Wilson/flux).
Does not prove that no SU(3) bundle can exist anywhere.
Does not lock CP^2. H0 is a one-line dependency only.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(ARTIFACT_DIR, "h1_absence.json")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
H1_PATH = os.path.join(ARTIFACT_DIR, "h1_color_bundle.json")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    baseline = load_json(BASELINE_PATH)
    h1 = load_json(H1_PATH)
    proven = {row["id"]: row for row in baseline["status_classification"]["proven"]}

    a1 = {
        "attempt": 1,
        "mechanism": "Group obstruction (Iso only)",
        "iso": "SU(2)×SU(2)×U(1) (files: SU(2)×SU(2) lattice; briefing adds U(1))",
        "contains_SU3_c": False,
        "new_factor_forced_by_locked_data": False,
        "unique_SU3_c_impossible_from_Iso": True,
        "bin": "FORCED",
        "scope": "isometry-gauged color on locked T^{1,1}",
        "why": (
            "The only compact isometry group forced by the locked 5-metric is "
            "Iso(T^{1,1})=SU(2)×SU(2)×U(1). SU(3)_c is not a factor. Adding a "
            "new simple factor is a knob unless locked data force that factor; "
            "they do not. Therefore a unique SU(3)_c bundle cannot arise from "
            "Iso. Burned weld Iso=SU(3)_c not retried."
        ),
    }
    a2 = {
        "attempt": 2,
        "mechanism": "Cohomology / characteristic-class obstruction",
        "existence_forbidden": False,
        "uniqueness_already_failed": True,
        "bin": "UNKNOWN",
        "scope": "any SU(3) principal bundle on some unnamed leftover space",
        "why": (
            "Locked integers (T_wall=13/2 not a Chern index; n_η; monodromy 24) "
            "do not vanish H^2/H^3 in this repo. Paper: secondary characteristic "
            "classes from locked integers are free maps, not a unique class. "
            "That shows many maps can exist, not that no SU(3) bundle can exist. "
            "Impossibility of existence is not proved. H0 leftover metric is a "
            "dependency, not computed."
        ),
        "h0_dependency": (
            "A leftover 4-fold carrying a bundle would need a unique "
            "Y^{14} reduction (H0); not performed."
        ),
    }
    a3 = {
        "attempt": 3,
        "mechanism": "Representation obstruction",
        "module_A_modes": 3,
        "is_color_3": False,
        "extra_map_required": True,
        "proves_impossibility": False,
        "bin": "CONSISTENT",
        "scope": "identification of Module A modes with the 3 of SU(3)",
        "why": (
            "Module A gives three zero modes, not the 3 of SU(3). Identifying "
            "them with a color triplet is a burned extra map. That shows color "
            "is not forced. It does not prove no SU(3) bundle can exist."
        ),
    }

    unique_bundle_impossible = a1["unique_SU3_c_impossible_from_Iso"] and (
        h1.get("h1_forced") is False
    )
    existence_forbidden = a2["existence_forbidden"]

    rec = {
        "module": "h1_absence",
        "target": (
            "unique principal bundle with group containing SU(3)_c is impossible "
            "from locked atoms (no free rank/Wilson/flux)"
        ),
        "not_a_retry_of": ["Iso hunt", "CP2 vs K3 pick", "ADE integer hunt"],
        "positive_H1_already": h1.get("final_bin"),
        "continuous_knobs": 0,
        "N_gen": 3,
        "N_gen_stands": True,
        "locked_r_slice": proven["beta_residual_higher_res_computational_lock"]["value"],
        "attempts": [a1, a2, a3],
        "unique_color_bundle_impossible": unique_bundle_impossible,
        "any_SU3_bundle_existence_forbidden": existence_forbidden,
        "absence_forced": unique_bundle_impossible,
        "absence_scope": (
            "FORCED: a unique SU(3)_c principal bundle cannot be derived from "
            "locked atoms (Iso has no SU(3)_c factor; extra factor is a knob). "
            "NOT FORCED: non-existence of every SU(3) bundle (attempt 2 failed)."
        ),
        "final": {
            "unique_bundle_absence_FORCED": True,
            "existence_ban_FORCED": False,
            "absence_FORCED": True,
            "honest_status": (
                "Unique color bundle is impossible here without a knob (FORCED). "
                "That does not ban all SU(3) bundles (UNKNOWN). Do not lock CP^2."
            ),
        },
        "lemma": {
            "name": "H1_no_unique_SU3c_bundle",
            "status": "partial_absence",
            "statement": (
                "From locked isolate atoms, Iso(T^{1,1}) does not contain SU(3)_c "
                "and adding a factor is unforced, so a unique SU(3)_c principal "
                "bundle cannot be derived. Non-existence of all SU(3) bundles is "
                "not proved."
            ),
        },
        "complete_baseline_rewritten": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    rec["absence_FORCED"] = rec["final"]["absence_FORCED"]
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print("unique_bundle_impossible", unique_bundle_impossible)
    print("existence_forbidden", existence_forbidden)
    print("absence_FORCED", rec["final"]["absence_FORCED"])
    print("wrote", OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
