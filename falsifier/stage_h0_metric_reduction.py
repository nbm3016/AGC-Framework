#!/usr/bin/env python3
"""
H0 metric / reduction probe.

Does locked isolate data uniquely force (g_{Y^{14}}, g_{μν}) with no free
warp, radius, Wilson coefficient, or leftover-X^4 choice?

Does not treat σ* or Weyl λ as a 4D metric.
Does not pick K3 or CP^2. Does not re-open Absolute Scale as a dynamical modulus.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(ARTIFACT_DIR, "h0_metric_reduction.json")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
CLASS_PATH = os.path.join(ARTIFACT_DIR, "h1h0_class_map.json")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    baseline = load_json(BASELINE_PATH)
    proven = {row["id"]: row for row in baseline["status_classification"]["proven"]}
    class_map = load_json(CLASS_PATH)
    a1 = {
        "attempt": 1,
        "mechanism": "Unique 14D metric from locked 5-geometry",
        "unique": False,
        "bin": "CLASS",
        "why": (
            "Locked data force a unique squashed T^{1,1} 5-metric (σ*=√3/2) "
            "plus Σ^5 wall and self-dual 7-form on that compact sector. They do "
            "not fix leftover X^4 or warps that would complete g_{Y^{14}}. "
            "σ* is shape of T^{1,1}, not g_{μν}. Briefing fibration Y^{14}→M^4 "
            "is ansatz language (M4_BRIDGE.md), not a coded 14D metric."
        ),
        "what_is_forced": "unique 5-metric on T^{1,1} at σ*",
        "what_is_free": ["leftover X^4", "warps between factors"],
    }
    a2 = {
        "attempt": 2,
        "mechanism": "Unique 4D Einstein / KK reduction",
        "unique": False,
        "bin": "REFUSED",
        "why": (
            "No live g_{μν}(x) is discretized (M4_BRIDGE.md; physical_bridge.json). "
            "KK ansatz ds² = e^{2A} g_{μν}(x) + g_int has warp A and 4D conformal "
            "class unfixed by locked atoms. λ is Weyl gauge / observational "
            "conversion, not R in meters. Absolute scale is not reopened as a "
            "dynamical modulus (N1–N12 negative; closed by quotienting)."
        ),
        "warp_A_fixed": False,
        "g_mu_nu_Einstein_forced": False,
        "live_g_mu_nu_in_repo": False,
    }
    a3 = {
        "attempt": 3,
        "mechanism": "Leftover 4-fold as part of H0",
        "unique": False,
        "bin": "CLASS",
        "why": (
            "Existing CLASS map: leftover X^4 is not forced to be K3 vs CP^2 vs "
            "T^4 vs other Einstein 4-folds (h1h0_class_map.json). Not picked "
            "because reductions often use K3."
        ),
        "track_B_lock": class_map.get("track_B_lock", False),
        "named_not_picked": ["K3", "CP^2", "T^4"],
    }

    rec = {
        "module": "h0_metric_reduction",
        "target": "unique (g_Y14, g_mu_nu) with no free warp/radius/Wilson/X^4",
        "h0_forced": False,
        "continuous_knobs": 0,
        "N_gen": 3,
        "N_gen_stands": True,
        "sigma_star_is_not_g_mu_nu": True,
        "lambda_is_not_R_meters": True,
        "absolute_scale_reopened": False,
        "locked_r_slice": proven["beta_residual_higher_res_computational_lock"]["value"],
        "attempts": [a1, a2, a3],
        "lemma": {
            "name": "H0_unique_metric_reduction",
            "status": "open",
            "required_theorem": (
                "A unique 14D metric g_{Y^{14}} and a unique KK reduction to "
                "an Einstein g_{μν}(x) with warp A fixed by locked isolate atoms."
            ),
            "extra_data_remaining": [
                "leftover X^4 (K3 vs CP^2 vs T^4 vs other)",
                "warp A in ds² = e^{2A} g_{μν} + g_int",
                "4D conformal class of g_{μν}",
            ],
        },
        "complete_baseline_rewritten": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print("h0_forced", rec["h0_forced"])
    for a in rec["attempts"]:
        print(a["attempt"], a["bin"], a["unique"])
    print("wrote", OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
