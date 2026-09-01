#!/usr/bin/env python3
"""
Absolute Geometric Yardstick Lemma — Option A (forced Lovelock / Euler form).

Named theorem (Lovelock 1971): in D spacetime dimensions, the unique
metric Lagrangian densities built from the Riemann tensor that yield
second-order equations of motion are the Lovelock series
  L_k = Euler density E_{2k} of dimension 2k  (k = 0..⌊(D-1)/2⌋).

This experiment:
  1) Identifies which Lovelock/Euler forms are admissible for the AGC
     fibration dimension and for the internal factors (T^{1,1}, Σ⁵).
  2) Uses ONLY those forced forms (not free Wilson towers).
  3) Restricts numerical coefficients to the locked discrete set
     {N_gen, n_η, monodromy, Vol_k, λ̃_k, …} and locked pure numbers
     (σ*, r) as fixed skeleton data — not free fits.
  4) Tests whether index theory + forced Lovelock form selects a unique
     absolute scale R_* > 0.

Expansion Mode: continuous_knobs remain 0; Stage 1–4 scientific locks untouched.
"""

from __future__ import annotations

import itertools
import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import minimize_scalar

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "yardstick_lovelock_euler.json")
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
    sigma = float(lr.get("sigma_star") or (math.sqrt(3.0) / 2.0))
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
    return {
        "atoms": atoms,
        "n_gen": n_gen,
        "n_eta": n_eta,
        "mon": mon,
        "vols": vols,
        "lams": lams,
        "sigma": sigma,
        "r": r,
        "t_wall": t_wall,
        "sum_l2": sum_l2,
        "coeff_pool": ["N_gen", "n1", "n2", "n3", "n_sum", "mon", "T_wall", "sum_lam2", "lam0"],
    }


# ---------------------------------------------------------------------------
# Lovelock / Euler theorem bookkeeping (forced FORM)
# ---------------------------------------------------------------------------

def lovelock_admissible_catalog() -> Dict[str, Any]:
    """
    Named theorem: Lovelock (1971). Unique second-order curvature Lagrangians
    in D dimensions are L_k ∝ Euler density of dimension 2k, for
    k = 0,1,...,⌊(D-1)/2⌋.

    AGC bulk fibration dimension taken as D=14 (Y^{14} → M^4).
    Internal factors: T^{1,1} (dim 5), Σ^5 (dim 5); product internal dim 10.
    """
    D_bulk = 14
    k_max_bulk = (D_bulk - 1) // 2  # 6
    # Admissible Lovelock orders in bulk
    bulk_orders = list(range(0, k_max_bulk + 1))  # L_0..L_6

    # Internal factors (odd-dimensional): integrated Euler densities
    # χ(M^{2k+1}) = 0 for closed orientable odd-dimensional manifolds.
    internal_factors = {
        "T11": {
            "dim": 5,
            "odd": True,
            "euler_characteristic": 0,
            "note": "Odd-dimensional SE 5-fold; χ=0. Pure topological Euler density integrates to 0.",
        },
        "Sigma5": {
            "dim": 5,
            "odd": True,
            "euler_characteristic": 0,
            "note": "Odd-dimensional APS wall 5-fold; χ=0.",
        },
        "T11xSigma5_product": {
            "dim": 10,
            "odd": False,
            "euler_characteristic": "χ(T11)*χ(Σ5)=0*0=0 (Künneth/product for closed factors)",
            "note": "Product of odd manifolds has vanishing Euler characteristic.",
        },
    }

    # Scaling of Lovelock density L_k under g_internal → R² ĝ (overall volume radius)
    # Riemann ~ 1/R², so (Riem)^k ~ 1/R^{2k}; √g_n ~ R^n ⇒ ∫√g L_k ~ R^{n-2k}
    # Effective 4D potential contribution after reduction ~ ∫√g_n L_k  (up to Planck factors)
    def scaling_internal(n: int, k: int) -> Dict[str, Any]:
        power = n - 2 * k
        return {
            "internal_dim_n": n,
            "lovelock_order_k": k,
            "volume_integrand_scales_as_R_to": power,
            "vanishes_as_topological_density_when": (
                "2k == n and χ=0 (odd n always has χ=0 for closed orientable case)"
                if (2 * k == n)
                else None
            ),
        }

    scalings = {
        "on_T11_dim5": [scaling_internal(5, k) for k in range(0, 3)],  # k≤2 for n=5 meaningful
        "on_Sigma5_dim5": [scaling_internal(5, k) for k in range(0, 3)],
        "on_product_dim10": [scaling_internal(10, k) for k in range(0, 6)],
        "on_bulk_dim14_as_internal": [scaling_internal(14, k) for k in range(0, 7)],
    }

    # Forced 4D-effective forms after reduction on overall radius R (shape fixed at σ*):
    # Only powers R^{n-2k} for admissible (n,k) can appear from pure Lovelock.
    forced_powers_from_lovelock = sorted(
        {
            5 - 2 * k
            for k in range(0, 3)  # T11 or Σ5
        }
        | {
            10 - 2 * k
            for k in range(0, 6)  # product internal
        }
        | {
            14 - 2 * k
            for k in range(0, 7)
        }
    )

    return {
        "named_theorem": "Lovelock (1971): unique second-order metric Lagrangians = Euler densities E_{2k}",
        "D_bulk": D_bulk,
        "bulk_lovelock_orders_k": bulk_orders,
        "internal_factors": internal_factors,
        "scalings": scalings,
        "forced_volume_powers_R_to_the": forced_powers_from_lovelock,
        "key_topological_obstruction": (
            "T^{1,1} and Σ⁵ are odd-dimensional ⇒ Euler characteristic χ=0. "
            "The pure topological (integrated) Euler densities that would give "
            "R-independent cosmological terms from L_{n/2} vanish. "
            "No Lovelock topological constant term is forced nonzero by the locked geometry."
        ),
        "form_forced_not_free": (
            "Admissible curvature densities are only Lovelock L_k; free R², R_{μν}R^{μν} "
            "with independent Wilson coefficients are NOT allowed under the named theorem "
            "unless they recombine into Lovelock combinations."
        ),
    }


