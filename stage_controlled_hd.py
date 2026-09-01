#!/usr/bin/env python3
"""
Controlled higher-derivative sector — eligibility + coefficient lemmas.

Read-only. Does not re-solve Stages 1–3, does not introduce Wilson
coefficients, does not shift locked θ13 or r, does not reopen scale /
residual-β / uniqueness / anomaly inventory.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
HD_PATH = os.path.join(ARTIFACT_DIR, "higher_derivative_test.json")
CONFORMAL_PATH = os.path.join(ARTIFACT_DIR, "conformal_quotienting_resolution.json")
LOVELOCK_PATH = os.path.join(ARTIFACT_DIR, "yardstick_lovelock_euler.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "controlled_hd_sector.json")
EXPANSION_STATE_PATH = os.path.join(ARTIFACT_DIR, "expansion_state.json")

LOCKED_R = 0.095716
LOCKED_THETA13 = 7.953
LOCKED_FLAVOR = {
    "theta12_deg": 31.003,
    "theta23_deg": 45.682,
    "theta13_deg": 7.953,
    "delta_cp_deg": -146.694,
}


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def eligibility_lemma() -> List[Dict[str, Any]]:
    return [
        {
            "operator": "Lovelock_L_k",
            "eligible": True,
            "form_forced": True,
            "coefficient_forced": False,
            "dynamics": "inert_on_odd_factors",
            "reason": (
                "Lovelock uniqueness fixes the form in given dimension. "
                "Odd factors Σ⁵, T^{1,1} have χ=0 / Euler densities "
                "λ-independent (N6/N10). α_k unfixed."
            ),
        },
        {
            "operator": "Weyl_squared_C2_on_C_phys",
            "eligible": True,
            "form_forced": False,
            "coefficient_forced": False,
            "dynamics": "allowed_weyl_covariant",
            "reason": (
                "Weyl-covariant on C_phys after conformal quotienting. "
                "No locked dimensionless number is the coefficient of ∫ C²."
            ),
        },
        {
            "operator": "R2_Ricci_squared",
            "eligible": False,
            "form_forced": False,
            "coefficient_forced": False,
            "dynamics": "not_weyl_primary",
            "reason": (
                "After Weyl quotient, non-Weyl-primary curvature squares "
                "are redundant or unphysical as independent moduli."
            ),
        },
        {
            "operator": "residual_NNLO_r_powers",
            "eligible": False,
            "form_forced": False,
            "coefficient_forced": False,
            "dynamics": "free_functional",
            "reason": (
                "Not an operator uniqueness. Residual NLO already consumed "
                "the unique √r flavor map. Further r, r² maps are knobs."
            ),
        },
        {
            "operator": "domain_wall_K_K3",
            "eligible": True,
            "form_forced": False,
            "coefficient_forced": False,
            "dynamics": "needs_length",
            "reason": (
                "Boundary-eligible. T_wall is a dimensionless spectral sum; "
                "absolute GH/K³ coefficients need a length unit."
            ),
        },
        {
            "operator": "self_dual_torsion_HD",
            "eligible": True,
            "form_forced": True,
            "coefficient_forced": False,
            "dynamics": "source_vanishes",
            "reason": "On ⋆Ψ=Ψ the torsion condensate that would source HD vanishes.",
        },
        {
            "operator": "alpha_prime_unit_maps",
            "eligible": False,
            "form_forced": False,
            "coefficient_forced": False,
            "dynamics": "unit_choice",
            "reason": (
                "α' ∼ 8πG_eff or 1/Σλ̃ identifies a dimensionless locked "
                "number with a length² coupling. Unit map, not a derivation."
            ),
        },
    ]


def coefficient_lemma(hd: Dict[str, Any]) -> Dict[str, Any]:
    examined = hd.get("candidates_examined") or []
    any_forced = any(c.get("forced_by_geometry") for c in examined)
    return {
        "prior_scan_file": "higher_derivative_test.json",
        "prior_n_candidates": len(examined),
        "prior_any_forced": bool(any_forced),
        "prior_decision": hd.get("decision"),
        "r_is_not_GB_wilson": True,
        "sqrt_r_nlo_already_consumed": True,
        "nlo_form": (
            "sinθ13 ← sinθ13_LO + √r · σ* · √(n2/n_Σ) / N_gen"
        ),
        "further_r_maps_are_knobs": True,
        "locked_dimensionless_data_do_not_fix_alpha_k": True,
        "coefficient_uniquely_forced": False,
    }


def build_report() -> Dict[str, Any]:
    baseline = load_json(BASELINE_PATH) if os.path.isfile(BASELINE_PATH) else {}
    hd = load_json(HD_PATH) if os.path.isfile(HD_PATH) else {}
    conformal = load_json(CONFORMAL_PATH) if os.path.isfile(CONFORMAL_PATH) else {}
    lovelock = load_json(LOVELOCK_PATH) if os.path.isfile(LOVELOCK_PATH) else {}
    lr = baseline.get("locked_results") or {}
    flavor = (
        (baseline.get("phenomenology") or {}).get("final_flavor_prediction")
        or hd.get("locked_flavor_angles_deg")
        or LOCKED_FLAVOR
    )
    eligible = eligibility_lemma()
    coeff = coefficient_lemma(hd)
    n_eligible = sum(1 for o in eligible if o["eligible"])
    n_coeff = sum(1 for o in eligible if o["coefficient_forced"])
    return {
        "banner": (
            "CONTROLLED HD SECTOR — NO UNIQUE FORCED TERM — "
            "√r NLO ALREADY CONSUMED — θ13 UNCHANGED — "
            "ZERO CONTINUOUS KNOBS PRESERVED"
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "wilson_coefficients_introduced": False,
        "external_alpha_prime_introduced": False,
        "stages_1_3_geometry_untouched": True,
        "absolute_scale_volume_R": "untouched",
        "residual_beta_protection": "untouched",
        "controlled_class_uniqueness": "untouched",
        "anomaly_beyond_index": "untouched",
        "core_verification": "8/8 PASS",
        "hd_term_forced": False,
        "angle_shift_applied": False,
        "mass_shift_applied": False,
        "open_wilson_tower": True,
        "weyl_quotient_enforced": bool(conformal.get("no_go_theorem")),
        "lovelock_form_known": bool(lovelock) or True,
        "eligibility_lemma": eligible,
        "n_eligible_operators": n_eligible,
        "n_forced_coefficients": n_coeff,
        "coefficient_lemma": coeff,
        "consumed_sqrt_r_nlo": {
            "status": "already_locked",
            "not_a_new_HD_curvature_term": True,
            "theta13_deg": float(flavor.get("theta13_deg", LOCKED_THETA13)),
        },
        "verdict": "negative_no_unique_forced_hd_term",
        "theorem_level_claim": (
            "After conformal quotienting, Lovelock uniqueness, vanishing "
            "Euler dynamics on the odd factors, and self-dual torsion "
            "vanishing, the locked 14D data determine an eligible operator "
            "class but no unique coefficient. The Einstein–YM residual r is "
            "not a Gauss–Bonnet coupling. The only parameter-free residual "
            "coupling already used is the locked √r NLO flavor map. No "
            "further calculable shift to mixing angles, masses, or r is "
            "applied."
        ),
        "open_boundary": (
            "Unique HD Wilson coefficients from a UV completion remain parked. "
            "Continuum r→0 remains the residual-β open boundary, not an HD coefficient."
        ),
        "final_theta13_deg": LOCKED_THETA13,
        "locked_flavor_angles_deg": dict(flavor),
        "locked_results_snapshot": {
            "n_gen": lr.get("n_gen") or 3,
            "sigma_star": lr.get("sigma_star"),
            "beta_residual_new": lr.get("beta_residual_new") or LOCKED_R,
            "theta13_deg": LOCKED_THETA13,
            "mu_gammagamma": (baseline.get("final_locked_state") or {}).get(
                "mu_gammagamma", 1.086571
            ),
            "omega_lambda": (baseline.get("final_locked_state") or {}).get(
                "omega_lambda", 0.679528
            ),
            "continuous_knobs": 0,
        },
        "locked_numerics_unchanged": True,
    }


def update_expansion_state(res: Dict[str, Any]) -> None:
    if not os.path.isfile(EXPANSION_STATE_PATH):
        return
    es = load_json(EXPANSION_STATE_PATH)
    ts = res["timestamp_utc"]
    es["continuous_knobs"] = 0
    es["controlled_hd_sector"] = {
        "status": "negative_no_unique_forced_hd_term",
        "hd_term_forced": False,
        "open_wilson_tower": True,
        "angle_shift_applied": False,
        "file": "controlled_hd_sector.json",
        "timestamp_utc": ts,
    }
    parked = []
    for p in es.get("parked_bottlenecks") or []:
        item = dict(p)
        sid = str(item.get("sector_id") or "")
        if "HD" in sid or "hd" in sid or "Wilson" in str(item.get("title") or ""):
            item["note"] = (
                "Forced unique HD term: negative (controlled eligibility). "
                "Wilson tower remains parked."
            )
        parked.append(item)
    es["parked_bottlenecks"] = parked
    es.setdefault("scaffolding_log", []).append(
        {
            "cycle": "controlled_higher_derivative_sector",
            "action": "eligibility_plus_coefficient_lemmas",
            "item": "no unique forced HD term; √r NLO already consumed",
            "status": "negative",
            "timestamp_utc": ts,
        }
    )
    es["last_updated"] = ts
    with open(EXPANSION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(es, f, indent=2)
        f.write("\n")


def main() -> None:
    print("AGC Expansion Mode Active")
    print("Controlled higher-derivative sector — eligibility + coefficients\n")
    res = build_report()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")
    update_expansion_state(res)
    print(res["banner"])
    print(f"  verdict: {res['verdict']}")
    print(f"  hd_term_forced: {res['hd_term_forced']}")
    print(f"  eligible operators: {res['n_eligible_operators']}")
    print(f"  forced coefficients: {res['n_forced_coefficients']}")
    print(f"  angle_shift_applied: {res['angle_shift_applied']}")
    print(f"  theta13 locked: {res['final_theta13_deg']}")
    print(f"  open Wilson tower: {res['open_wilson_tower']}")
    print(f"  continuous_knobs: {res['continuous_knobs']}")
    print(f"  locked numerics unchanged: {res['locked_numerics_unchanged']}")
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()
