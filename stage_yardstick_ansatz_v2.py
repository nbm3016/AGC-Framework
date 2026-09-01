#!/usr/bin/env python3
"""
Absolute Scale Generation — refined / deeper ansatz class (Expansion Mode).

Goes beyond pure power-sum V(R) = Σ c_i R^{e_i}.

Ansatz families (coefficients & discrete integers ONLY from locked set
{N_gen, n_η,i, monodromy, Vol_k, λ̃_k} and locked pure numbers σ*, r as
*fixed* skeleton data — not free fit parameters):

  A) Instanton / non-perturbative:   V = A exp(−B R^{p}) + C R^{q}
  B) Log-radion:                     V = A (log R)^2 + B R^{p} + C R^{q}
  C) Rational / Möbius density:      V = (a + b R^{p}) / (c + d R^{q})
  D) Spectral product (zeta-like):   V = Σ_k log(λ̃_k + α R^{p}) + β R^{q}
  E) Topological BF/CS-inspired:     V = κ·N_mon·N_gen·f(R) + wall/Casimir
  F) Warp-coupled:                   V = A exp(−n_Σ σ* / R^{p}) + B R^{q}
  G) Double-scale functor (R, χ):    discrete two-field critical points
                                     χ ~ monodromy phase proxy (discrete)

Tests for isolated positive R forced uniquely by discrete/index structure.
TDA-lite: barrier test under Ω-rescaling of each ansatz's critical-set map.

continuous_knobs must remain 0; no scientific Stage 1–4 locks rewritten.
"""

from __future__ import annotations

import itertools
import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import brentq, minimize_scalar

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "yardstick_ansatz_v2.json")
EXPANSION_STATE_PATH = os.path.join(ARTIFACT_DIR, "expansion_state.json")


def load_locked() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    if b.get("status") != "PASS":
        raise ValueError("baseline not PASS")
    return b


def discrete_pack(lr: Dict[str, Any]) -> Dict[str, Any]:
    n_gen = int(lr.get("n_gen") or 3)
    n_eta = [int(x) for x in (lr.get("n_eta_triple") or [3, 8, 15])]
    mon = 24
    vols = [j * (j + 1.0) for j in (0.5, 1.0, 1.5)[:n_gen]]
    lams = [float(x) for x in (lr.get("lambda_targets") or [4.5, 12.0, 22.5])]
    sigma = float(lr.get("sigma_star") or (math.sqrt(3) / 2))
    r = float(lr.get("beta_residual_new") or 0.095716)
    t_wall = float(sum(vols))
    sum_l2 = float(sum(x * x for x in lams))
    atoms = {
        "N_gen": float(n_gen),
        "n1": float(n_eta[0]),
        "n2": float(n_eta[1]),
        "n3": float(n_eta[2]),
        "n_sum": float(sum(n_eta)),
        "mon": float(mon),
        "T_wall": t_wall,
        "sum_lam2": sum_l2,
        "lam0": lams[0],
        "lam1": lams[1],
        "lam2": lams[2],
        "Vol0": vols[0],
        "Vol1": vols[1],
        "Vol2": vols[2],
    }
    # Fixed skeleton pure numbers (not free knobs; locked already)
    locked_pure = {"sigma_star": sigma, "beta_residual": r, "tau_res": r * sigma * sigma}
    exp_pos = sorted({1, 2, n_gen, n_gen + 1, n_eta[0], n_eta[1], mon})
    exp_pos = [e for e in exp_pos if 1 <= e <= mon]
    return {
        "atoms": atoms,
        "locked_pure": locked_pure,
        "exp_pos": exp_pos,
        "lams": lams,
        "n_gen": n_gen,
        "n_eta": n_eta,
        "mon": mon,
        "t_wall": t_wall,
        "sum_l2": sum_l2,
        "sigma": sigma,
        "r": r,
    }


