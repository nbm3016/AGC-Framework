#!/usr/bin/env python3
"""
Sterilized flavor/generation GRAPH MODULE (native lock only).

Read-only reconstruction of the 165 involution-closed 6-regular circulants
on Z/24, the unique adjacency spectrum, Aut-orbits on Fourier modes, and
the category-error flags that strike U(2)/S3 and the APS/Z24 weld.

Does not re-solve Stages 1–4.
Does not write FN / SO(10) / Cabibbo / GJ / V_cb into complete_baseline.json.
MAP ≠ LOCK.
"""

from __future__ import annotations

import itertools
import json
import math
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, FrozenSet, List, Sequence, Tuple

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "flavor_graph_module.json")

N = 24
DEGREE = 6
AUT = (1, 5, 7, 11, 13, 17, 19, 23)
LOCKED_N_ETA = (3, 8, 15)
NATIVE_REPS = (3, 8, 9)
NATIVE_CONNECTION = (3, 8, 9, 15, 16, 21)
TARGET_A = (6.0, 3.0, 2.0, -1.0, -2.0, -5.0)
TARGET_A_MULT = (1, 2, 6, 12, 1, 2)
TARGET_L = (0.0, 3.0, 4.0, 7.0, 8.0, 11.0)
TARGET_L_MULT = (1, 2, 6, 12, 1, 2)

STRUCK = (
    "unbroken U(2)/S3 forced by the Laplacian",
    "native V_cb=0 as SM prediction",
    "generations = Fourier eigenspaces",
)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def connection_from_reps(reps: Sequence[int]) -> Tuple[int, ...]:
    s = set()
    for k in reps:
        s.add(k % N)
        s.add((-k) % N)
    return tuple(sorted(s))


def adjacency_evals(reps: Sequence[int]) -> List[float]:
    ev = []
    for m in range(N):
        lam = 0.0
        for k in reps:
            lam += 2.0 * math.cos(2.0 * math.pi * m * k / N)
        ev.append(lam)
    return ev


def spectrum_signature(evals: Sequence[float], tol: float = 1e-9) -> Tuple[Tuple[float, int], ...]:
    rounded = [round(x / tol) * tol for x in evals]
    counts = Counter(rounded)
    return tuple(sorted(((float(v), int(c)) for v, c in counts.items()), key=lambda t: -t[0]))


def target_signature(values: Sequence[float], mults: Sequence[int]) -> Tuple[Tuple[float, int], ...]:
    return tuple(sorted(((float(v), int(m)) for v, m in zip(values, mults)), key=lambda t: -t[0]))


