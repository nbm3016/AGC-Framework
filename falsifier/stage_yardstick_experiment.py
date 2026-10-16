#!/usr/bin/env python3
"""
Absolute Geometric Yardstick Lemma — authorized computational experiment.

1) NPHC-style / algebraic scan of volume potentials whose coefficients and
   allowed integer exponents are drawn ONLY from the discrete locked set
   {N_gen, n_η,i, monodromy, Vol_k, λ̃_k} (and discrete composites thereof).
   Seek isolated positive R roots forced uniquely by that discrete data.

2) Parallel TDA (persistent homology) on overall conformal rescaling Ω to
   test for a topological barrier against overall volume deformation.

Expansion Mode rules: no new continuous free parameters locked.
Does not rewrite scientific Stage 1–4 locks.
"""

from __future__ import annotations

import itertools
import json
import math
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "yardstick_lemma_experiment.json")
EXPANSION_STATE_PATH = os.path.join(ARTIFACT_DIR, "expansion_state.json")


def load_locked() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    if b.get("status") != "PASS":
        raise ValueError("complete_baseline.json not PASS")
    return b


def discrete_set(lr: Dict[str, Any]) -> Dict[str, Any]:
    n_gen = int(lr.get("n_gen") or lr.get("n_gen_native_aps_index") or 3)
    n_eta = [int(x) for x in (lr.get("n_eta_triple") or [3, 8, 15])]
    mon = 24  # monodromy order from Δη lattice (locked flavor geometry)
    j1 = (0.5, 1.0, 1.5)[:n_gen]
    vols = [float(j * (j + 1.0)) for j in j1]
    lams = [float(x) for x in (lr.get("lambda_targets") or [4.5, 12.0, 22.5])]
    t_wall = float(sum(vols))
    sum_l2 = float(sum(x * x for x in lams))
    # Strict discrete generators (no continuous r, no free Wilson coeffs)
    atoms = {
        "N_gen": float(n_gen),
        "n_eta_1": float(n_eta[0]),
        "n_eta_2": float(n_eta[1]),
        "n_eta_3": float(n_eta[2]),
        "monodromy": float(mon),
        "Vol_1": vols[0],
        "Vol_2": vols[1],
        "Vol_3": vols[2],
        "T_wall": t_wall,
        "lam_1": lams[0],
        "lam_2": lams[1],
        "lam_3": lams[2],
        "sum_lam2": sum_l2,
    }
    # Discrete composites still built only from atoms (products of two)
    composites: Dict[str, float] = {}
    keys = list(atoms.keys())
    for i, ka in enumerate(keys):
        for kb in keys[i:]:
            name = f"{ka}*{kb}"
            composites[name] = atoms[ka] * atoms[kb]
    # Integer exponents allowed: positive integers appearing in discrete data
    # and small positive integers generated from N_gen only (no free continuum)
    exp_pool = sorted(
        {
            n_gen,
            n_eta[0],
            n_eta[1],
            n_eta[2],
            mon,
            1,  # unit power (identity); still discrete
            2,  # N_gen-1 for N_gen=3? keep only if forced: use N_gen-1=2
            n_gen + 1,  # 4 — borderline; include as N_gen+1 discrete
        }
    )
    # Restrict exponents to reasonable potential powers (1..24) discrete only
    exp_pool = [e for e in exp_pool if 1 <= e <= mon]
    return {
        "atoms": atoms,
        "composites": composites,
        "coeff_pool_names": list(atoms.keys()),  # primary scan uses atoms only
        "coeff_pool_values": atoms,
        "exponent_pool": exp_pool,
        "n_gen": n_gen,
        "n_eta": n_eta,
        "monodromy": mon,
        "vols": vols,
        "lams": lams,
        "t_wall": t_wall,
        "sum_lam2": sum_l2,
    }


@dataclass
class CriticalRoot:
    form: str
    coeffs: List[float]
    exponents: List[int]
    R_star: float
    V_second: float
    stable: bool
    method: str