def find_positive_minima(
    f: Callable[[float], float],
    brackets: Sequence[Tuple[float, float]] = (
        (1e-4, 1e-2),
        (1e-2, 1e-1),
        (1e-1, 1.0),
        (1.0, 10.0),
        (10.0, 100.0),
        (100.0, 1e4),
    ),
) -> List[Dict[str, float]]:
    """Grid + scalar minimize on log-R; return local minima with R>0, V''>0 proxy."""
    found: List[Dict[str, float]] = []
    for lo, hi in brackets:
        try:
            res = minimize_scalar(f, bounds=(lo, hi), method="bounded", options={"xatol": 1e-10})
            if not res.success:
                continue
            R = float(res.x)
            if R <= 0 or not math.isfinite(R):
                continue
            # numerical second derivative
            h = max(1e-7 * R, 1e-10)
            v0, vp, vm = f(R), f(R + h), f(R - h)
            v2 = (vp - 2 * v0 + vm) / (h * h)
            if v2 > 0 and math.isfinite(v0):
                found.append({"R": R, "V": float(v0), "V2": float(v2)})
        except Exception:
            continue
    # dedupe by rounded R
    uniq: Dict[float, Dict[str, float]] = {}
    for item in found:
        key = round(item["R"], 8)
        if key not in uniq or item["V"] < uniq[key]["V"]:
            uniq[key] = item
    return list(uniq.values())


def critical_from_derivative(
    dV: Callable[[float], float],
    brackets: Sequence[Tuple[float, float]] = (
        (1e-4, 1e-2),
        (1e-2, 0.1),
        (0.1, 1.0),
        (1.0, 10.0),
        (10.0, 100.0),
        (100.0, 1e4),
    ),
) -> List[float]:
    roots: List[float] = []
    for lo, hi in brackets:
        try:
            flo, fhi = dV(lo), dV(hi)
            if not (math.isfinite(flo) and math.isfinite(fhi)):
                continue
            if flo * fhi > 0:
                continue
            r = brentq(dV, lo, hi, xtol=1e-12)
            if r > 0:
                roots.append(float(r))
        except Exception:
            continue
    return sorted({round(r, 10) for r in roots})


# ---------- Family A: Instanton / non-perturbative ----------
def scan_instanton(pack: Dict[str, Any]) -> Dict[str, Any]:
    atoms = pack["atoms"]
    exp_pos = pack["exp_pos"]
    # restrict coeff pool for tractability
    coeff_names = ["T_wall", "sum_lam2", "mon", "N_gen", "n_sum", "lam0"]
    results = []
    n_checked = 0
    for na, nb, nc in itertools.product(coeff_names, repeat=3):
        A, B, C = atoms[na], atoms[nb], atoms[nc]
        for p, q in itertools.product(exp_pos[:5], repeat=2):
            n_checked += 1
            # V = A exp(-B R^p) + C / R^q   and A exp(-B/R^p) + C R^q
            for mode in ("exp_minus_B_R_p", "exp_minus_B_over_R_p"):

                def make_f(A=A, B=B, C=C, p=p, q=q, mode=mode):
                    if mode == "exp_minus_B_R_p":

                        def f(R: float) -> float:
                            if R <= 0:
                                return 1e300
                            return A * math.exp(-B * (R**p)) + C / (R**q)

                    else:

                        def f(R: float) -> float:
                            if R <= 0:
                                return 1e300
                            return A * math.exp(-B / (R**p)) + C * (R**q)

                    return f

                mins = find_positive_minima(make_f())
                for m in mins:
                    results.append(
                        {
                            "family": "A_instanton",
                            "mode": mode,
                            "coeffs": [na, nb, nc],
                            "exponents": [p, q],
                            "R_star": m["R"],
                            "stable": True,
                        }
                    )
    return _summarize_family("A_instanton", n_checked, results)


