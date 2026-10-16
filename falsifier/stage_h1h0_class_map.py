#!/usr/bin/env python3
"""
Dual CLASS map: Track A external SU(3) bundle; Track B K3 leftover 4-fold.

Neither is a lock. Uniqueness is not forced from current atoms.
Do not lock CP^2 or K3. Do not install SU(3)_c.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(ARTIFACT_DIR, "h1h0_class_map.json")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def chern_fits() -> List[Dict[str, Any]]:
    """Named scaffolding: identify locked integers with (rank, c2, instanton k)."""
    n_eta = (3, 8, 15)
    ints = {
        "N_gen": 3,
        "n1": 3,
        "n2": 8,
        "n3": 15,
        "sum_n": 26,
        "monodromy": 24,
        "T_wall": "13/2",
        "Delta_eta_denoms": [4, 3, 4],
    }
    fits = [
        {"map": "rank=N_gen=3", "rank": 3, "group_hint": "not SU(3) rank (SU(3) rank=2)"},
        {"map": "rank=2 not in locked ints as unique", "rank": 2, "group_hint": "SU(3) rank; extra choice"},
        {"map": "c2=N_gen=3", "c2": 3},
        {"map": "c2=n2=8", "c2": 8},
        {"map": "c2=n3=15", "c2": 15},
        {"map": "c2=monodromy=24", "c2": 24},
        {"map": "c2=sum_n_eta=26", "c2": 26},
        {"map": "instanton_k=N_gen=3", "k": 3},
        {"map": "instanton_k=n2=8", "k": 8},
        {"map": "instanton_k=monodromy=24", "k": 24},
        {"map": "T_wall=13/2 as c2", "c2": 6.5, "note": "not an integer instanton number"},
        {"map": "dim SU(3)=8=n2", "extra": "identifies dim(G) with n_eta_2"},
    ]
    return ints, fits


def main() -> int:
    baseline = load_json(BASELINE_PATH)
    proven = {row["id"]: row for row in baseline["status_classification"]["proven"]}
    ints, fits = chern_fits()

    a1 = {
        "attempt": 1,
        "track": "A",
        "mechanism": "Bundle Chern data vs locked integers",
        "unique": False,
        "bin": "REFUSED",
        "why": (
            f"{len(fits)} distinct identifications of {{c2, rank, k}} with "
            "{N_gen, n_η, 24, 13/2}. Existence of some SU(3) bundle is not "
            "uniqueness. Matching N_gen or T_wall to c2 by hand is a map. "
            "Wilson lines / parabolic reduction remain unfixed scaffolding."
        ),
        "n_fits": len(fits),
        "fits": fits,
        "scaffolding_named": ["c2", "instanton number k", "Wilson lines", "parabolic reduction"],
        "scaffolding_withdrawn": True,
    }
    named_4folds = ["K3 (holonomy SU(2), not SU(3))", "CP^2 (KK-isometry color option)", "T^4", "other Einstein 4-folds"]
    a2 = {
        "attempt": 2,
        "track": "B",
        "mechanism": "K3 reduction class vs other leftover 4-folds",
        "unique": False,
        "bin": "CLASS",
        "why": (
            "Locked isolate does not force leftover X^4 ≅ K3 rather than "
            "CP^2 / T^4 / other Einstein 4-folds. Holonomy of a K3 metric is "
            "SU(2), not SU(3). Iso(K3) is not SU(3)_c. CP^2 stays named as the "
            "KK-isometry color option; not picked because QCD wants SU(3)."
        ),
        "named_classes": named_4folds,
        "k3_gives": [
            "SU(2) holonomy of a hyperkahler metric",
            "can CARRY an external SU(3) bundle (Track A on Track B, still CLASS)",
        ],
        "k3_does_not_give": [
            "SU(3)_c as holonomy",
            "SU(3)_c as Iso(K3)",
            "a unique leftover 4-fold",
            "a live 4D Einstein metric",
        ],
        "h0_dependency": (
            "Live 4D Einstein / KK needs a unique 14D metric + reduction; "
            "this track does not produce that metric."
        ),
        "scaffolding_withdrawn": True,
    }
    a3 = {
        "attempt": 3,
        "track": "A+B",
        "mechanism": "Combined (K3, SU(3) bundle) functor",
        "unique": False,
        "bin": "REFUSED",
        "why": (
            "A pair (X^4, P) is a product of a non-unique leftover class and "
            "non-unique Chern data. No unique pair (K3, SU(3) bundle) from "
            "locked atoms. Picking the SM-looking pair is forbidden."
        ),
        "scaffolding_withdrawn": True,
    }

    rec = {
        "module": "h1h0_class_map",
        "map_neq_lock": True,
        "track_A_lock": False,
        "track_B_lock": False,
        "combined_lock": False,
        "H1_unique_color": "NOT_DERIVED",
        "iso_is_not_color": True,
        "CP2_locked": False,
        "K3_locked": False,
        "SU3_c_installed": False,
        "continuous_knobs": 0,
        "N_gen": 3,
        "N_gen_stands": True,
        "locked_integers": ints,
        "attempts": [a1, a2, a3],
        "extra_data_remaining": [
            "principal-bundle rank",
            "c2 / instanton number k",
            "Wilson lines / parabolic reduction",
            "choice of leftover X^4 (K3 vs CP^2 vs T^4 vs other)",
            "H0 14D metric + reduction (not produced here)",
        ],
        "complete_baseline_rewritten": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print("A lock", rec["track_A_lock"], "B lock", rec["track_B_lock"], "combined", rec["combined_lock"])
    print("n_fits", a1["n_fits"])
    print("wrote", OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
