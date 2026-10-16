#!/usr/bin/env python3
"""
Weld-retirement test: APS survivors ↔ graph Aut-orbits / L-eigenspaces.

Question: is there a unique, parameter-free pairing forced by locked data?
No continuous coefficient. No nicest-match pick.
If L has no 3-dimensional object the APS triple must occupy, FAIL.
If more than one pairing of the right dimension works, FAIL (stays a weld).
MAP_NOT_LOCK is not renamed here.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from itertools import combinations
from typing import Any, Dict, List, Tuple

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.path.join(ARTIFACT_DIR, "flavor_graph_module.json")
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "weld_retirement.json")

APS_J1 = (0.5, 1.0, 1.5)
LOCKED_N_ETA = (3, 8, 15)
LOCKED_N_GEN = 3
MONODROMY = 24


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def orbit_catalog(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for space in graph["eigenspaces"]:
        for orb in space["aut_orbits"]:
            key = tuple(sorted(orb))
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "kind": "aut_orbit",
                    "fourier_k": list(key),
                    "dim": len(key),
                    "lambda_L": space["lambda_L"],
                }
            )
    return out


def eigenspace_catalog(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "kind": "L_eigenspace",
            "lambda_L": space["lambda_L"],
            "dim": space["dim"],
            "fourier_k": space["fourier_k"],
            "reducible": space["reducible"],
            "real_2_plane": space["real_2_plane"],
            "singlet": space["singlet"],
            "A4_triplet": space["A4_triplet"],
        }
        for space in graph["eigenspaces"]
    ]


def dim3_objects(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [x for x in items if x["dim"] == 3]


def doublet_singlet_unions(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Unions of one dim-2 object and one dim-1 object (total dim 3)."""
    ones = [x for x in items if x["dim"] == 1]
    twos = [x for x in items if x["dim"] == 2]
    pairs = []
    for a in twos:
        for b in ones:
            pairs.append(
                {
                    "dim2": a,
                    "dim1": b,
                    "total_dim": 3,
                }
            )
    return pairs


def main() -> int:
    graph = load_json(GRAPH_PATH)
    baseline = load_json(BASELINE_PATH)
    snap = graph["locked_snapshot"]["from_baseline"]
    proven = {row["id"]: row for row in baseline["status_classification"]["proven"]}

    spaces = eigenspace_catalog(graph)
    orbits = orbit_catalog(graph)

    L_dim3 = dim3_objects(spaces)
    orbit_dim3 = dim3_objects(orbits)
    L_21 = doublet_singlet_unions(spaces)
    orbit_21 = doublet_singlet_unions(orbits)

    n_eta_set = set(LOCKED_N_ETA)
    n_eta_is_aut_orbit = any(set(o["fourier_k"]) == n_eta_set for o in orbits)
    n_eta_is_eigenspace = any(set(s["fourier_k"]) == n_eta_set for s in spaces)

    unique_L_object = len(L_dim3) == 1
    unique_orbit_object = len(orbit_dim3) == 1
    unique_L_union = len(L_21) == 1
    unique_orbit_union = len(orbit_21) == 1

    forced = unique_L_object or unique_orbit_object or unique_L_union or unique_orbit_union
    # More than one channel, or zero dim-3 objects: not unique.
    n_channels = (
        len(L_dim3) + len(orbit_dim3) + len(L_21) + len(orbit_21)
    )
    unique_forced = forced and n_channels == 1

    if len(L_dim3) == 0 and len(orbit_dim3) == 0:
        verdict = "FAIL"
        reason = (
            "L has no 3-dimensional eigenspace and Aut has no 3-dimensional orbit "
            "that the APS triple must occupy."
        )
    elif not unique_forced:
        verdict = "FAIL"
        reason = (
            f"More than one dim-3 pairing exists (L 2+1 unions={len(L_21)}, "
            f"Aut-orbit 2+1 unions={len(orbit_21)}); not unique, stays a weld."
        )
    else:
        verdict = "PASS"
        reason = "Exactly one pairing is forced by locked data."

    functor = None
    map_not_lock_retired = False
    if verdict == "PASS":
        functor = "unique pairing recorded below"
        map_not_lock_retired = True

    rec = {
        "module": "weld_retirement",
        "question": (
            "unique parameter-free pairing {three APS modes} "
            "<-> {graph Aut-orbits / L-eigenspaces}"
        ),
        "continuous_knobs": 0,
        "locked_inputs": {
            "APS_j1": list(APS_J1),
            "N_gen": LOCKED_N_GEN,
            "n_eta": list(LOCKED_N_ETA),
            "monodromy_order": MONODROMY,
            "delta_eta_over_pi": [0.25, 2.0 / 3.0, 1.25],
            "r": snap["r"],
            "sigma_star": snap["sigma_star"],
            "graph_connection": graph["connection"],
            "lambda_L": graph["lambda_L"],
            "multiplicities": graph["multiplicities"],
        },
        "baseline_check": {
            "N_gen": proven["native_N_gen_3"]["value"],
            "n_eta": proven["n_eta_delta_eta"]["n_eta"],
            "r": proven["beta_residual_higher_res_computational_lock"]["value"],
            "theta13_deg": proven["residual_NLO_A4_flavor_high_scale"]["theta13_deg"],
            "untouched": True,
        },
        "L_eigenspace_dims": [s["dim"] for s in spaces],
        "Aut_orbit_dims": [o["dim"] for o in orbits],
        "n_L_objects_dim_3": len(L_dim3),
        "n_Aut_orbits_dim_3": len(orbit_dim3),
        "n_L_doublet_singlet_unions": len(L_21),
        "n_Aut_orbit_doublet_singlet_unions": len(orbit_21),
        "L_doublet_singlet_unions": [
            {
                "dim2_lambda_L": p["dim2"]["lambda_L"],
                "dim2_k": p["dim2"]["fourier_k"],
                "dim1_lambda_L": p["dim1"]["lambda_L"],
                "dim1_k": p["dim1"]["fourier_k"],
            }
            for p in L_21
        ],
        "n_eta_is_Aut_orbit": n_eta_is_aut_orbit,
        "n_eta_is_L_eigenspace": n_eta_is_eigenspace,
        "A4_triplet_in_L": graph["A4_triplet_in_L"],
        "unique_forced_pairing": unique_forced,
        "functor": functor,
        "verdict": verdict,
        "reason": reason,
        "MAP_NOT_LOCK": "stays" if not map_not_lock_retired else "retired_for_this_pairing_only",
        "CKM_welded": False,
        "r_touched": False,
        "theta13_touched": False,
        "complete_baseline_rewritten": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print("verdict", verdict)
    print("reason", reason)
    print("L_dim3", len(L_dim3), "orbit_dim3", len(orbit_dim3))
    print("L_2plus1", len(L_21), "orbit_2plus1", len(orbit_21))
    print("MAP_NOT_LOCK", rec["MAP_NOT_LOCK"])
    print("wrote", OUT_PATH)
    return 0 if rec["continuous_knobs"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