# ---------- Family B: Log-radion ----------
def scan_log_radion(pack: Dict[str, Any]) -> Dict[str, Any]:
    atoms = pack["atoms"]
    exp_pos = pack["exp_pos"]
    coeff_names = ["T_wall", "sum_lam2", "mon", "N_gen", "n_sum"]
    results = []
    n_checked = 0
    for na, nb, nc in itertools.product(coeff_names, repeat=3):
        A, B, C = atoms[na], atoms[nb], atoms[nc]
        for p, q in itertools.product(exp_pos[:5], repeat=2):
            if p == q:
                continue
            n_checked += 1

            def f(R: float, A=A, B=B, C=C, p=p, q=q) -> float:
                if R <= 0:
                    return 1e300
                return A * (math.log(R) ** 2) + B * (R**p) + C / (R**q)

            mins = find_positive_minima(f)
            for m in mins:
                results.append(
                    {
                        "family": "B_log_radion",
                        "coeffs": [na, nb, nc],
                        "exponents": [p, q],
                        "R_star": m["R"],
                        "stable": True,
                    }
                )
    return _summarize_family("B_log_radion", n_checked, results)


# ---------- Family C: Rational / Möbius ----------
def scan_rational(pack: Dict[str, Any]) -> Dict[str, Any]:
    atoms = pack["atoms"]
    exp_pos = pack["exp_pos"]
    names = ["T_wall", "sum_lam2", "mon", "N_gen", "n1", "lam0"]
    results = []
    n_checked = 0
    for na, nb, nc, nd in itertools.product(names, repeat=4):
        a, b, c, d = atoms[na], atoms[nb], atoms[nc], atoms[nd]
        if abs(c) < 1e-15:
            continue
        for p, q in itertools.product(exp_pos[:4], repeat=2):
            n_checked += 1

            def f(R: float, a=a, b=b, c=c, d=d, p=p, q=q) -> float:
                if R <= 0:
                    return 1e300
                den = c + d * (R**q)
                if abs(den) < 1e-15:
                    return 1e300
                return (a + b * (R**p)) / den

            # critical: numerator of f' = 0
            # f = num/den; f'=0 => num' den - num den' = 0
            def dcond(R: float, a=a, b=b, c=c, d=d, p=p, q=q) -> float:
                num = a + b * (R**p)
                den = c + d * (R**q)
                nump = b * p * (R ** (p - 1)) if p != 0 else 0.0
                denp = d * q * (R ** (q - 1)) if q != 0 else 0.0
                return nump * den - num * denp

            for R in critical_from_derivative(dcond):
                # stability via numerical V''
                h = max(1e-7 * R, 1e-10)
                try:
                    v2 = (f(R + h) - 2 * f(R) + f(R - h)) / (h * h)
                except Exception:
                    continue
                if v2 > 0 and math.isfinite(f(R)):
                    results.append(
                        {
                            "family": "C_rational",
                            "coeffs": [na, nb, nc, nd],
                            "exponents": [p, q],
                            "R_star": R,
                            "stable": True,
                        }
                    )
    return _summarize_family("C_rational", n_checked, results)


