#!/usr/bin/env python3
"""
Type Layer-A moduli from T1–T7. No pre-filled types. No complete_baseline write.
"""

from __future__ import annotations

from typing import Any, Dict, List

LEGAL_TYPES = ("FORCED", "GAUGE", "CLASS", "OPEN-FIELD", "FORBIDDEN")


def _row(name: str, typ: str, source: str, value_forced: bool, physics_reading: str, notes: str) -> Dict[str, Any]:
    if typ not in LEGAL_TYPES:
        raise ValueError(typ)
    return {
        "name": name,
        "type": typ,
        "source": source,
        "value_forced": bool(value_forced and typ == "FORCED"),
        "physics_reading": physics_reading,
        "notes": notes,
    }


def type_menu(locked: Dict[str, Any], ports: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply T1–T7 to named candidates. free_fit_alpha is unlisted (T7)."""
    rows: List[Dict[str, Any]] = []
    t_n = str(ports.get("T_wall_from_n") or ports.get("numeric", {}).get("T_wall_from_n"))
    t_l = str(ports.get("T_wall_from_lam") or ports.get("numeric", {}).get("T_wall_from_lam"))
    agree = t_n == t_l and t_n not in {"None", ""}
    sig2 = str(ports.get("sigma_star_sq") or ports.get("numeric", {}).get("sigma_star_sq"))
    geff = str(ports.get("eight_pi_G_eff") or ports.get("numeric", {}).get("eight_pi_G_eff"))

    # T1 locked fields / identities
    rows.append(_row("N_gen", "FORCED", "T1 complete_baseline", True, "none", "locked field"))
    rows.append(_row("n_eta", "FORCED", "T1 complete_baseline", True, "none", "locked field"))
    rows.append(_row("sigma_star", "FORCED", "T1 complete_baseline", True, "T^{1,1} shape, not g_μν", "locked field"))
    if agree:
        rows.append(
            _row(
                "T_wall_identity",
                "FORCED",
                "T1 Fraction Σ n_η/4 = Σ λ̃/6",
                True,
                "not Chern, not GeV^3",
                f"{t_n}",
            )
        )
    else:
        rows.append(
            _row(
                "T_wall_identity",
                "FORBIDDEN",
                "T1 sums disagree (live finding)",
                False,
                "not Chern, not GeV^3",
                f"{t_n} vs {t_l}",
            )
        )
    rows.append(_row("Iso_group", "FORCED", "T1 locked 5-fold isometry", True, "not color", "SU(2)×SU(2)×U(1)"))
    rows.append(_row("b2", "FORCED", "T1 topology T^{1,1}≃S²×S³", True, "not flux", "Betti"))
    rows.append(_row("b3", "FORCED", "T1 topology T^{1,1}≃S²×S³", True, "not flux", "Betti"))
    rows.append(
        _row(
            "eight_pi_G_eff_number",
            "FORCED",
            "T1 σ*²/C2(3)",
            True,
            "pure number, not G_N",
            geff,
        )
    )

    # T2 physics readings of identities — not FORCED
    rows.append(_row("T_wall_as_Chern", "FORBIDDEN", "T2 reading", False, "Chern", "standing law"))
    rows.append(_row("T_wall_as_GeV3", "FORBIDDEN", "T2 reading", False, "GeV^3", "standing law"))
    rows.append(_row("eight_pi_G_eff_as_G_N", "FORBIDDEN", "T2 reading", False, "G_N", "standing law"))
    rows.append(_row("b2_b3_as_flux", "FORBIDDEN", "T2 reading", False, "flux", "standing law"))
    rows.append(_row("Iso_as_color", "FORBIDDEN", "T2/T4 reading", False, "color", "standing law"))

    # T6 gauge
    rows.append(_row("Weyl_lambda", "GAUGE", "T6 Weyl quotient", False, "not R in meters", "observer not adjuster"))
    rows.append(_row("overall_R", "GAUGE", "T6 observational conversion", False, "not dynamical freeze", "stick withdrawn"))

    # T3 uniqueness failed
    rows.append(_row("leftover_X4_family", "CLASS", "T3 family remains", False, "not a unique 4-fold", "K3/CP2/T4 unnamed pick"))
    rows.append(_row("CP2_as_the_4fold", "FORBIDDEN", "T3 named pick", False, "the 4-fold", "unique pick failed"))
    rows.append(_row("K3_as_the_4fold", "FORBIDDEN", "T3 named pick", False, "the 4-fold", "unique pick failed"))

    # T4 standing law
    rows.append(_row("unique_color", "FORBIDDEN", "T4", False, "unique SU(3)_c", "not derived"))
    rows.append(_row("G_SM_from_isolate", "FORBIDDEN", "T4", False, "G_SM", "not forced"))
    rows.append(_row("sigma_star_equals_g_mu_nu", "FORBIDDEN", "T4", False, "spacetime metric", "σ* is not g_μν"))

    # T5 symbol allowed, value not forced
    rows.append(_row("warp_factor", "OPEN-FIELD", "T5", False, "warp A", "eligible != determined"))
    rows.append(_row("g_mu_nu", "OPEN-FIELD", "T5", False, "4D metric symbol", "eligible != determined"))

    # T7 free_fit_alpha unlisted — not appended
    return rows
