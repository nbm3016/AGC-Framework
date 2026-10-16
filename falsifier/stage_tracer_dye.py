#!/usr/bin/env python3
"""
Phase II — Tracer Dye Diagnostic (Temporary Planck Scale Injection).

Goal: Temporarily inject M_Pl solely as a diagnostic tracer to expose where
an absolute scale must couple to the locked geometry. Map structural
intersection points, withdraw M_Pl completely, then search for pure
topological features that could occupy the same slots.

Strict rules:
  - M_Pl is temporary diagnostic only.
  - After mapping, external scale is fully withdrawn.
  - Final reported mechanism (if any) has no continuous parameter and no M_Pl.
  - continuous_knobs remain exactly 0 in the final result.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, List, Optional

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
COMPLETE_BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
TRACER_PATH = os.path.join(ARTIFACT_DIR, "tracer_dye_diagnostic.json")

C2_SU3 = 4.0 / 3.0
SIGMA_STAR = math.sqrt(3.0) / 2.0
BETA_RESIDUAL_LOCKED = 0.095716
MONODROMY_ORDER = 24

# Diagnostic only — never retained in final equations
M_PL_TRACER_GEV = 1.220910e19  # conventional Planck mass (GeV), tracer dye only


def load_locked() -> Dict[str, Any]:
    with open(COMPLETE_BASELINE_PATH, encoding="utf-8") as f:
        b = json.load(f)
    if b.get("status") != "PASS":
        raise ValueError("complete_baseline.json not PASS")
    return b


def locked_pure_numbers(baseline: Dict[str, Any]) -> Dict[str, Any]:
    lr = baseline.get("locked_results") or {}
    sigma = float(lr.get("sigma_star") or SIGMA_STAR)
    lams = list(lr.get("lambda_targets") or [4.5, 12.0, 22.5])
    n_eta = list(lr.get("n_eta_triple") or [3, 8, 15])
    r = float(lr.get("beta_residual_new") or BETA_RESIDUAL_LOCKED)
    n_gen = int(lr.get("n_gen") or lr.get("n_gen_native_aps_index") or 3)
    g8 = float(lr.get("eight_pi_g_eff") or (sigma ** 2 / C2_SU3))
    t_wall = sum(j * (j + 1.0) for j in (0.5, 1.0, 1.5)[:n_gen])
    tau_res = r * sigma * sigma
    return {
        "sigma_star": sigma,
        "lambda_tilde": lams,
        "n_eta": n_eta,
        "n_eta_sum": sum(n_eta),
        "beta_residual_new": r,
        "n_gen": n_gen,
        "eight_pi_g_eff": g8,
        "T_wall": t_wall,
        "tau_res": tau_res,
        "monodromy_order": MONODROMY_ORDER,
    }


def phase_a_tracer_injection(nums: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Phase A (temporary): insert M_Pl into locked residual / wall / self-dual /
    APS structures in the most natural geometric ways. Map where the
    dimensionful unit is forced to couple.
    """
    M = M_PL_TRACER_GEV
    sigma = nums["sigma_star"]
    r = nums["beta_residual_new"]
    t_wall = nums["T_wall"]
    tau = nums["tau_res"]
    g8 = nums["eight_pi_g_eff"]
    lams = nums["lambda_tilde"]
    n_gen = nums["n_gen"]
    n_sum = nums["n_eta_sum"]

    points: List[Dict[str, Any]] = []

    # --- Hole 1: residual tension → vacuum energy density ---
    # τ_res is dimensionless; ρ_vac needs mass⁴ → ρ ~ τ_res M_Pl⁴
    points.append(
        {
            "id": "H1_residual_tension_to_vacuum_energy",
            "structure": "residual tension τ_res = r·σ*²",
            "tracer_equation": "ρ_vac^(diag) = τ_res · M_Pl⁴",
            "why_M_Pl_couples": (
                "Einstein equation / vacuum energy density has mass dimension 4; "
                "locked τ_res is a pure number. Converting residual stress into "
                "physical energy density requires an absolute mass⁴ unit. M_Pl is "
                "the natural 4D gravitational unit when residual stress is read as "
                "a contribution to the Einstein tensor."
            ),
            "dimensional_hole": "[ρ] = mass⁴  vs  [τ_res] = 1",
            "tracer_value_note": f"τ_res={tau:.6f}; ρ would be τ_res·M_Pl⁴ (diagnostic only)",
            "locked_pure_input": {"tau_res": tau, "r": r, "sigma_star": sigma},
        }
    )

    # --- Hole 2: domain-wall tension → surface energy / volume potential ---
    points.append(
        {
            "id": "H2_domain_wall_tension_to_surface_energy",
            "structure": "Σ⁵ domain-wall spectral tension T_wall = Σ Vol_k",
            "tracer_equation": "T_phys^(diag) = T_wall · M_Pl³   (or T_wall · M_Pl⁴ · L if L~1/M_Pl)",
            "why_M_Pl_couples": (
                "Physical domain-wall surface energy has dimension mass³ (in 4D "
                "effective description) or mass⁴×length. Locked T_wall is a spectral "
                "volume sum (pure number). Matching to a physical wall requires a "
                "fundamental mass unit; M_Pl is the natural gravitational / compactification "
                "unit for the wall action term ∫ T √γ."
            ),
            "dimensional_hole": "[T_phys] = mass³ (or mass⁴·length)  vs  [T_wall] = 1",
            "tracer_value_note": f"T_wall={t_wall:.4f}",
            "locked_pure_input": {"T_wall": t_wall, "n_gen": n_gen},
        }
    )

    # --- Hole 3: 8πG_eff → Newton constant / Planck identification ---
    points.append(
        {
            "id": "H3_eight_pi_G_eff_to_Newton",
            "structure": "8πG_eff = σ*²/C₂(3) (dimensionless code ratio)",
            "tracer_equation": "G_N^(diag) = (8πG_eff) / M_Pl²   or   8πG_N = 1/M_Pl² with code ratio absorbed",
            "why_M_Pl_couples": (
                "Newton's constant has dimension mass⁻². The locked 8πG_eff is only "
                "the dimensionless ratio σ*²/C₂. Identifying the Einstein–Hilbert "
                "coefficient with observed gravity forces an absolute mass unit M_Pl."
            ),
            "dimensional_hole": "[G_N] = mass⁻²  vs  [8πG_eff] = 1",
            "tracer_value_note": f"8πG_eff={g8:.6f}",
            "locked_pure_input": {"eight_pi_g_eff": g8, "sigma_star": sigma},
        }
    )

    # --- Hole 4: spectral gap → physical KK / Dirac mass ---
    points.append(
        {
            "id": "H4_spectral_gap_to_physical_mass",
            "structure": "APS / Laplacian eigenvalues λ̃ on unit Σ⁵",
            "tracer_equation": "m_k^(diag) = √λ̃_k · M_Pl / R̃   (R̃ = compact radius in Planck units)",
            "why_M_Pl_couples": (
                "Spectral eigenvalues λ̃ are dimensionless on the unit manifold. "
                "Physical masses require m ~ √λ̃ / L with L a length. Writing L = R̃/M_Pl "
                "exposes that either M_Pl or an equivalent absolute inverse-length must "
                "enter. If R̃ is O(1), the hole is filled only by M_Pl itself."
            ),
            "dimensional_hole": "[m] = mass  vs  [√λ̃] = 1  (needs 1/L)",
            "tracer_value_note": f"√λ̃₀={math.sqrt(lams[0]):.6f}; ratios √(λ̃_k/λ̃_0) fixed without M_Pl",
            "locked_pure_input": {
                "lambda_tilde": lams,
                "sqrt_lambda_0": math.sqrt(lams[0]),
            },
        }
    )

    # --- Hole 5: Casimir / volume potential V(R) ---
    points.append(
        {
            "id": "H5_casimir_volume_potential",
            "structure": "Casimir-like V ~ (Σ λ̃²)/R⁴ on overall volume modulus",
            "tracer_equation": "V_phys^(diag) = (Σ λ̃²) · M_Pl⁴ / R̃⁴",
            "why_M_Pl_couples": (
                "Restoring dimensions to the scale-free Casimir functional always "
                "introduces M_Pl⁴ (or another mass⁴) times a function of the "
                "dimensionless radius R̃ = R·M_Pl. Without M_Pl (or equivalent), "
                "V remains a pure number, not an energy density."
            ),
            "dimensional_hole": "[V] = mass⁴  vs  [Σλ̃²/R̃⁴] needs mass⁴ unit",
            "tracer_value_note": f"Σλ̃²={sum(x*x for x in lams):.2f}",
            "locked_pure_input": {"sum_lambda_sq": sum(x * x for x in lams)},
        }
    )

    # --- Hole 6: residual NLO flavor is dimensionless (control — no hole for angles) ---
    points.append(
        {
            "id": "H6_residual_NLO_flavor_angles",
            "structure": "residual NLO A4 mixing (√r, σ*, n_η, N_gen)",
            "tracer_equation": "θ_ij^(NLO) = f(r, σ*, n_η, N_gen)   [no M_Pl]",
            "why_M_Pl_couples": (
                "CONTROL POINT: mixing angles are dimensionless. The residual NLO "
                "map already closes without any absolute scale. Tracer dye does not "
                "couple here — this is a filled dimensionless slot, not a hole."
            ),
            "dimensional_hole": "none — [θ] = 1 already matched",
            "tracer_value_note": "θ13=7.953° locked; M_Pl not required",
            "locked_pure_input": {"r": r, "sigma_star": sigma, "n_gen": n_gen},
            "is_control_not_hole": True,
        }
    )

    # --- Hole 7: instanton / nonperturbative prefactor ---
    points.append(
        {
            "id": "H7_instanton_prefactor",
            "structure": "nonperturbative factor exp(−T_wall) or exp(−1/r)",
            "tracer_equation": "Λ_np^(diag) = M_Pl · exp(−T_wall)   or   M_Pl · exp(−1/r)",
            "why_M_Pl_couples": (
                "Exponential suppressions are pure numbers; the prefactor that turns "
                "them into a mass or Λ_QCD-like scale is an absolute mass unit. "
                "M_Pl is the default gravitational UV cutoff used as tracer."
            ),
            "dimensional_hole": "[Λ_np] = mass  vs  [e^{−S}] = 1",
            "tracer_value_note": (
                f"exp(-T_wall)={math.exp(-t_wall):.6e}; "
                f"exp(-1/r)={math.exp(-1.0/r):.6e}"
            ),
            "locked_pure_input": {
                "exp_minus_T_wall": math.exp(-t_wall),
                "exp_minus_1_over_r": math.exp(-1.0 / r),
            },
        }
    )

    # --- Hole 8: warp hierarchy physical IR scale ---
    warp = math.exp(float(n_sum) * sigma / n_gen)
    points.append(
        {
            "id": "H8_warp_hierarchy_IR_anchor",
            "structure": "warp factor W = exp(n_Σ·σ*/N_gen) from η-lattice + σ*",
            "tracer_equation": "Λ_IR^(diag) = M_Pl · W^{−1}   or   M_Pl · W",
            "why_M_Pl_couples": (
                "Warp fixes only the ratio Λ_IR/Λ_UV. Anchoring either end of the "
                "hierarchy requires an absolute scale; tracer places M_Pl at the UV."
            ),
            "dimensional_hole": "[Λ_IR] = mass  vs  [W] = 1",
            "tracer_value_note": f"W={warp:.6e}",
            "locked_pure_input": {"warp_factor": warp, "n_eta_sum": n_sum},
        }
    )

    # --- Hole 9: self-dual ⋆Ψ=Ψ does not force mass (control) ---
    points.append(
        {
            "id": "H9_self_dual_projection",
            "structure": "self-duality ⋆Ψ=Ψ and APS index",
            "tracer_equation": "⋆Ψ=Ψ,  index(D_APS)=0   [projector / integer; no M_Pl]",
            "why_M_Pl_couples": (
                "CONTROL POINT: self-duality and APS index are topological / projector "
                "conditions. They select discrete mode content (N_gen=3) without "
                "introducing mass dimension. Tracer dye does not couple."
            ),
            "dimensional_hole": "none — topological selection is scale-free",
            "tracer_value_note": "N_gen=3 native; j2=0 sector",
            "locked_pure_input": {"n_gen": n_gen, "monodromy_order": MONODROMY_ORDER},
            "is_control_not_hole": True,
        }
    )

    # --- Hole 10: APS barrier / wall position in physical length ---
    points.append(
        {
            "id": "H10_APS_wall_physical_thickness",
            "structure": "APS domain-wall locus on Σ⁵ (topologically fixed position in field space)",
            "tracer_equation": "L_wall^(diag) = ℓ_* / M_Pl   with ℓ_* = σ*/√r or 1/√T_wall (pure)",
            "why_M_Pl_couples": (
                "Wall position is topologically fixed in dimensionless field coordinates. "
                "Converting that locus into a physical thickness/length requires 1/M_Pl "
                "(or another inverse-mass unit)."
            ),
            "dimensional_hole": "[L] = mass⁻¹  vs  [ℓ_*] = 1",
            "tracer_value_note": (
                f"ℓ_* proxies: 1/√T_wall={1/math.sqrt(t_wall):.6f}, "
                f"σ*/√r={sigma/math.sqrt(r):.6f}"
            ),
            "locked_pure_input": {
                "inv_sqrt_T_wall": 1.0 / math.sqrt(t_wall),
                "sigma_over_sqrt_r": sigma / math.sqrt(r),
            },
        }
    )

    return points