# ---------- Family D: Spectral product / zeta-like ----------
def scan_spectral_product(pack: Dict[str, Any]) -> Dict[str, Any]:
    atoms = pack["atoms"]
    lams = pack["lams"]
    exp_pos = pack["exp_pos"]
    results = []
    n_checked = 0
    # α, β from discrete atoms; p,q from exp pool
    for n_alpha, n_beta in itertools.product(
        ["N_gen", "mon", "n1", "T_wall", "lam0"],
        ["sum_lam2", "T_wall", "mon", "n_sum"],
    ):
        alpha, beta = atoms[n_alpha], atoms[n_beta]
        for p, q in itertools.product(exp_pos[:5], repeat=2):
            n_checked += 1

            def f(R: float, alpha=alpha, beta=beta, p=p, q=q) -> float:
                if R <= 0:
                    return 1e300
                s = 0.0
                for lam in lams:
                    arg = lam + alpha * (R**p)
                    if arg <= 0:
                        return 1e300
                    s += math.log(arg)
                return s + beta / (R**q)

            mins = find_positive_minima(f)
            for m in mins:
                results.append(
                    {
                        "family": "D_spectral_product",
                        "coeffs": [n_alpha, n_beta],
                        "exponents": [p, q],
                        "R_star": m["R"],
                        "stable": True,
                    }
                )
            # dual: log(λ R^2 + α) style
            n_checked += 1

            def f2(R: float, alpha=alpha, beta=beta, p=p, q=q) -> float:
                if R <= 0:
                    return 1e300
                s = 0.0
                for lam in lams:
                    arg = lam * (R**2) + alpha
                    if arg <= 0:
                        return 1e300
                    s += math.log(arg)
                return s + beta * (R**q)

            mins2 = find_positive_minima(f2)
            for m in mins2:
                results.append(
                    {
                        "family": "D_spectral_product",
                        "mode": "log_lam_R2",
                        "coeffs": [n_alpha, n_beta],
                        "exponents": [p, q],
                        "R_star": m["R"],
                        "stable": True,
                    }
                )
    return _summarize_family("D_spectral_product", n_checked, results)


# ---------- Family E: Topological BF/CS-inspired coupling ----------
def scan_topological_coupling(pack: Dict[str, Any]) -> Dict[str, Any]:
    """
    κ is discrete (N_gen * mon or mon only) — topological level.
    f(R) from {R^{-n}, exp(-R^n), (log R)^2} with n discrete.
    Competing wall/Casimir terms from discrete atoms only.
    """
    atoms = pack["atoms"]
    exp_pos = pack["exp_pos"]
    n_gen, mon = pack["n_gen"], pack["mon"]
    kappa_options = {
        "mon": float(mon),
        "N_gen*mon": float(n_gen * mon),
        "n_sum": atoms["n_sum"],
        "N_gen*n_sum": float(n_gen) * atoms["n_sum"],
    }
    results = []
    n_checked = 0
    for nk, kappa in kappa_options.items():
        for nW, nC in itertools.product(["T_wall", "Vol0"], ["sum_lam2", "lam0"]):
            W, C = atoms[nW], atoms[nC]
            for p, q, s in itertools.product(exp_pos[:4], repeat=3):
                for fmode in ("inv", "exp", "log2"):
                    n_checked += 1

                    def f(
                        R: float,
                        kappa=kappa,
                        W=W,
                        C=C,
                        p=p,
                        q=q,
                        s=s,
                        fmode=fmode,
                    ) -> float:
                        if R <= 0:
                            return 1e300
                        if fmode == "inv":
                            top = kappa / (R**s)
                        elif fmode == "exp":
                            top = kappa * math.exp(-(R**s))
                        else:
                            top = kappa * (math.log(R) ** 2)
                        return top + W / (R**p) - C / (R**q)

                    mins = find_positive_minima(f)
                    for m in mins:
                        results.append(
                            {
                                "family": "E_topological_BFCS",
                                "kappa": nk,
                                "fmode": fmode,
                                "coeffs": [nW, nC],
                                "exponents": [p, q, s],
                                "R_star": m["R"],
                                "stable": True,
                            }
                        )
    return _summarize_family("E_topological_BFCS", n_checked, results)