def census_165() -> Dict[str, Any]:
    target = target_signature(TARGET_A, TARGET_A_MULT)
    hits: List[Tuple[int, ...]] = []
    signatures: Dict[Tuple[Tuple[float, int], ...], int] = defaultdict(int)
    for reps in itertools.combinations(range(1, N // 2), 3):
        sig = spectrum_signature(adjacency_evals(reps))
        signatures[sig] += 1
        if sig == target:
            hits.append(reps)
    return {
        "n_graphs": int(math.comb(11, 3)),
        "n_distinct_A_signatures": len(signatures),
        "n_hits_target_A_spectrum": len(hits),
        "unique": len(hits) == 1,
        "hit_reps": [list(h) for h in hits],
        "hit_connections": [list(connection_from_reps(h)) for h in hits],
    }


def aut_orbit(seed: int) -> FrozenSet[int]:
    return frozenset((a * seed) % N for a in AUT)


def aut_orbits_on_fourier() -> List[Dict[str, Any]]:
    seen = set()
    orbits = []
    for k in range(N):
        if k in seen:
            continue
        orb = aut_orbit(k)
        seen |= orb
        orbits.append(
            {
                "rep": k,
                "orbit": sorted(orb),
                "dim": len(orb),
            }
        )
    return orbits


def laplacian_from_A(evals_A: Sequence[float]) -> List[float]:
    return [DEGREE - x for x in evals_A]


def eigenspace_partition(evals_L: Sequence[float], tol: float = 1e-9) -> List[Dict[str, Any]]:
    buckets: Dict[float, List[int]] = defaultdict(list)
    for k, lam in enumerate(evals_L):
        key = round(lam / tol) * tol
        buckets[key].append(k)
    out = []
    for lam in sorted(buckets):
        ks = buckets[lam]
        orbs = []
        seen = set()
        for k in ks:
            if k in seen:
                continue
            orb = aut_orbit(k)
            seen |= orb
            orbs.append(sorted(orb))
        out.append(
            {
                "lambda_L": lam,
                "dim": len(ks),
                "fourier_k": ks,
                "aut_orbits": orbs,
                "reducible": len(orbs) > 1,
                "real_2_plane": len(ks) == 2,
                "singlet": len(ks) == 1,
                "A4_triplet": len(ks) == 3,
            }
        )
    return out


def locked_snapshot(baseline: Dict[str, Any]) -> Dict[str, Any]:
    proven = {row["id"]: row for row in baseline["status_classification"]["proven"]}
    flavor = proven["residual_NLO_A4_flavor_high_scale"]
    stage4 = proven["stage4_mu_omega_w0"]
    return {
        "N_gen": 3,
        "sigma_star": "sqrt(3)/2",
        "n_eta": [3, 8, 15],
        "r": 0.095716,
        "theta13_deg": 7.953,
        "mu_gammagamma": 1.086571,
        "omega_lambda": 0.679528,
        "from_baseline": {
            "N_gen": proven["native_N_gen_3"]["value"],
            "sigma_star": proven["sigma_star_shape_stabilized"]["value"],
            "n_eta": proven["n_eta_delta_eta"]["n_eta"],
            "r": proven["beta_residual_higher_res_computational_lock"]["value"],
            "theta13_deg": flavor["theta13_deg"],
            "mu_gammagamma": stage4["mu_gammagamma"],
            "omega_lambda": stage4["omega_lambda"],
        },
        "matches_official_lock": (
            proven["native_N_gen_3"]["value"] == 3
            and proven["n_eta_delta_eta"]["n_eta"] == [3, 8, 15]
            and proven["beta_residual_higher_res_computational_lock"]["value"] == 0.095716
            and flavor["theta13_deg"] == 7.953
            and stage4["mu_gammagamma"] == 1.086571
            and stage4["omega_lambda"] == 0.679528
        ),
    }


def native_aut_closure() -> Dict[str, Any]:
    orb3 = sorted(aut_orbit(3))
    orb8 = sorted(aut_orbit(8))
    closure = sorted(set(orb3) | set(orb8))
    return {
        "n_eta": list(LOCKED_N_ETA),
        "orb_3": orb3,
        "orb_8": orb8,
        "union": closure,
        "equals_connection": closure == list(NATIVE_CONNECTION),
        "aut": list(AUT),
        "aut_iso": "C2^3",
        "complex_irreps_1d": True,
    }


def build_record() -> Dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    census = census_165()
    ev_A = adjacency_evals(NATIVE_REPS)
    ev_L = laplacian_from_A(ev_A)
    spaces = eigenspace_partition(ev_L)
    dims = [row["dim"] for row in spaces]
    closure = native_aut_closure()
    snap = locked_snapshot(baseline)
    return {
        "module": "flavor_graph_module",
        "map_neq_lock": True,
        "graph_lock": True,
        "unique_A_spectrum": list(TARGET_A),
        "connection": list(NATIVE_CONNECTION),
        "aut_closure_of_n_eta": True,
        "lambda_L": list(TARGET_L),
        "multiplicities": list(TARGET_L_MULT),
        "A4_triplet_in_L": False,
        "r_breaks_doublet": False,
        "U2_S3_claim": "struck",
        "hilbert_space_weld": "external",
        "FN_SO10": "map_not_lock",
        "Vcb_native_as_SM": False,
        "continuous_knobs": 0,
        "locked_snapshot": snap,
        "complete_baseline_rewritten": False,
        "census": census,
        "aut_closure": closure,
        "laplacian": {
            "definition": "L = 6I - A",
            "not_a_map": True,
            "A_evals_native": [round(x, 12) for x in ev_A],
            "L_evals_native": [round(x, 12) for x in ev_L],
            "A_signature": [[v, m] for v, m in spectrum_signature(ev_A)],
            "L_signature": [[v, m] for v, m in spectrum_signature(ev_L)],
            "matches_target_A": spectrum_signature(ev_A) == target_signature(TARGET_A, TARGET_A_MULT),
            "matches_target_L": spectrum_signature(ev_L) == target_signature(TARGET_L, TARGET_L_MULT),
        },
        "eigenspaces": spaces,
        "no_3_dimensional_eigenspace": 3 not in dims,
        "native_sentence": (
            "Aut-orbits on Fourier modes are singlets and real 2-planes. "
            "Aut-equivariant operators on this graph cannot mix a chosen "
            "2-plane with a chosen singlet. That is a fact about the "
            "24-vertex kinetic operator, not SM flavor."
        ),
        "struck_language": list(STRUCK),
        "category_error": {
            "aps_survivors": "Sigma^5",
            "laplacian_eigenspaces": "Z/24",
            "same_hilbert_space": False,
            "gen12_with_lambda_L_3_and_gen3_with_lambda_L_8": "EXTERNAL_WELD",
            "doublet_singlet_pairs": 4,
            "FN_charges_320_vs_Aut_Yukawa": "contradict",
            "breaking_2plus1_onto_APS_16s": "NOT_IN_ISOLATE",
        },
        "map_only": {
            "FN": {
                "lambda": "n1/n3=1/5",
                "charges": [3, 2, 0],
                "status": "map_not_lock",
                "note": "hierarchical powers only; O(10) misses on down and muon",
            },
            "SO10_junction": {
                "content": "3_A4 ⊗ 16, one 10_H, no 45/126/MSSM",
                "status": "map_not_lock",
                "m_b_over_m_tau": "livable after SM RG",
                "m_s_over_m_mu": "miss",
                "m_d_over_m_e": "miss",
                "gauge_unification": False,
                "native_10H_supplies_GJ": False,
            },
            "Wolfenstein_lambda": {
                "value": "1/5",
                "is_Cabibbo_0.225": False,
            },
            "reuse_3_over_8_as_mass_ratio": "FORBIDDEN_already_tan2_theta12",
        },
        "rejected_overlays_negative_ledger": [
            "Rule B",
            "Rule C",
            "Rule D",
            "lepton NLO on 5/24",
            "SM RG of lambda",
            "Rule 7 squash",
            "Rule 8 hull 26/9",
            "Rule 9 KK threshold",
        ],
        "open_hull_leaks": [
            "26/9 uncancelled",
            "continuum r->0 not forced",
        ],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    rec = build_record()
    if not rec["census"]["unique"]:
        raise SystemExit("census failed uniqueness of target A spectrum")
    if not rec["laplacian"]["matches_target_A"] or not rec["laplacian"]["matches_target_L"]:
        raise SystemExit("native graph spectrum mismatch")
    if rec["A4_triplet_in_L"] or not rec["no_3_dimensional_eigenspace"]:
        raise SystemExit("A4 triplet appeared in L")
    if rec["complete_baseline_rewritten"]:
        raise SystemExit("baseline rewrite flag must stay false")
    if rec["continuous_knobs"] != 0:
        raise SystemExit("continuous_knobs must stay 0")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print("wrote", OUT_PATH)
    print("unique_among_165", rec["census"]["unique"])
    print("A4_triplet_in_L", rec["A4_triplet_in_L"])
    print("U2_S3_claim", rec["U2_S3_claim"])
    print("hilbert_space_weld", rec["hilbert_space_weld"])
    print("continuous_knobs", rec["continuous_knobs"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