# ---------------------------------------------------------------------------
# Evaluate forced Lovelock power-sum potentials with discrete coefficients
# ---------------------------------------------------------------------------

def find_minima(f: Callable[[float], float]) -> List[Dict[str, float]]:
    brackets = [
        (1e-4, 1e-2),
        (1e-2, 0.1),
        (0.1, 1.0),
        (1.0, 10.0),
        (10.0, 1e2),
        (1e2, 1e4),
    ]
    found: List[Dict[str, float]] = []
    for lo, hi in brackets:
        try:
            res = minimize_scalar(f, bounds=(lo, hi), method="bounded", options={"xatol": 1e-12})
            if not res.success:
                continue
            R = float(res.x)
            if R <= 0 or not math.isfinite(R):
                continue
            h = max(1e-8 * R, 1e-12)
            v2 = (f(R + h) - 2 * f(R) + f(R - h)) / (h * h)
            if v2 > 0 and math.isfinite(f(R)):
                found.append({"R": R, "V": float(f(R)), "V2": float(v2)})
        except Exception:
            continue
    uniq: Dict[float, Dict[str, float]] = {}
    for item in found:
        key = round(item["R"], 9)
        if key not in uniq or item["V"] < uniq[key]["V"]:
            uniq[key] = item
    return list(uniq.values())


def analytic_two_power_critical(
    c1: float, p1: int, c2: float, p2: int
) -> Optional[Tuple[float, float]]:
    """V = c1 R^{p1} + c2 R^{p2}; critical if c1 p1 R^{p1-1} + c2 p2 R^{p2-1} = 0."""
    if p1 == p2 or c1 == 0.0 or c2 == 0.0:
        return None
    if p1 == 0 or p2 == 0:
        # Constant term: V' = c_other * p_other * R^{p-1} = 0 has no finite R>0 root
        # unless the non-constant coefficient vanishes.
        return None
    # R^{p1-p2} = - (c2 p2)/(c1 p1)
    rhs = -(c2 * p2) / (c1 * p1)
    if rhs <= 0:
        return None
    power = p1 - p2
    try:
        R = rhs ** (1.0 / power)
        R = float(R)
    except Exception:
        return None
    if not (math.isfinite(R) and R > 0):
        return None
    V2 = c1 * p1 * (p1 - 1) * R ** (p1 - 2) + c2 * p2 * (p2 - 1) * R ** (p2 - 2)
    return R, float(V2)