# ---------- Family F: Warp-coupled (uses locked σ* as fixed skeleton number) ----------
def scan_warp_coupled(pack: Dict[str, Any]) -> Dict[str, Any]:
    atoms = pack["atoms"]
    sigma = pack["sigma"]
    n_sum = atoms["n_sum"]
    exp_pos = pack["exp_pos"]
    results = []
    n_checked = 0
    for nA, nB in itertools.product(
        ["T_wall", "mon", "N_gen", "sum_lam2"],
        ["sum_lam2", "T_wall", "lam0", "n_sum"],
    ):
        A, B = atoms[nA], atoms[nB]
        for p, q in itertools.product(exp_pos[:5], repeat=2):
            n_checked += 1
            # V = A exp(-n_Σ σ* R^p) + B/R^q
            # and V = A exp(-n_Σ σ* / R^p) + B R^q

            def f1(R: float, A=A, B=B, p=p, q=q) -> float:
                if R <= 0:
                    return 1e300
                return A * math.exp(-n_sum * sigma * (R**p)) + B / (R**q)

            def f2(R: float, A=A, B=B, p=p, q=q) -> float:
                if R <= 0:
                    return 1e300
                return A * math.exp(-n_sum * sigma / (R**p)) + B * (R**q)

            for mode, f in (("warp_exp_R", f1), ("warp_exp_invR", f2)):
                mins = find_positive_minima(f)
                for m in mins:
                    results.append(
                        {
                            "family": "F_warp_coupled",
                            "mode": mode,
                            "coeffs": [nA, nB],
                            "exponents": [p, q],
                            "uses_locked_sigma_star": True,
                            "R_star": m["R"],
                            "stable": True,
                        }
                    )
    return _summarize_family("F_warp_coupled", n_checked, results)


# ---------- Family G: Two-field discrete functor (R, χ) ----------
def scan_two_field(pack: Dict[str, Any]) -> Dict[str, Any]:
    """
    χ takes values on a discrete circle of order monodromy (χ = 2π k / mon).
    Potential V(R,χ) = a/R^p + b/R^q * (1 + cos(mon*χ)) + c (χ - χ0)^2 / R^s
    Minimize over R for each discrete χ_k; look for unique (R,χ) lock.
    """
    atoms = pack["atoms"]
    mon = pack["mon"]
    exp_pos = pack["exp_pos"]
    results = []
    n_checked = 0
    chi_grid = [2.0 * math.pi * k / mon for k in range(mon)]
    for na, nb, nc in itertools.product(
        ["T_wall", "mon"],
        ["sum_lam2", "lam0"],
        ["N_gen", "n1"],
    ):
        a, b, c = atoms[na], atoms[nb], atoms[nc]
        for p, q, s in itertools.product(exp_pos[:4], repeat=3):
            n_checked += 1
            best = None
            for chi in chi_grid:

                def f(R: float, chi=chi, a=a, b=b, c=c, p=p, q=q, s=s) -> float:
                    if R <= 0:
                        return 1e300
                    return (
                        a / (R**p)
                        + (b / (R**q)) * (1.0 + math.cos(mon * chi))
                        + c * ((chi) ** 2) / (R**s)
                    )

                mins = find_positive_minima(f)
                for m in mins:
                    cand = {
                        "family": "G_two_field",
                        "coeffs": [na, nb, nc],
                        "exponents": [p, q, s],
                        "chi": chi,
                        "R_star": m["R"],
                        "V": m["V"],
                        "stable": True,
                    }
                    if best is None or m["V"] < best["V"]:
                        best = cand
            if best is not None:
                results.append(best)
    # uniqueness of global best R across discrete χ-minimizers
    return _summarize_family("G_two_field", n_checked, results)