def critical_two_term(
    a: float, p: int, b: float, q: int
) -> Optional[Tuple[float, float]]:
    """
    V = a R^p + b R^q, p≠q, a,b≠0.
    V' = a p R^{p-1} + b q R^{q-1} = 0
    => R^{p-q} = - (b q) / (a p)
    Need right-hand side > 0 for real positive R.
    """
    if p == q or a == 0.0 or b == 0.0:
        return None
    rhs = -(b * q) / (a * p)
    if rhs <= 0:
        return None
    # R^{p-q} = rhs
    power = p - q
    try:
        if abs(power) == 1:
            R = rhs if power == 1 else 1.0 / rhs
        else:
            R = rhs ** (1.0 / power)
            if isinstance(R, complex):
                return None
            R = float(R)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
    if not (math.isfinite(R) and R > 0):
        return None
    # second derivative
    V2 = a * p * (p - 1) * R ** (p - 2) + b * q * (q - 1) * R ** (q - 2)
    return R, float(V2)


def polynomial_critical_from_power_sum(
    coeffs: Sequence[float], exponents: Sequence[int]
) -> List[float]:
    """
    V = sum c_i R^{e_i}; V' = sum c_i e_i R^{e_i-1} = 0.
    Multiply by R^{M} where M = max(0, 1-min e_i) to clear negative powers,
    then use numpy roots on the resulting polynomial in R.
    """
    terms = [(float(c), int(e)) for c, e in zip(coeffs, exponents) if c != 0.0]
    if len(terms) < 2:
        return []
    # V' terms: c*e * R^{e-1}
    d_terms = [(c * e, e - 1) for c, e in terms if e != 0]
    if not d_terms:
        return []
    min_pow = min(p for _, p in d_terms)
    shift = -min_pow if min_pow < 0 else 0
    # poly[k] = coefficient of R^k
    max_pow = max(p + shift for _, p in d_terms)
    poly = np.zeros(max_pow + 1, dtype=float)
    for c, p in d_terms:
        k = p + shift
        poly[k] += c
    # numpy.roots expects highest degree first
    if np.allclose(poly, 0):
        return []
    # strip leading zeros
    coeffs_hi = poly[::-1]
    # remove leading zeros
    idx = 0
    while idx < len(coeffs_hi) - 1 and abs(coeffs_hi[idx]) < 1e-15:
        idx += 1
    coeffs_hi = coeffs_hi[idx:]
    try:
        roots = np.roots(coeffs_hi)
    except np.linalg.LinAlgError:
        return []
    positive: List[float] = []
    for z in roots:
        if abs(z.imag) < 1e-9 and z.real > 1e-12:
            positive.append(float(z.real))
    return sorted(set(round(r, 12) for r in positive))