def phase_b_withdraw_and_replace(
    coupling_points: List[Dict[str, Any]],
    nums: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Phase B: completely remove M_Pl. For each coupling point (excluding pure
    controls), search for a pure topological / residual feature that could fill
    the same structural role without any external scale.
    """
    r = nums["beta_residual_new"]
    t_wall = nums["T_wall"]
    tau = nums["tau_res"]
    lams = nums["lambda_tilde"]
    g8 = nums["eight_pi_g_eff"]
    n_gen = nums["n_gen"]
    sigma = nums["sigma_star"]
    n_sum = nums["n_eta_sum"]
    warp = math.exp(float(n_sum) * sigma / n_gen)

    replacements: List[Dict[str, Any]] = []

    # Search map: candidate pure fillers already in locked data
    pure_candidates = {
        "tau_res": tau,
        "T_wall": t_wall,
        "r": r,
        "eight_pi_g_eff": g8,
        "sqrt_lambda_0": math.sqrt(lams[0]),
        "sum_lambda_sq": sum(x * x for x in lams),
        "n_gen": n_gen,
        "monodromy_order": MONODROMY_ORDER,
        "warp_factor": warp,
        "exp_minus_T_wall": math.exp(-t_wall),
        "N_gen_times_T_wall": n_gen * t_wall,
        "r_times_T_wall": r * t_wall,
    }

    for p in coupling_points:
        pid = p["id"]
        is_control = bool(p.get("is_control_not_hole"))

        if is_control:
            replacements.append(
                {
                    "coupling_point_id": pid,
                    "structure": p["structure"],
                    "is_dimensional_hole": False,
                    "pure_topological_replacement_found": True,
                    "replacement_form": (
                        "Already closed by pure geometry / topology "
                        f"({p['structure']}); no absolute unit required."
                    ),
                    "contains_M_Pl": False,
                    "contains_continuous_parameter": False,
                    "status": "no_hole_control_point",
                    "notes": p["why_M_Pl_couples"],
                }
            )
            continue

        # Dimensional holes: can a pure number occupy a mass-dimension slot?
        # Honest answer: no pure number has mass dimension.
        # Check if any locked structure is *already* dimensionful — none are.
        found = False
        form = None
        reason = (
            "After withdrawal of M_Pl, every locked pure number "
            f"({', '.join(pure_candidates.keys())}) still has mass dimension 0. "
            "None can fill a structural slot that requires [mass], [mass²], "
            "[mass³], or [mass⁴]. Replacing M_Pl by τ_res, T_wall, r, √λ̃, "
            "or monodromy order would be a unitless placeholder, not a "
            "dimensionally consistent absolute scale."
        )

        # Explicit per-hole checks for any *non-dimensionful* structural substitute
        # that might still close the *equation form* without needing energy units
        # (e.g. if the physics only needed a pure-number stabilizer).
        if pid == "H1_residual_tension_to_vacuum_energy":
            # Could τ_res alone act as Ω_Λ without M_Pl? Stage-4 already maps residual
            # structure into dimensionless Ω_Λ — that path is ratios, not absolute ρ.
            form_attempt = "ρ_vac / ρ_* = τ_res  (ratio only; ρ_* still free)"
            reason = (
                f"Locked τ_res={tau:.6f} can fix a *dimensionless* vacuum fraction "
                "relative to an unspecified ρ_* (as Stage-4 Ω_Λ does). It cannot "
                "set absolute ρ_vac without mass⁴. No pure topological filler for "
                "the absolute energy-density hole."
            )
            found = False
            form = None
            attempted_ratio_only = form_attempt
        elif pid == "H2_domain_wall_tension_to_surface_energy":
            form_attempt = "T_phys / scale³ = T_wall  (ratio only)"
            reason = (
                f"T_wall={t_wall:.4f} fixes relative wall strength among spectral "
                "sectors and topological freeze of wall *position* in field space, "
                "but not absolute surface energy."
            )
            found = False
            form = None
            attempted_ratio_only = form_attempt
        elif pid == "H3_eight_pi_G_eff_to_Newton":
            form_attempt = "G_code = σ*²/C₂  (already locked dimensionless)"
            reason = (
                "The dimensionless Einstein–YM ratio is already fixed. The hole is "
                "the conversion of that ratio into dimensionful G_N; no topological "
                "integer supplies mass⁻²."
            )
            found = False
            form = None
            attempted_ratio_only = form_attempt
        elif pid == "H4_spectral_gap_to_physical_mass":
            form_attempt = "m_k / m_1 = √(λ̃_k/λ̃_1)  (ratios only)"
            reason = (
                "APS spectrum uniquely fixes mass *ratios*. Absolute m_k still needs "
                "1/L. Volume modulus R remains flat, so no pure geometric L emerges."
            )
            found = False
            form = None
            attempted_ratio_only = form_attempt
        elif pid == "H5_casimir_volume_potential":
            form_attempt = "V_code(R̃) = (Σλ̃²)/R̃⁴  (scale-free shape; no absolute min)"
            reason = (
                "Even after fixing the functional *shape* with locked λ̃, the potential "
                "is homogeneous in overall radius and has no stable finite-R minimum "
                "without a second independent scale (prior volume-squeeze negative)."
            )
            found = False
            form = None
            attempted_ratio_only = form_attempt
        elif pid == "H7_instanton_prefactor":
            form_attempt = "suppression = exp(−T_wall) or exp(−1/r)  (pure number)"
            reason = (
                "Nonperturbative *exponents* are fixed by locked T_wall and r. "
                "The absolute prefactor mass remains unfilled."
            )
            found = False
            form = None
            attempted_ratio_only = form_attempt
        elif pid == "H8_warp_hierarchy_IR_anchor":
            form_attempt = f"Λ_IR/Λ_UV = W or 1/W with W={warp:.6e}"
            reason = (
                "Warp factor from n_η and σ* is a pure hierarchy ratio. UV or IR "
                "anchor scale is not topological."
            )
            found = False
            form = None
            attempted_ratio_only = form_attempt
        elif pid == "H10_APS_wall_physical_thickness":
            form_attempt = "ℓ_* = σ*/√r or 1/√T_wall  (dimensionless thickness proxy)"
            reason = (
                "APS fixes wall locus in field space and pure-number thickness "
                "proxies. Physical length still needs mass⁻¹."
            )
            found = False
            form = None
            attempted_ratio_only = form_attempt
        else:
            attempted_ratio_only = None

        replacements.append(
            {
                "coupling_point_id": pid,
                "structure": p["structure"],
                "is_dimensional_hole": True,
                "tracer_equation_withdrawn": p["tracer_equation"].replace(
                    "M_Pl", "[WITHDRAWN]"
                ),
                "pure_topological_replacement_found": found,
                "replacement_form": form,
                "ratio_only_structure_still_available": attempted_ratio_only,
                "contains_M_Pl": False,
                "contains_continuous_parameter": False,
                "status": "hole_unfilled_by_pure_geometry",
                "notes": reason,
                "pure_numbers_examined": pure_candidates,
            }
        )

    return replacements


def analyze_tracer_dye(baseline: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    b = baseline or load_locked()
    nums = locked_pure_numbers(b)

    # Phase A: temporary injection (diagnostic map only)
    coupling_points = phase_a_tracer_injection(nums)

    # Phase B: withdraw M_Pl and search replacements
    replacements = phase_b_withdraw_and_replace(coupling_points, nums)

    holes = [r for r in replacements if r.get("is_dimensional_hole")]
    controls = [r for r in replacements if not r.get("is_dimensional_hole")]
    filled = [r for r in holes if r.get("pure_topological_replacement_found")]
    unfilled = [r for r in holes if not r.get("pure_topological_replacement_found")]

    # Final equations must not contain M_Pl
    final_status = (
        "Absolute scale generation remains NO. Tracer dye exposed dimensional "
        "coupling holes; after complete withdrawal of M_Pl, no pure topological "
        "feature fills those mass-dimension slots. Dimensionless sectors (flavor "
        "angles, APS index, self-duality) were already closed without a yardstick."
    )

    table = []
    for r in replacements:
        table.append(
            {
                "coupling_point": r["coupling_point_id"],
                "structure": r["structure"],
                "pure_topological_replacement_found": (
                    "Yes" if r["pure_topological_replacement_found"] else "No"
                ),
                "replacement_form": r.get("replacement_form")
                if r["pure_topological_replacement_found"]
                else None,
                "notes_short": (
                    "control (no dimensional hole)"
                    if not r.get("is_dimensional_hole")
                    else "dimensional hole unfilled"
                ),
            }
        )

    return {
        "banner": "TRACER DYE DIAGNOSTIC COMPLETE – EXTERNAL SCALE WITHDRAWN",
        "continuous_knobs": 0,
        "M_Pl_in_final_equations": False,
        "external_scale_status": "withdrawn",
        "tracer_phase": {
            "status": "temporary_only",
            "M_Pl_tracer_GeV_used_for_map_only": M_PL_TRACER_GEV,
            "note": (
                "M_Pl appears only in Phase A diagnostic tracer equations. "
                "It is not retained in any final locked equation or mechanism."
            ),
            "coupling_points_mapped": coupling_points,
        },
        "withdrawal_phase": {
            "status": "complete",
            "M_Pl_removed": True,
            "replacements": replacements,
        },
        "summary": {
            "n_structures_probed": len(coupling_points),
            "n_dimensional_holes": len(holes),
            "n_control_points_already_closed": len(controls),
            "n_holes_filled_by_pure_topology": len(filled),
            "n_holes_unfilled": len(unfilled),
            "unfilled_hole_ids": [u["coupling_point_id"] for u in unfilled],
            "control_point_ids": [c["coupling_point_id"] for c in controls],
        },
        "decision_table": table,
        "absolute_scale_generation_final_status": "NO",
        "statement": final_status,
        "what_tracer_revealed": [
            "Absolute scale must couple wherever mass dimension is required: "
            "vacuum energy (mass⁴), wall surface energy (mass³), G_N (mass⁻²), "
            "physical masses/lengths (mass / mass⁻¹), instanton prefactor (mass), "
            "warp anchors (mass).",
            "Dimensionless locked predictions (θ_ij, N_gen, σ*, monodromy, "
            "APS projectors) do not require the tracer.",
            "After withdrawal, pure geometry still only supplies pure numbers "
            "and ratios — the dimensional holes remain structural.",
        ],
        "locked_pure_numbers_used": nums,
    }


def decision_table_text(analysis: Dict[str, Any]) -> str:
    lines = [
        "=" * 88,
        analysis["banner"],
        "=" * 88,
        "Phase A: M_Pl injected as temporary tracer → coupling map built",
        "Phase B: M_Pl completely withdrawn → pure topological replacement search",
        f"M_Pl in final equations: {analysis['M_Pl_in_final_equations']}",
        f"Continuous knobs: {analysis['continuous_knobs']}",
        f"Absolute scale generation (final): {analysis['absolute_scale_generation_final_status']}",
        "-" * 88,
        f"{'Coupling point':<42} {'Replacement?':<14} Form / status",
        "-" * 88,
    ]
    for row in analysis["decision_table"]:
        form = row["replacement_form"] or row["notes_short"]
        if form and len(form) > 40:
            form = form[:37] + "..."
        lines.append(
            f"{row['coupling_point']:<42} {row['pure_topological_replacement_found']:<14} {form}"
        )
    lines += [
        "-" * 88,
        f"Dimensional holes unfilled: {analysis['summary']['n_holes_unfilled']}/"
        f"{analysis['summary']['n_dimensional_holes']}",
        f"Control points (already closed, no M_Pl): "
        f"{analysis['summary']['n_control_points_already_closed']}",
        analysis["statement"],
        "=" * 88,
    ]
    return "\n".join(lines)


def save_result(analysis: Dict[str, Any]) -> str:
    # Ensure no accidental final retention of M_Pl in "final" keys
    payload = dict(analysis)
    payload["M_Pl_in_final_equations"] = False
    payload["continuous_knobs"] = 0
    with open(TRACER_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return TRACER_PATH


def main() -> None:
    print("Tracer dye diagnostic (temporary Planck injection) — starting\n")
    analysis = analyze_tracer_dye()
    print(decision_table_text(analysis))
    path = save_result(analysis)
    print(f"\nSaved {path}")
    print(analysis["banner"])


if __name__ == "__main__":
    main()