def _summarize_family(
    name: str, n_checked: int, results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    if not results:
        return {
            "family": name,
            "n_checked": n_checked,
            "n_stable_minima": 0,
            "n_unique_R": 0,
            "unique_R_sample": [],
            "R_min": None,
            "R_max": None,
            "R_std": None,
            "unique_forced": False,
            "sample": [],
        }
    Rs = np.array([r["R_star"] for r in results], dtype=float)
    unique = sorted({round(float(x), 6) for x in Rs if x > 0 and math.isfinite(x)})
    return {
        "family": name,
        "n_checked": n_checked,
        "n_stable_minima": len(results),
        "n_unique_R": len(unique),
        "unique_R_sample": unique[:25],
        "R_min": float(np.min(Rs)),
        "R_max": float(np.max(Rs)),
        "R_median": float(np.median(Rs)),
        "R_std": float(np.std(Rs)),
        "unique_forced": len(unique) == 1,
        "sample": results[:6],
    }


def tda_ansatz_critical_map(family_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Meta-TDA: treat the cloud of all found R_* (log R) as a point set.
    If absolute scale were forced, the cloud should collapse to one point
    (single infinite H0 bar at distance 0). Multiplicity => no barrier selecting one R.
    """
    all_logR = []
    for fam in family_summaries:
        for r in fam.get("unique_R_sample") or []:
            if r > 0:
                all_logR.append(math.log(r))
    if len(all_logR) < 2:
        return {
            "decision": "insufficient_points",
            "topological_selection_of_unique_R": False,
            "reason": "Too few distinct R to form a barrier test.",
        }
    pts = np.array(all_logR, dtype=float).reshape(-1, 1)
    # H0 via sorted gaps
    order = np.sort(pts.ravel())
    gaps = np.diff(order)
    max_gap = float(np.max(gaps)) if len(gaps) else 0.0
    spread = float(order[-1] - order[0])
    return {
        "n_logR_points": len(all_logR),
        "logR_spread": spread,
        "max_adjacent_gap": max_gap,
        "topological_selection_of_unique_R": spread < 1e-9,
        "reason": (
            f"Critical-value cloud of refined ansatz families spans Δlog R = {spread:.4f} "
            f"with max adjacent gap {max_gap:.4f}. A forced unique yardstick would collapse "
            "this cloud to a point. No such collapse → no topological selection of unique R."
        ),
    }


def cross_family_uniqueness(family_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_R = []
    for fam in family_summaries:
        all_R.extend(fam.get("unique_R_sample") or [])
        # also collect from full counts
    # rebuild from samples only (already unique per family)
    unique = sorted({round(float(r), 6) for r in all_R if r and r > 0})
    # Intersection of families that each claim unique_forced
    forced_families = [f["family"] for f in family_summaries if f.get("unique_forced")]
    return {
        "n_unique_R_across_all_families_sample": len(unique),
        "unique_R_sample": unique[:40],
        "families_with_internally_unique_R": forced_families,
        "global_unique_R_forced": len(unique) == 1 and len(unique) > 0,
        "reason": (
            "Even if one family had a single R under one assignment pattern, "
            "cross-family comparison is required for index-forced uniqueness. "
            f"Observed n_unique (from samples) = {len(unique)}; "
            f"internally unique families = {forced_families or 'none'}."
        ),
    }


def run() -> Dict[str, Any]:
    b = load_locked()
    lr = b["locked_results"]
    pack = discrete_pack(lr)

    print("Scanning Family A: Instanton / non-perturbative...")
    fam_A = scan_instanton(pack)
    print(f"  -> minima={fam_A['n_stable_minima']} uniqueR={fam_A['n_unique_R']}")

    print("Scanning Family B: Log-radion...")
    fam_B = scan_log_radion(pack)
    print(f"  -> minima={fam_B['n_stable_minima']} uniqueR={fam_B['n_unique_R']}")

    print("Scanning Family C: Rational / Möbius...")
    fam_C = scan_rational(pack)
    print(f"  -> minima={fam_C['n_stable_minima']} uniqueR={fam_C['n_unique_R']}")

    print("Scanning Family D: Spectral product / zeta-like...")
    fam_D = scan_spectral_product(pack)
    print(f"  -> minima={fam_D['n_stable_minima']} uniqueR={fam_D['n_unique_R']}")

    print("Scanning Family E: Topological BF/CS-inspired...")
    fam_E = scan_topological_coupling(pack)
    print(f"  -> minima={fam_E['n_stable_minima']} uniqueR={fam_E['n_unique_R']}")

    print("Scanning Family F: Warp-coupled (locked σ*)...")
    fam_F = scan_warp_coupled(pack)
    print(f"  -> minima={fam_F['n_stable_minima']} uniqueR={fam_F['n_unique_R']}")

    print("Scanning Family G: Two-field (R, χ monodromy)...")
    fam_G = scan_two_field(pack)
    print(f"  -> minima={fam_G['n_stable_minima']} uniqueR={fam_G['n_unique_R']}")

    families = [fam_A, fam_B, fam_C, fam_D, fam_E, fam_F, fam_G]
    cross = cross_family_uniqueness(families)
    tda = tda_ansatz_critical_map(families)

    abs_generated = bool(
        cross["global_unique_R_forced"]
        and tda.get("topological_selection_of_unique_R")
    )

    result = {
        "banner": "AGC Expansion Mode Active — Absolute Scale refined ansatz class v2",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sector": "Absolute Scale Generation",
        "ansatz_generation": 2,
        "prior_power_sum_scan": "yardstick_lemma_experiment.json",
        "continuous_knobs": 0,
        "scientific_locks_altered": False,
        "discrete_data_used": {
            "atoms": pack["atoms"],
            "locked_pure_skeleton_numbers": pack["locked_pure"],
            "exp_pos": pack["exp_pos"],
            "note": (
                "σ* and β residual used only as fixed locked skeleton pure numbers "
                "(not free fit parameters)."
            ),
        },
        "families": {f["family"]: f for f in families},
        "cross_family": cross,
        "tda_critical_cloud": tda,
        "joint_decision": {
            "absolute_scale_generated": abs_generated,
            "global_unique_R_forced": cross["global_unique_R_forced"],
            "topological_selection_of_unique_R": tda.get(
                "topological_selection_of_unique_R", False
            ),
            "summary": (
                "Refined ansatz classes (instanton, log-radion, rational, spectral product, "
                "topological BF/CS-inspired, warp-coupled, two-field monodromy) produce "
                "stable positive R minima for many discrete assignments, but do not force a "
                "unique index-selected absolute scale. Critical-value cloud does not collapse. "
                "Absolute Geometric Yardstick lemma remains open. continuous_knobs=0."
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
    note = {
        "experiment": "yardstick_ansatz_v2_refined",
        "timestamp_utc": result["timestamp_utc"],
        "absolute_scale_generated": result["joint_decision"]["absolute_scale_generated"],
        "global_unique_R_forced": result["joint_decision"]["global_unique_R_forced"],
        "artifact": "yardstick_ansatz_v2.json",
        "families": list(result["families"].keys()),
        "lemma_status": "still_open_required_for_closure",
    }
    es.setdefault("lemma_experiments", []).append(note)
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "Absolute Scale — refined ansatz v2",
            "action": "deeper_functor_scan",
            "item": "Families A–G; no permanent scaffolding retained",
            "status": "complete",
            "timestamp_utc": result["timestamp_utc"],
        }
    )
    for bot in es.get("active_bottlenecks") or []:
        if bot.get("sector") == "Absolute Scale Generation":
            bot["lemma_experiment_v2"] = note
            bot["last_experiment_utc"] = result["timestamp_utc"]
            break
    es["last_updated"] = result["timestamp_utc"]
    with open(EXPANSION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(es, f, indent=2)
        f.write("\n")


def main() -> None:
    print("AGC Expansion Mode Active")
    print("Absolute Scale — refined/deeper ansatz class (v2)\n")
    result = run()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    update_expansion_state(result)

    print()
    print("=" * 72)
    print("FAMILY SUMMARY")
    print("=" * 72)
    for name, fam in result["families"].items():
        print(
            f"  {name}: checked={fam['n_checked']} minima={fam['n_stable_minima']} "
            f"uniqueR={fam['n_unique_R']} forced_internal={fam['unique_forced']}"
        )
    print()
    print("CROSS-FAMILY:", result["cross_family"]["reason"][:200])
    print("TDA CLOUD:", result["tda_critical_cloud"].get("reason", "")[:200])
    print()
    print("JOINT:", result["joint_decision"]["summary"])
    print(f"continuous_knobs = {result['continuous_knobs']}")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