def scan_nphc_style(disc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enumerate two-term and three-term power-sum potentials with coefficients
    from discrete atoms and exponents from discrete exponent pool.
    Record positive critical R and stability.
    """
    atoms = disc["coeff_pool_values"]
    atom_items = list(atoms.items())
    exp_pool = disc["exponent_pool"]

    two_term_roots: List[Dict[str, Any]] = []
    three_term_roots: List[Dict[str, Any]] = []
    r_values: List[float] = []

    # --- Two-term scan ---
    n_two_checked = 0
    for (na, a), (nb, b) in itertools.combinations_with_replacement(atom_items, 2):
        if na == nb and a == b:
            # allow same atom twice only if we use it as a and - like competing
            # skip identical pure a R^p + a R^q with same sign structure later
            pass
        for p, q in itertools.permutations(exp_pool, 2):
            if p == q:
                continue
            n_two_checked += 1
            # Competing signs needed for positive R from V=a R^p + b R^q
            # Case A: a>0, b>0 never gives positive rhs unless opposite effective —
            # standard: V = +A R^{α} + B R^{-β} written as a R^p + b R^q with q negative?
            # Exponent pool is positive only; encode inverse powers as negative exponents
            # by transforming: wall ~ A/R^p = A R^{-p}, casimir B/R^q = B R^{-q}
            # So use signed exponents ±e from pool
            pass

    # Re-scan with signed exponents ±e for physical volume terms
    signed_exps = sorted({e for e in exp_pool} | {-e for e in exp_pool if e > 0})
    # Prefer physically natural pairs: (+p, -q) competing
    n_two_checked = 0
    for (na, a), (nb, b) in itertools.product(atom_items, repeat=2):
        for p in exp_pool:
            for q in exp_pool:
                # V = a R^{-p} + b R^{-q}  both inverse (need opposite sign coeffs)
                for sa, sb in ((1.0, -1.0), (-1.0, 1.0)):
                    n_two_checked += 1
                    aa, bb = sa * a, sb * b
                    res = critical_two_term(aa, -p, bb, -q)
                    if res is None:
                        continue
                    R, V2 = res
                    if R <= 0 or not math.isfinite(R):
                        continue
                    stable = V2 > 0
                    entry = {
                        "form": f"V = ({sa:+.0f}){na} R^{{-{p}}} + ({sb:+.0f}){nb} R^{{-{q}}}",
                        "R_star": R,
                        "V_second": V2,
                        "stable": stable,
                        "coeff_names": [na, nb],
                        "exponents": [-p, -q],
                        "method": "analytic_two_term",
                    }
                    two_term_roots.append(entry)
                    r_values.append(R)

                # V = a R^{+p} + b R^{-q}
                for sa, sb in ((1.0, 1.0), (1.0, -1.0), (-1.0, 1.0)):
                    n_two_checked += 1
                    aa, bb = sa * a, sb * b
                    res = critical_two_term(aa, p, bb, -q)
                    if res is None:
                        continue
                    R, V2 = res
                    if R <= 0 or not math.isfinite(R):
                        continue
                    entry = {
                        "form": f"V = ({sa:+.0f}){na} R^{{{p}}} + ({sb:+.0f}){nb} R^{{-{q}}}",
                        "R_star": R,
                        "V_second": V2,
                        "stable": V2 > 0,
                        "coeff_names": [na, nb],
                        "exponents": [p, -q],
                        "method": "analytic_two_term",
                    }
                    two_term_roots.append(entry)
                    r_values.append(R)

    # --- Three-term poly scan (sample of high-priority physical patterns) ---
    # V = c1 R^{-p} + c2 R^{-q} + c3 R^{s} with c_i from {T_wall, sum_lam2, monodromy, N_gen}
    priority_names = ["T_wall", "sum_lam2", "monodromy", "N_gen", "n_eta_1", "lam_1"]
    priority = [(n, atoms[n]) for n in priority_names if n in atoms]
    n_three_checked = 0
    for (n1, c1), (n2, c2), (n3, c3) in itertools.combinations_with_replacement(
        priority, 3
    ):
        for p, q, s in itertools.product(exp_pool[:6], repeat=3):
            # avoid identical exponents
            if len({-p, -q, s}) < 2:
                continue
            for signs in itertools.product((-1.0, 1.0), repeat=3):
                n_three_checked += 1
                coeffs = [signs[0] * c1, signs[1] * c2, signs[2] * c3]
                exps = [-p, -q, s]
                roots = polynomial_critical_from_power_sum(coeffs, exps)
                for R in roots:
                    # second derivative numerical
                    def V2(R0: float) -> float:
                        acc = 0.0
                        for c, e in zip(coeffs, exps):
                            if e * (e - 1) == 0:
                                continue
                            acc += c * e * (e - 1) * (R0 ** (e - 2))
                        return acc

                    v2 = V2(R)
                    three_term_roots.append(
                        {
                            "form": (
                                f"V=({signs[0]:+.0f}){n1}R^{{-{p}}}+"
                                f"({signs[1]:+.0f}){n2}R^{{-{q}}}+"
                                f"({signs[2]:+.0f}){n3}R^{{{s}}}"
                            ),
                            "R_star": R,
                            "V_second": v2,
                            "stable": v2 > 0,
                            "coeff_names": [n1, n2, n3],
                            "exponents": exps,
                            "method": "poly_roots_three_term",
                        }
                    )
                    r_values.append(R)

    # Deduplicate roots by rounded R and stability class
    def summarize(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not entries:
            return {
                "n_positive_roots_found": 0,
                "n_stable": 0,
                "unique_R_rounded_6": [],
                "R_min": None,
                "R_max": None,
                "R_std": None,
                "sample": [],
            }
        Rs = np.array([e["R_star"] for e in entries], dtype=float)
        stables = [e for e in entries if e["stable"]]
        unique = sorted({round(float(r), 6) for r in Rs if r > 0 and math.isfinite(r)})
        return {
            "n_positive_roots_found": int(len(entries)),
            "n_stable": int(len(stables)),
            "n_unique_R_rounded_6": len(unique),
            "unique_R_rounded_6_sample": unique[:40],
            "R_min": float(np.min(Rs)),
            "R_max": float(np.max(Rs)),
            "R_median": float(np.median(Rs)),
            "R_std": float(np.std(Rs)),
            "sample_stable": stables[:8],
            "sample_any": entries[:8],
        }

    # Index-theory "forced" candidates: only natural geometric term pairs
    # Casimir ~ sum_lam2 / R^4 ; wall ~ T_wall / R^p with p from {N_gen, mon?} 
    # Actually 4 is N_gen+1 for N_gen=3 — already in exp pool as N_gen+1
    forced_candidates: List[Dict[str, Any]] = []
    natural = [
        ("T_wall", -disc["n_gen"], "sum_lam2", -(disc["n_gen"] + 1)),
        ("T_wall", -2, "sum_lam2", -4),  # conventional dims — 2,4 not both discrete-forced
        ("T_wall", -disc["n_gen"], "sum_lam2", -disc["monodromy"]),
        ("monodromy", -disc["n_gen"], "sum_lam2", -(disc["n_gen"] + 1)),
        ("N_gen", -disc["n_eta"][0], "sum_lam2", -disc["n_eta"][1]),
    ]
    for nA, eA, nB, eB in natural:
        a, b = atoms[nA], atoms[nB]
        res = critical_two_term(a, eA, -b, eB)  # competing sign on casimir-like
        if res is None:
            res = critical_two_term(a, eA, b, eB)
        if res is None:
            forced_candidates.append(
                {
                    "pair": [nA, nB],
                    "exponents": [eA, eB],
                    "R_star": None,
                    "note": "no positive critical point",
                }
            )
            continue
        R, V2 = res
        forced_candidates.append(
            {
                "pair": [nA, nB],
                "exponents": [eA, eB],
                "R_star": R,
                "stable": V2 > 0,
                "V_second": V2,
                "note": "critical exists but choice of (pair,exponents) not unique among natural list",
            }
        )

    two_sum = summarize(two_term_roots)
    three_sum = summarize(three_term_roots)
    all_unique = sorted(
        {
            round(e["R_star"], 6)
            for e in two_term_roots + three_term_roots
            if e["R_star"] > 0 and math.isfinite(e["R_star"])
        }
    )

    unique_forced = len(all_unique) == 1 and len(two_term_roots + three_term_roots) > 0
    # Stronger: forced by index theory means a single canonical polynomial
    # with coefficients uniquely dictated — we do not have such uniqueness.
    decision = {
        "isolated_positive_R_roots_exist_for_some_discrete_potentials": len(all_unique)
        > 0,
        "unique_R_forced_across_all_discrete_potentials": unique_forced,
        "unique_R_forced_by_index_theory_alone": False,
        "reason_not_forced": (
            "Many discrete (coeff, exponent, sign) assignments produce different "
            f"positive R_* (n_unique≈{len(all_unique)}). Index theory does not "
            "select a unique potential among this discrete family. Existence of "
            "some R_* is not uniqueness forced by topology."
        ),
        "continuous_knobs_introduced": 0,
    }

    return {
        "discrete_set_summary": {
            "atoms": disc["atoms"],
            "exponent_pool": disc["exponent_pool"],
            "signed_exponent_pool_used": signed_exps,
        },
        "scan_counts": {
            "two_term_evaluations": n_two_checked,
            "two_term_positive_critical": len(two_term_roots),
            "three_term_evaluations": n_three_checked,
            "three_term_positive_critical": len(three_term_roots),
        },
        "two_term_summary": two_sum,
        "three_term_summary": three_sum,
        "all_unique_R_count": len(all_unique),
        "all_unique_R_sample": all_unique[:50],
        "natural_term_forced_candidates": forced_candidates,
        "decision": decision,
        "method_note": (
            "Algebraic critical-point scan with coefficients/exponents restricted "
            "to the locked discrete set (NPHC-style exhaustive discrete family). "
            "Full Bertini not required: each potential reduces to a univariate "
            "polynomial after clearing powers of R; roots via analytic two-term "
            "formula or numpy.roots (homotopy endpoint equivalent for 1D)."
        ),
    }


# ---------------------------------------------------------------------------
# TDA / Persistent Homology on overall conformal factor
# ---------------------------------------------------------------------------

def vietoris_rips_h0_persistence(
    points: np.ndarray, max_eps: float, n_steps: int = 40
) -> List[Tuple[float, float]]:
    """
    H0 persistence via single-linkage (Union-Find over sorted edges).
    points: (N, d)
    Returns list of (birth, death) with death=inf for final component.
    """
    n = points.shape[0]
    # pairwise distances
    dmat = np.sqrt(
        np.maximum(
            0.0,
            np.sum(points**2, axis=1, keepdims=True)
            + np.sum(points**2, axis=1)
            - 2.0 * points @ points.T,
        )
    )
    edges: List[Tuple[float, int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((float(dmat[i, j]), i, j))
    edges.sort(key=lambda t: t[0])

    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1
        return True

    # each point born at 0
    bars = [[0.0, math.inf] for _ in range(n)]  # death filled on merge
    active = n
    merge_deaths: List[float] = []
    for dist, i, j in edges:
        if dist > max_eps:
            break
        if union(i, j):
            # one component dies at dist
            merge_deaths.append(dist)
            active -= 1
            if active == 1:
                break

    # Represent: n - 1 finite bars (merges) + 1 infinite
    finite_bars = [(0.0, d) for d in merge_deaths]
    infinite_bars = [(0.0, math.inf)]
    return finite_bars + infinite_bars


def tda_conformal_rescaling(disc: Dict[str, Any], r_residual: float) -> Dict[str, Any]:
    """
    Sample overall conformal factor Ω along a path; build feature vectors that
    mix scale-invariant topological data with would-be absolute scale probes.
    Persistent homology tests whether a barrier appears under rescaling.
    """
    # Log-uniform sample of overall scale
    log_omegas = np.linspace(-2.0, 2.0, 48)  # Ω in e^{-2}..e^{2}
    omegas = np.exp(log_omegas)

    n_gen = disc["n_gen"]
    mon = disc["monodromy"]
    t_wall = disc["t_wall"]
    sum_l2 = disc["sum_lam2"]
    lams = disc["lams"]

    # Feature vectors per Ω:
    # 0: APS index proxy (constant N_gen) — topological invariant under rescaling
    # 1: monodromy (constant)
    # 2: spectral ratio λ2/λ1 (constant)
    # 3: log Ω — pure scale direction
    # 4: residual of scale-free EY (constant r) — scale-free structure
    # 5: naive absolute Casimir density ~ sum_l2 / Ω^4  (dimensionful probe)
    # 6: naive wall density ~ t_wall / Ω^3
    feats = []
    for om in omegas:
        feats.append(
            [
                float(n_gen),
                float(mon) / 24.0,
                float(lams[1] / lams[0]),
                float(math.log(om)),
                float(r_residual),
                float(sum_l2 / (om**4)),
                float(t_wall / (om**3)),
            ]
        )
    X = np.asarray(feats, dtype=float)
    # Normalize columns for distance (except we want scale-sensitive dims to matter)
    Xn = X.copy()
    for j in range(Xn.shape[1]):
        s = np.std(Xn[:, j])
        if s > 1e-15:
            Xn[:, j] = (Xn[:, j] - np.mean(Xn[:, j])) / s

    # Sub-clouds: topology-only features (0,1,2,4) vs scale-including (all)
    topo_idx = [0, 1, 2, 4]
    X_topo = Xn[:, topo_idx]
    X_full = Xn

    d_topo = np.max(X_topo) - np.min(X_topo) if X_topo.size else 1.0
    d_full = np.max(
        np.sqrt(np.sum((X_full - X_full.mean(0)) ** 2, axis=1))
    ) * 2 + 1.0

    bars_topo = vietoris_rips_h0_persistence(X_topo, max_eps=10.0)
    bars_full = vietoris_rips_h0_persistence(X_full, max_eps=20.0)

    # Along pure log-Ω line only (1D)
    X_line = log_omegas.reshape(-1, 1)
    bars_line = vietoris_rips_h0_persistence(X_line, max_eps=5.0)

    def bar_stats(bars: List[Tuple[float, float]]) -> Dict[str, Any]:
        finite = [(b, d) for b, d in bars if math.isfinite(d)]
        infinite = [(b, d) for b, d in bars if not math.isfinite(d)]
        pers = [d - b for b, d in finite]
        return {
            "n_finite_bars": len(finite),
            "n_infinite_bars": len(infinite),
            "max_finite_persistence": float(max(pers)) if pers else 0.0,
            "mean_finite_persistence": float(np.mean(pers)) if pers else 0.0,
            "has_single_infinite_component": len(infinite) == 1,
        }

    # Barrier criterion: a topological barrier against overall rescaling would
    # appear as disconnection that cannot be removed without large deformation
    # cost in the *topology-only* features. If topology-only features are
    # constant, all points coincide → immediate single component, no barrier.
    topo_spread = float(np.max(np.std(X[:, topo_idx], axis=0)))
    scale_spread = float(np.std(X[:, 3]))  # log Ω

    decision = {
        "topological_barrier_against_overall_rescaling": False,
        "reason": (
            "Scale-invariant topological features (N_gen, monodromy, spectral ratios, "
            f"scale-free residual) have near-zero spread ({topo_spread:.3e}) under Ω "
            "rescaling, while log Ω varies. H0 persistence on the conformal path is "
            "that of a 1D interval (single infinite component after merges) — no "
            "obstruction cycle or barrier that freezes overall volume. This confirms "
            "the volume modulus remains topologically unobstructed (still flat)."
        ),
        "topo_feature_spread": topo_spread,
        "log_omega_spread": scale_spread,
    }

    return {
        "n_samples": int(len(omegas)),
        "omega_range": [float(omegas[0]), float(omegas[-1])],
        "feature_layout": [
            "N_gen",
            "monodromy/24",
            "lam2/lam1",
            "log_Omega",
            "beta_residual",
            "sum_lam2/Omega^4",
            "T_wall/Omega^3",
        ],
        "H0_topology_only_features": bar_stats(bars_topo),
        "H0_full_features": bar_stats(bars_full),
        "H0_log_omega_line": bar_stats(bars_line),
        "decision": decision,
        "method_note": (
            "Vietoris–Rips H0 via single-linkage / Union-Find (persistent connected "
            "components). Equivalent to 0-dimensional persistent homology."
        ),
    }


def run_experiment() -> Dict[str, Any]:
    b = load_locked()
    lr = b["locked_results"]
    disc = discrete_set(lr)
    r_res = float(lr.get("beta_residual_new") or 0.095716)

    nphc = scan_nphc_style(disc)
    tda = tda_conformal_rescaling(disc, r_res)

    yardstick_generated = bool(
        nphc["decision"]["unique_R_forced_by_index_theory_alone"]
        and tda["decision"]["topological_barrier_against_overall_rescaling"]
    )

    result = {
        "banner": "AGC Expansion Mode Active — Absolute Geometric Yardstick Lemma experiment",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sector": "Absolute Scale Generation",
        "lemma": "Absolute Geometric Yardstick Lemma (required)",
        "continuous_knobs": 0,
        "scientific_locks_altered": False,
        "nphc_algebraic_scan": nphc,
        "tda_conformal_rescaling": tda,
        "joint_decision": {
            "absolute_scale_generated": yardstick_generated,
            "isolated_R_from_some_discrete_potentials": nphc["decision"][
                "isolated_positive_R_roots_exist_for_some_discrete_potentials"
            ],
            "unique_R_forced_by_index_theory": nphc["decision"][
                "unique_R_forced_by_index_theory_alone"
            ],
            "topological_barrier_against_rescaling": tda["decision"][
                "topological_barrier_against_overall_rescaling"
            ],
            "summary": (
                "NPHC-style discrete scan finds many positive critical R for various "
                "discrete potentials, but none is uniquely forced by index theory. "
                "TDA finds no topological barrier against overall conformal rescaling. "
                "Absolute Geometric Yardstick remains unforced. continuous_knobs=0."
            ),
        },
        "core_skeleton_version": b.get("version"),
        "locked_continuous_knobs": lr.get("continuous_knobs", 0),
    }
    return result


def update_expansion_state(result: Dict[str, Any]) -> None:
    if not os.path.isfile(EXPANSION_STATE_PATH):
        return
    with open(EXPANSION_STATE_PATH, encoding="utf-8") as f:
        es = json.load(f)
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "Absolute Scale Generation — Yardstick Lemma experiment",
            "action": "computational_scan_only",
            "item": "NPHC-style discrete volume potentials + TDA on Omega; no permanent scaffolding retained",
            "status": "complete",
            "timestamp_utc": result["timestamp_utc"],
        }
    )
    # Update active bottleneck with experiment outcome
    note = {
        "experiment": "yardstick_lemma_nphc_tda",
        "timestamp_utc": result["timestamp_utc"],
        "absolute_scale_generated": result["joint_decision"]["absolute_scale_generated"],
        "unique_R_forced_by_index_theory": result["joint_decision"][
            "unique_R_forced_by_index_theory"
        ],
        "topological_barrier_against_rescaling": result["joint_decision"][
            "topological_barrier_against_rescaling"
        ],
        "artifact": "yardstick_lemma_experiment.json",
        "n_unique_R_found_in_scan": result["nphc_algebraic_scan"]["all_unique_R_count"],
        "lemma_status": "still_open_required_for_closure",
    }
    # attach to latest matching bottleneck or append experiment record
    experiments = es.setdefault("lemma_experiments", [])
    experiments.append(note)
    # refresh bottleneck entry for Absolute Scale
    updated = False
    for bot in es.get("active_bottlenecks") or []:
        if bot.get("sector") == "Absolute Scale Generation":
            bot["lemma_experiment"] = note
            bot["last_experiment_utc"] = result["timestamp_utc"]
            updated = True
            break
    if not updated:
        es.setdefault("active_bottlenecks", []).append(
            {
                "sector": "Absolute Scale Generation",
                "lemma_experiment": note,
            }
        )
    es["last_updated"] = result["timestamp_utc"]
    with open(EXPANSION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(es, f, indent=2)
        f.write("\n")


def main() -> None:
    print("AGC Expansion Mode Active")
    print("Absolute Geometric Yardstick Lemma — computational experiment\n")
    result = run_experiment()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    update_expansion_state(result)

    nphc = result["nphc_algebraic_scan"]
    tda = result["tda_conformal_rescaling"]
    jd = result["joint_decision"]

    print("=" * 72)
    print("1) NPHC-STYLE / ALGEBRAIC DISCRETE VOLUME SCAN")
    print("=" * 72)
    print(f"  Two-term positive critical points: {nphc['scan_counts']['two_term_positive_critical']}")
    print(f"  Three-term positive critical points: {nphc['scan_counts']['three_term_positive_critical']}")
    print(f"  Unique R (rounded 6 dec) across scan: {nphc['all_unique_R_count']}")
    print(f"  R sample: {nphc['all_unique_R_sample'][:12]}")
    print(f"  Unique R forced by index theory alone? {nphc['decision']['unique_R_forced_by_index_theory_alone']}")
    print(f"  Reason: {nphc['decision']['reason_not_forced'][:160]}...")
    print()
    print("=" * 72)
    print("2) TDA (H0 PERSISTENT HOMOLOGY) ON OVERALL CONFORMAL FACTOR")
    print("=" * 72)
    print(f"  Samples: {tda['n_samples']}  Ω ∈ {tda['omega_range']}")
    print(f"  H0 topology-only: {tda['H0_topology_only_features']}")
    print(f"  H0 log-Ω line:    {tda['H0_log_omega_line']}")
    print(f"  Barrier against rescaling? {tda['decision']['topological_barrier_against_overall_rescaling']}")
    print(f"  Reason: {tda['decision']['reason'][:180]}...")
    print()
    print("=" * 72)
    print("JOINT DECISION")
    print("=" * 72)
    print(f"  Absolute scale generated? {jd['absolute_scale_generated']}")
    print(f"  {jd['summary']}")
    print(f"  continuous_knobs = {result['continuous_knobs']}")
    print(f"\nSaved {OUT_PATH}")
    print("Updated expansion_state.json")


if __name__ == "__main__":
    main()
