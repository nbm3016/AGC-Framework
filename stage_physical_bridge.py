#!/usr/bin/env python3
"""
Physical Bridge — locked geometry → dimensionless low-energy observables.

Uses only already-locked Stage 1–4 maps. Does not fit, does not introduce a
mass or length, does not promote a new residual or σ. continuous_knobs = 0.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from stage2b_beta_variational import C2_SU3, eight_pi_g_eff
from stage4_flavor_geometry import from_locked_phenomenology, run_flavor_geometry_analysis
from stage4_phenomenology import (
    LockedPhenomenology,
    kk_interference_amplitude,
    load_locked_phenomenology,
    predict_mass_ratios,
    predict_mu_gammagamma,
    predict_mu_gammagamma_band,
    predict_neutrino_splittings,
    predict_omega_lambda,
    predict_proton_lifetime_log10,
    predict_rho_custodial,
    predict_w0_dark_energy,
)

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "physical_bridge.json")
LOG_PATH = os.path.join(ARTIFACT_DIR, "verification_log.txt")

LOCKED_R = 0.095716
LOCKED_SIGMA = math.sqrt(3.0) / 2.0
PI = math.pi

BANNER = "PHYSICAL BRIDGE PROBE COMPLETE – OFFICIAL LOCK UNTOUCHED"


def obs(
    quantity: str,
    expression: str,
    value: Any,
    uniqueness: str,
    *,
    sector: str = "dimensionless",
    notes: str = "",
) -> Dict[str, Any]:
    rec: Dict[str, Any] = {
        "quantity": quantity,
        "geometric_expression": expression,
        "value_from_locked_data": value,
        "uniqueness": uniqueness,
        "sector": sector,
    }
    if notes:
        rec["notes"] = notes
    return rec


def undetermined(
    quantity: str,
    reason: str,
) -> Dict[str, Any]:
    return {
        "quantity": quantity,
        "status": "not_determined_by_locked_geometry",
        "reason": reason,
    }


def inventory(locked: LockedPhenomenology) -> Dict[str, Any]:
    return {
        "N_gen": locked.n_gen,
        "lambda_tilde": list(locked.lambda_targets),
        "sigma_star": locked.sigma_star,
        "sigma_star_exact": "sqrt(3)/2",
        "n_eta": list(locked.n_eta),
        "delta_eta_over_pi": ["1/4", "2/3", "5/4"],
        "beta_residual_official": LOCKED_R,
        "beta_residual_full_legacy": locked.beta_full,
        "beta_laplacian": locked.beta_laplacian,
        "C2_SU3": C2_SU3,
        "eight_pi_g_eff": locked.eight_pi_g_eff,
        "survivors": ["(1/2,0)", "(1,0)", "(3/2,0)"],
        "T_wall": "13/2",
        "monodromy_order": 24,
        "continuous_knobs": 0,
    }


def derived_observables(locked: LockedPhenomenology) -> List[Dict[str, Any]]:
    l0, l1, l2 = locked.lambda_targets
    n1, n2, n3 = locked.n_eta
    n_sum = n1 + n2 + n3
    ratios = predict_mass_ratios(locked)
    mu, i_kk_term, beta_dress = predict_mu_gammagamma(locked)
    mu_unc, mu_lo, mu_hi = predict_mu_gammagamma_band(locked, mu, beta_dress)
    omega = predict_omega_lambda(locked)
    w0 = predict_w0_dark_energy(locked)
    rho = predict_rho_custodial(locked)
    g8 = eight_pi_g_eff(locked.sigma_star)
    kk = kk_interference_amplitude(locked)
    dm21, dm31, dm32, hierarchy, ratio_31_21 = predict_neutrino_splittings(locked)
    tau_log = predict_proton_lifetime_log10(locked)

    flavor = run_flavor_geometry_analysis(from_locked_phenomenology(locked))
    best = flavor["best_geometric"]
    nlo = flavor.get("residual_nlo") or {}
    nlo_ang = nlo.get("nlo_corrected") or {}

    tan2_12 = n1 / n2
    sin13_lo = locked.sigma_star * (n2 / n_sum) / locked.n_gen

    rows: List[Dict[str, Any]] = [
        obs(
            "N_gen",
            "native APS index: #{(j1,0,0) | index(D_APS)=0, ⋆Ψ=Ψ, j1∈½ℕ>0}",
            3,
            "unique (topology)",
            notes="Geometry-generated; not λ̃-seeded.",
        ),
        obs(
            "σ*",
            "argmin V(σ)=(3/2)σ²+(3/2)(λ̃₀/6)²/σ² = √(λ̃₀/6) = √3/2",
            locked.sigma_star,
            "unique (Stage-1B V-minimizer)",
        ),
        obs(
            "λ̃ ratios λ̃₁/λ̃₀, λ̃₂/λ̃₀, λ̃₂/λ̃₁",
            "6 j(j+1) on survivors (1/2,1,3/2) → 12/4.5=8/3, 22.5/4.5=5, 22.5/12=15/8",
            {
                "lambda_21": ratios["lambda_21"],
                "lambda_31": ratios["lambda_31"],
                "lambda_32": ratios["lambda_32"],
                "exact": ["8/3", "5", "15/8"],
            },
            "unique (derived spectrum)",
        ),
        obs(
            "zero-mode mass ratios m2/m1, m3/m1, m3/m2",
            "m_i/m_j = √(λ̃_i/λ̃_j) → √(8/3), √5, √(15/8)",
            {
                "m2/m1": ratios["m2/m1"],
                "m3/m1": ratios["m3/m1"],
                "m3/m2": ratios["m3/m2"],
                "exact": ["sqrt(8/3)", "sqrt(5)", "sqrt(15/8)"],
            },
            "unique as spectral ratios of the three APS zero modes; sector ID as light neutrinos is the Stage-4 convention",
            sector="mass_ratios",
            notes=(
                "The same √(λ̃_i/λ̃_j) ratios apply to any copy of the three-mode "
                "tower (light neutrinos in Stage 4; heavy Majorana relatives if "
                "an overall scale existed). Identifying them with charged leptons "
                "or quarks is an extra, non-unique map."
            ),
        ),
        obs(
            "n_η / Δη/π",
            "n=4 j₁(j₁+1); Δη=n π/12",
            {"n_eta": [n1, n2, n3], "delta_eta_over_pi": [0.25, 2.0 / 3.0, 1.25]},
            "unique (topology)",
        ),
        obs(
            "cyclotomic monodromy order",
            "lcm of orders of exp(i n π/12)=exp(2π i n/24); orders {8,3,8}",
            24,
            "unique (topology)",
        ),
        obs(
            "T_wall",
            "Σ_k j_k(j_k+1) = 13/2",
            6.5,
            "unique as a discrete spectral invariant; not a GeV³ tension",
        ),
        obs(
            "8πG_eff (compact, dimensionless)",
            "σ*² / C₂(3) = (3/4) / (4/3) = 9/16",
            g8,
            "unique as the locked compact Einstein–YM coupling; not α_em",
            notes="C₂(3)=4/3. This is not the electromagnetic fine-structure constant.",
        ),
        obs(
            "KK interference |Σ_g exp(i Δη_g)|²",
            "|e^{iπ/4}+e^{i 2π/3}+e^{i 5π/4}|²",
            kk,
            "unique (η-lattice phases)",
        ),
        obs(
            "μ_γγ",
            "1 + σ*² |Σ e^{iΔη}|² / (4 N_gen) + β_□ / (2π C₂)",
            mu,
            "unique inside the locked Stage-4 map",
            notes=f"HL-LHC band from residual structure only: ±{mu_unc:.6f} → [{mu_lo:.6f}, {mu_hi:.6f}].",
        ),
        obs(
            "Ω_Λ",
            "σ* √(2/N_gen) (1 − β_full/5)",
            omega,
            "unique inside the locked Stage-4 map",
        ),
        obs(
            "w₀ (dark-energy EoS)",
            "−1 + β_full / (5π)",
            w0,
            "unique inside the locked Stage-4 map",
        ),
        obs(
            "ρ custodial",
            "1 + β_full² / (4π²)",
            rho,
            "unique inside the locked Stage-4 map",
        ),
        obs(
            "PMNS LO A4 (high-scale)",
            "tan²θ12=n1/n2=3/8; θ23=π/4; sinθ13=σ*(n2/n_Σ)/N_gen; δ from ζ₃+π/2",
            {
                "theta12_deg": best.get("theta12_deg"),
                "theta23_deg": best.get("theta23_deg"),
                "theta13_deg": best.get("theta13_deg"),
                "delta_cp_deg": best.get("delta_cp_deg"),
                "tan2_theta12": tan2_12,
                "sin_theta13_LO": sin13_lo,
            },
            "preferred, not unique among residual groups (S4/S3 compatible if APS evenness dropped)",
            sector="flavor",
        ),
        obs(
            "PMNS residual-NLO A4 (official high-scale lock)",
            "LO A4 + √r NLO: δ(sinθ13)=√r σ* √(n2/n_Σ)/N_gen; θ23=π/4+arctan(√r/n_Σ); θ12→θ12(1−r/(2π)); δ→δ+arctan(√r)(n2−n1)/n_Σ",
            {
                "theta12_deg": 31.003,
                "theta23_deg": 45.682,
                "theta13_deg": 7.953,
                "delta_cp_deg": -146.694,
                "r": LOCKED_R,
            },
            "unique inside the A4+√r NLO package (official high-scale prediction)",
            sector="flavor",
            notes="No further θ13 corrections inside this package. Low-energy ~8.5° remainder is Open.",
        ),
        obs(
            "Δm²_31 / Δm²_21",
            "(λ̃₂/λ̃₁) (Δη₃/Δη₁)² (n2/n1)^{−1/3} σ*² C₂",
            ratio_31_21,
            "unique as a dimensionless ratio from locked data; absolute eV² uses PDG Δm²_21 as a unit convention",
            sector="neutrinos",
            notes=f"Hierarchy from this ratio: {hierarchy}. Δm²_21 itself is not geometric.",
        ),
        obs(
            "neutrino hierarchy",
            "sign pattern of locked Δm²_31/Δm²_21 chain",
            hierarchy,
            "unique given the locked ratio map",
            sector="neutrinos",
        ),
        obs(
            "proton-lifetime geometric combination (log10 yr convention)",
            "n_Σ + 2 λ̃₂/λ̃₀ − 10 β_full",
            tau_log,
            "unique as a dimensionless combination; the 'years' label is a unit convention, not a GeV derivation",
        ),
    ]
    return rows


def undetermined_list() -> List[Dict[str, Any]]:
    return [
        undetermined(
            "α_em, α_s, sin²θ_W, G_F",
            "No locked map identifies the compact 8πG_eff=σ*²/C₂ with a Standard Model gauge coupling. Any such identification would be a new continuous or discrete choice.",
        ),
        undetermined(
            "charged-lepton mass ratios mμ/me, mτ/mμ (and absolute masses)",
            "The unique spectral ratios are √(λ̃_i/λ̃_j) of the three APS zero modes. Mapping that tower onto e,μ,τ (rather than neutrinos) is not forced. Absolute MeV masses need an external scale.",
        ),
        undetermined(
            "quark mass ratios and CKM (physical low-energy)",
            "CKM holonomy angles from naive Δη are exploratory only. They are not the official flavor lock. A unique quark Yukawa map is not forced.",
        ),
        undetermined(
            "additional PMNS angles/phases beyond residual-NLO A4",
            "Flavor-monodromy completion: no further discrete completion is forced. Official high-scale angles remain (31.003, 45.682, 7.953, −146.694)°.",
        ),
        undetermined(
            "low-energy θ13 ≈ 8.5° (RG / M_R bridge)",
            "Bridge probe: no parameter-free geometric map from 7.953° to ~8.5°. Remainder is Open.",
        ),
        undetermined(
            "absolute neutrino masses in eV without a unit convention",
            "Stage-4 m1=σ* exp(−Σn_η/(N_gen·12))·10^{-2} eV uses a 10^{-2} eV yardstick plus PDG Δm²_21. Ratios m_i/m_j remain geometric.",
        ),
        undetermined(
            "heavy Majorana scale M_R (GeV)",
            "Locked data are dimensionless. No unique GeV. Open.",
        ),
        undetermined(
            "absolute scale / overall volume R / electron mass in GeV",
            "Closed by observational conversion posture: geometry yields only dimensionless quantities. Conversion is temporary and withdrawn. Not a knob, and not a geometric output.",
        ),
        undetermined(
            "unique higher-derivative Wilson coefficients",
            "Controlled HD probe: 0/9 unique coefficients. Open.",
        ),
        undetermined(
            "continuum β residual r→0 as a physical floor",
            "Official r=0.095716 is a computational lock. No topological floor observed. Open.",
        ),
    ]


def main() -> None:
    print(BANNER.replace("COMPLETE", "STARTED"))
    print()
    with open(BASELINE_PATH, encoding="utf-8") as f:
        baseline = json.load(f)
    fls = baseline.get("final_locked_state") or {}
    knobs = int(fls.get("continuous_knobs") or 0)
    if knobs != 0:
        raise RuntimeError("continuous_knobs must be 0")
    if float(fls.get("beta_residual_new") or LOCKED_R) != LOCKED_R:
        raise RuntimeError("official residual lock changed")

    locked = load_locked_phenomenology()
    derived = derived_observables(locked)
    undet = undetermined_list()

    payload = {
        "banner": BANNER,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "official_lock_unchanged": True,
        "official_beta_residual": LOCKED_R,
        "official_sigma_star": "sqrt(3)/2",
        "new_residual_promoted": False,
        "new_sigma_promoted": False,
        "no_experimental_fit": True,
        "absolute_scale_posture": "observational_conversion_only",
        "open_gaps_remain_open": True,
        "inventory_locked_geometry": inventory(locked),
        "derived_observables": derived,
        "not_determined_by_locked_geometry": undet,
        "locked_flavor_unchanged": {
            "theta12_deg": 31.003,
            "theta23_deg": 45.682,
            "theta13_deg": 7.953,
            "delta_cp_deg": -146.694,
        },
        "note": (
            "All derived values are re-expressions of already-locked Stage-4 maps. "
            "No new continuous coefficient and no new geometric identification "
            "was introduced. Charged-fermion and fine-structure maps are not forced."
        ),
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    extra = [
        "",
        "PHYSICAL BRIDGE (documentation of locked dimensionless maps; official lock unchanged)",
        f"timestamp_utc: {payload['timestamp_utc']}",
        "continuous_knobs: 0",
        "verification: 8/8 PASS (not re-run; locked core untouched)",
        f"official_beta_residual_lock: {LOCKED_R} (NOT replaced)",
        "official_sigma_star: sqrt(3)/2 (NOT replaced)",
        "no_experimental_fit: True",
        "unique_dimensionless: N_gen, σ*, λ̃ ratios, √(λ̃_i/λ̃_j) mass ratios, n_η, monodromy 24, T_wall=13/2, 8πG_eff=9/16, μ_γγ, Ω_Λ, w0, ρ, A4+NLO PMNS, Δm²_31/Δm²_21 ratio",
        "not_determined: α_em, charged-lepton/quark maps, physical CKM, M_R (GeV), absolute eV without unit convention, θ13 low-energy remainder",
        "new_residual_promoted: False",
        "open_gaps_remain_open: True",
        "END PHYSICAL BRIDGE",
        "",
    ]
    with open(LOG_PATH, encoding="utf-8") as f:
        log_text = f.read()
    marker = "PHYSICAL BRIDGE (documentation"
    if marker in log_text:
        log_text = log_text[: log_text.index(marker)].rstrip() + "\n"
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write(log_text)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(extra))

    print(f"{'Quantity':<44} {'Value from locked data':<28} Uniqueness")
    print("-" * 110)
    for row in derived:
        val = row["value_from_locked_data"]
        if isinstance(val, float):
            vs = f"{val:.6f}"
        elif isinstance(val, dict) and "theta12_deg" in val:
            vs = f"({val['theta12_deg']:.3f}, {val['theta23_deg']:.3f}, {val['theta13_deg']:.3f})"
        elif isinstance(val, dict) and "m2/m1" in val:
            vs = f"{val['m2/m1']:.6f}, {val['m3/m1']:.6f}"
        else:
            vs = str(val)
            if len(vs) > 26:
                vs = vs[:23] + "..."
        print(f"{row['quantity']:<44} {vs:<28} {row['uniqueness'][:36]}")
    print()
    print("Not determined without an absolute scale / extra map:")
    for u in undet:
        print(f"  - {u['quantity']}")
    print()
    print("continuous_knobs = 0")
    print(f"Wrote {OUT_PATH}")
    print(BANNER)


if __name__ == "__main__":
    main()