def scan_forced_lovelock_forms(pack: Dict[str, Any], catalog: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forced form: V(R) = Σ_k α_k R^{n_k - 2k}  where powers come ONLY from
    Lovelock scaling on admissible internal dimensions, and α_k ∈ discrete set
    (signed).
    """
    atoms = pack["atoms"]
    pool = pack["coeff_pool"]
    powers = list(catalog["forced_volume_powers_R_to_the"])
    # Drop pure constants (power 0) as they cannot create a critical point alone;
    # keep them for multi-term combinations.
    powers = sorted(set(int(p) for p in powers))

    # --- Two-term forced-power potentials ---
    two_term: List[Dict[str, Any]] = []
    n_two = 0
    for p, q in itertools.combinations(powers, 2):
        if p == q:
            continue
        for na, nb in itertools.product(pool, repeat=2):
            for sa, sb in ((1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (-1.0, -1.0)):
                n_two += 1
                c1, c2 = sa * atoms[na], sb * atoms[nb]
                res = analytic_two_power_critical(c1, p, c2, q)
                if res is None:
                    continue
                R, V2 = res
                if V2 > 0:
                    two_term.append(
                        {
                            "form": f"V=({sa:+.0f}){na} R^{{{p}}} + ({sb:+.0f}){nb} R^{{{q}}}",
                            "powers": [p, q],
                            "R_star": R,
                            "V2": V2,
                            "stable": True,
                            "forced_powers": True,
                        }
                    )

    # --- Three-term forced-power (poly roots of V'=0; restricted discrete sample) ---
    three_term: List[Dict[str, Any]] = []
    n_three = 0
    pool3 = ["T_wall", "sum_lam2", "mon", "N_gen", "n_sum", "lam0"]
    # Prefer physically natural Lovelock powers from n=5 and n=10 only
    powers3 = sorted({p for p in powers if p in (1, 2, 3, 4, 5, 6, 8, 10)})
    power_triples = list(itertools.combinations(powers3, 3))
    for p, q, s in power_triples:
        for na, nb, nc in itertools.product(pool3, repeat=3):
            for signs in itertools.product((-1.0, 1.0), repeat=3):
                n_three += 1
                coeffs = [
                    signs[0] * atoms[na],
                    signs[1] * atoms[nb],
                    signs[2] * atoms[nc],
                ]
                exps = [p, q, s]
                # V' = sum c e R^{e-1} = 0 → poly after shift
                d_terms = [(c * e, e - 1) for c, e in zip(coeffs, exps) if e != 0]
                if len(d_terms) < 2:
                    continue
                min_pow = min(pw for _, pw in d_terms)
                shift = -min_pow if min_pow < 0 else 0
                max_pow = max(pw + shift for _, pw in d_terms)
                poly = np.zeros(max_pow + 1, dtype=float)
                for c, pw in d_terms:
                    poly[pw + shift] += c
                coeffs_hi = poly[::-1]
                # strip leading zeros
                idx = 0
                while idx < len(coeffs_hi) - 1 and abs(coeffs_hi[idx]) < 1e-15:
                    idx += 1
                coeffs_hi = coeffs_hi[idx:]
                try:
                    roots = np.roots(coeffs_hi)
                except np.linalg.LinAlgError:
                    continue
                for z in roots:
                    if abs(z.imag) > 1e-9 or z.real <= 1e-12:
                        continue
                    R = float(z.real)
                    # V'' stability
                    v2 = sum(
                        c * e * (e - 1) * (R ** (e - 2))
                        for c, e in zip(coeffs, exps)
                        if e * (e - 1) != 0
                    )
                    if v2 > 0 and math.isfinite(v2):
                        three_term.append(
                            {
                                "form": (
                                    f"V=({signs[0]:+.0f}){na}R^{{{p}}}+"
                                    f"({signs[1]:+.0f}){nb}R^{{{q}}}+"
                                    f"({signs[2]:+.0f}){nc}R^{{{s}}}"
                                ),
                                "powers": [p, q, s],
                                "R_star": R,
                                "V2": float(v2),
                                "stable": True,
                                "forced_powers": True,
                            }
                        )

    def summarize(entries: List[Dict[str, Any]], n_checked: int) -> Dict[str, Any]:
        if not entries:
            return {
                "n_checked": n_checked,
                "n_stable": 0,
                "n_unique_R": 0,
                "unique_R_sample": [],
                "unique_forced": False,
            }
        Rs = [e["R_star"] for e in entries]
        uniq = sorted({round(r, 6) for r in Rs if r > 0 and math.isfinite(r)})
        arr = np.array(Rs, dtype=float)
        return {
            "n_checked": n_checked,
            "n_stable": len(entries),
            "n_unique_R": len(uniq),
            "unique_R_sample": uniq[:30],
            "R_min": float(np.min(arr)),
            "R_max": float(np.max(arr)),
            "R_std": float(np.std(arr)),
            "unique_forced": len(uniq) == 1,
            "sample": entries[:5],
        }

    return {
        "forced_powers_used": powers,
        "two_term": summarize(two_term, n_two),
        "three_term": summarize(three_term, n_three),
        "all_unique_R": sorted(
            {
                round(e["R_star"], 6)
                for e in two_term + three_term
                if e["R_star"] > 0 and math.isfinite(e["R_star"])
            }
        ),
    }


def topological_euler_vanishing(catalog: Dict[str, Any]) -> Dict[str, Any]:
    """
    Direct consequence: odd-dimensional internal factors ⇒ χ=0 ⇒ no
    R-independent topological Lovelock cosmological term forced.
    """
    return {
        "T11_chi": 0,
        "Sigma5_chi": 0,
        "product_chi": 0,
        "forced_topological_cosmological_constant_from_Euler": 0.0,
        "can_this_alone_set_absolute_scale": False,
        "reason": catalog["key_topological_obstruction"],
    }


def index_selection_test(scan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Does APS index / discrete data select ONE of the critical R values?
    The index fixes N_gen, n_η, monodromy — already used as coefficients.
    Uniqueness would require n_unique_R == 1 across the forced-form family.
    """
    all_R = scan["all_unique_R"]
    return {
        "n_unique_R_under_forced_Lovelock_powers": len(all_R),
        "unique_R_forced_by_index_plus_Lovelock_form": len(all_R) == 1 and len(all_R) > 0,
        "sample_R": all_R[:20],
        "reason": (
            "Lovelock fixes the admissible powers {n-2k}, but discrete coefficient "
            "assignments still produce a cloud of distinct positive critical R "
            f"(n_unique={len(all_R)}). APS index data enter only as discrete "
            "coefficients already scanned; they do not pick a single (α_k) vector "
            "among the discrete set. Hence index + forced form does not select a "
            "unique absolute scale."
        ),
    }


def shape_fixed_lovelock_no_go(pack: Dict[str, Any]) -> Dict[str, Any]:
    """
    With shape σ frozen at σ*, pure Lovelock on Einstein internal metrics
    yields V(R) = Σ α_k R^{n-2k}. For a single power, V' never vanishes at
    finite R>0. Multi-power needs ≥2 orders with competing signs — coefficients
    not fixed by Lovelock uniqueness alone (only the form of each L_k is).
    """
    powers = sorted(
        {
            5 - 2 * k
            for k in range(0, 3)
        }
        | {
            10 - 2 * k
            for k in range(0, 6)
        }
    )
    single_power_critical = []
    for p in powers:
        # V = c R^p ⇒ V' = c p R^{p-1} = 0 only if c=0 or p=0 or R=0/∞
        single_power_critical.append(
            {
                "power": p,
                "finite_positive_critical_R": False,
                "note": "Single Lovelock order cannot stabilize R at finite positive value.",
            }
        )
    return {
        "sigma_star_fixed": pack["sigma"],
        "single_order_stabilization_possible": False,
        "single_power_analysis": single_power_critical,
        "requires_at_least_two_lovelock_orders_with_relative_coeff": True,
        "relative_coeff_fixed_by_lovelock_theorem": False,
        "relative_coeff_fixed_by_APS_index": False,
        "note": (
            "Lovelock uniqueness fixes each L_k's tensor structure, not the relative "
            "dimensionless ratios α_k/α_j. Those ratios remain free continuous parameters "
            "unless fixed by another principle — and mapping them onto the discrete set "
            "still fails uniqueness (see scan)."
        ),
    }


def run() -> Dict[str, Any]:
    b = load_locked()
    lr = b["locked_results"]
    pack = discrete_pack(lr)
    catalog = lovelock_admissible_catalog()

    print("Building Lovelock/Euler admissible catalog (forced form)...", flush=True)
    print(f"  Forced volume powers: {catalog['forced_volume_powers_R_to_the']}", flush=True)
    print(f"  χ(T11)=χ(Σ5)=0 (odd dimensions)", flush=True)

    euler = topological_euler_vanishing(catalog)
    nogo = shape_fixed_lovelock_no_go(pack)

    print("Scanning discrete coefficients on forced Lovelock powers only...", flush=True)
    scan = scan_forced_lovelock_forms(pack, catalog)
    print(
        f"  two-term stable={scan['two_term']['n_stable']} uniqueR={scan['two_term']['n_unique_R']}"
    )
    print(
        f"  three-term stable={scan['three_term']['n_stable']} uniqueR={scan['three_term']['n_unique_R']}"
    )
    print(f"  all unique R count={len(scan['all_unique_R'])}")

    index_sel = index_selection_test(scan)

    abs_gen = bool(index_sel["unique_R_forced_by_index_plus_Lovelock_form"])

    result = {
        "banner": "AGC Expansion Mode Active — Absolute Scale Option A (Lovelock/Euler forced form)",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sector": "Absolute Scale Generation",
        "option": "A_Lovelock_Euler_forced_form",
        "why_option_A": (
            "Preferred: form fixed by a named theorem (Lovelock 1971), not a free ansatz class. "
            "Cleaner under Expansion Mode than open multi-field NPHC with unconstrained system choice."
        ),
        "continuous_knobs": 0,
        "scientific_locks_altered": False,
        "named_theorem": catalog["named_theorem"],
        "lovelock_catalog": catalog,
        "topological_euler_vanishing": euler,
        "single_order_nogo": nogo,
        "forced_form_discrete_coeff_scan": scan,
        "index_plus_form_selection": index_sel,
        "joint_decision": {
            "absolute_scale_generated": abs_gen,
            "lovelock_form_forced_by_theorem": True,
            "euler_topological_term_forced_nonzero": False,
            "unique_R_from_index_plus_forced_form": index_sel[
                "unique_R_forced_by_index_plus_Lovelock_form"
            ],
            "relative_lovelock_coeffs_fixed_by_index": False,
            "summary": (
                "Lovelock/Euler theorem forces the admissible curvature densities and thus "
                "the discrete set of volume powers R^{n-2k}. Odd-dimensional T^{1,1} and Σ⁵ "
                "have χ=0, so pure topological Euler terms vanish. Single Lovelock order "
                "cannot stabilize finite R. Multi-order combinations with coefficients from "
                "the locked discrete set produce many distinct positive critical R; APS index "
                "data do not select a unique coefficient vector. Absolute scale is not "
                "generated. continuous_knobs=0."
            ),
        },
        "lemma_status": "still_open_required_for_closure",
        "core_skeleton_version": b.get("version"),
        "locked_continuous_knobs": lr.get("continuous_knobs", 0),
        "option_B_deferred_reason": (
            "Option A is the stronger clean attack (form theorem + discrete coeffs). "
            "Multi-field NPHC (R,σ,φ) would reintroduce either free relative Lovelock "
            "ratios or an unconstrained superpotential family; σ is already locked at "
            "σ* with m²>0, so the only open modulus is R — already covered by this scan."
        ),
    }
    return result


def update_expansion_state(result: Dict[str, Any]) -> None:
    if not os.path.isfile(EXPANSION_STATE_PATH):
        return
    with open(EXPANSION_STATE_PATH, encoding="utf-8") as f:
        es = json.load(f)
    note = {
        "experiment": "yardstick_lovelock_euler_option_A",
        "timestamp_utc": result["timestamp_utc"],
        "absolute_scale_generated": result["joint_decision"]["absolute_scale_generated"],
        "unique_R_forced": result["joint_decision"][
            "unique_R_from_index_plus_forced_form"
        ],
        "euler_chi_vanishes": True,
        "artifact": "yardstick_lovelock_euler.json",
        "lemma_status": "still_open_required_for_closure",
    }
    es.setdefault("lemma_experiments", []).append(note)
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "Absolute Scale — Lovelock/Euler forced form (Option A)",
            "action": "theorem_forced_form_scan",
            "item": "Lovelock L_k only; discrete coeffs; no permanent scaffolding",
            "status": "complete",
            "timestamp_utc": result["timestamp_utc"],
        }
    )
    for bot in es.get("active_bottlenecks") or []:
        if bot.get("sector") == "Absolute Scale Generation":
            bot["lemma_experiment_lovelock"] = note
            bot["last_experiment_utc"] = result["timestamp_utc"]
            # Strengthen lemma statement with Lovelock obstruction
            bot["refined_obstruction"] = (
                "Lovelock form forced but relative α_k unfixed by index; "
                "odd-dim internal χ=0; no unique R_*."
            )
            break
    es["last_updated"] = result["timestamp_utc"]
    with open(EXPANSION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(es, f, indent=2)
        f.write("\n")


def main() -> None:
    print("AGC Expansion Mode Active")
    print("Absolute Scale — Option A: Lovelock/Euler forced form\n")
    result = run()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    update_expansion_state(result)

    jd = result["joint_decision"]
    print()
    print("=" * 72)
    print("JOINT DECISION")
    print("=" * 72)
    print(f"  Absolute scale generated? {jd['absolute_scale_generated']}")
    print(f"  Lovelock form forced by theorem? {jd['lovelock_form_forced_by_theorem']}")
    print(f"  Euler topological term forced nonzero? {jd['euler_topological_term_forced_nonzero']}")
    print(f"  Unique R from index + forced form? {jd['unique_R_from_index_plus_forced_form']}")
    print(f"  {jd['summary']}")
    print(f"  continuous_knobs = {result['continuous_knobs']}")
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
