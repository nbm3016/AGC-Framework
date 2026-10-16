#!/usr/bin/env python3
"""
Check engine: runCheck(claim, facts) -> {bin, gates, reasons}.

Refuse-gates fire from the YES-as-lock interpretation of a claim plus facts.
A fired refuse-gate => REFUSED. No override.
Bins: FORCED | CLASS | CONSISTENT | REFUSED | UNKNOWN
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

LEGAL = frozenset({"FORCED", "CLASS", "CONSISTENT", "REFUSED", "UNKNOWN"})
REFUSE_GATES = (
    "R-isolate-write",
    "R-knobs",
    "R-burn-list",
    "R-weld",
    "R-stick-left-in",
    "R-map-called-lock",
    "R-color-lock",
    "R-scale",
    "R-metric-swap",
    "R-rewrite-numeric",
    "R-unlisted-modulus",
    "R-modulus-called-lock",
)

ALLOWED_MODULUS_TYPES = frozenset({"FORCED", "GAUGE", "CLASS", "OPEN-FIELD"})
LEGAL_MODULUS_TYPES = frozenset({"FORCED", "GAUGE", "CLASS", "OPEN-FIELD", "FORBIDDEN"})

BURNED = (
    "Iso(T^{1,1})=SU(3)_c",
    "holonomy SU(3)=QCD",
    "chi=N_gen welded to CP2",
    "N_gen=dim of the 3 of SU(3)",
    "3 APS modes=45 SM Weyl",
    "C2(3) in V(sigma) as proof of color",
    "graph orbits=SM generations",
    "graph orbits=color",
)


def _fire(claim: Dict[str, Any], facts: Dict[str, Any]) -> List[Tuple[str, str]]:
    fired: List[Tuple[str, str]] = []
    yes = claim.get("yes_as_lock") or {}

    if yes.get("write_isolate") or claim.get("would_write_isolate"):
        fired.append(("R-isolate-write", "YES would write the isolate"))
    if yes.get("free_real") or (facts.get("knobs", 0) != 0 and yes.get("requires_knobs")):
        fired.append(("R-knobs", "YES introduces a free real parameter"))
    if yes.get("burned") or any(b in str(claim.get("text", "")) and yes.get("assert_burned") for b in BURNED):
        fired.append(("R-burn-list", "YES is a burned weld"))
    if yes.get("weld_class_to_lock"):
        fired.append(("R-weld", "YES welds CLASS onto LOCK"))
    if yes.get("stick_left_in"):
        fired.append(("R-stick-left-in", "YES leaves observational stick in as dynamics"))
    if yes.get("map_called_lock"):
        fired.append(("R-map-called-lock", "YES labels a map/class as LOCK/FORCED/DERIVED"))
    if yes.get("unique_color_derived") or yes.get("picks_SU3c") or yes.get("n_gen_as_colors") or yes.get("c2_as_color"):
        fired.append(("R-color-lock", "YES picks unique SU(3)_c / three colors / C2 as color"))
    if yes.get("lambda_is_R_meters") or yes.get("stick_as_R"):
        fired.append(("R-scale", "YES treats Weyl λ or stick as R in meters"))
    if yes.get("sigma_is_gmunu") or yes.get("sigma_is_A") or yes.get("phi_is_gmunu"):
        fired.append(("R-metric-swap", "YES identifies σ* or φ(θ,ψ) with g_μν"))
    if yes.get("rewrite_numeric"):
        fired.append(("R-rewrite-numeric", "YES would rewrite a locked numeric"))
    if yes.get("t_wall_as_tension"):
        fired.append(("R-scale", "YES uses T_wall as brane tension / Israel jump"))
    if yes.get("geff_as_GN"):
        fired.append(("R-modulus-called-lock", "YES uses 8πG_eff as G_N in an ODE"))
    ext_names = set(claim.get("external_names") or [])
    claim_isolate = bool(claim.get("claim_as_isolate_atom"))
    if yes.get("new_real") or yes.get("integration_C"):
        if claim_isolate or not ext_names:
            fired.append(("R-knobs", "YES introduces L, bulk Λ, RS k, or integration constant C as isolate"))

    menu = facts.get("modulus_menu") or []
    by_name = {row["name"]: row for row in menu if isinstance(row, dict) and "name" in row}
    used = claim.get("uses_modulus")
    if used:
        row = by_name.get(used)
        allowed = {r["name"] for r in menu if r.get("type") in ALLOWED_MODULUS_TYPES}
        if used not in allowed:
            if used in ext_names and not claim_isolate:
                pass
            else:
                fired.append(("R-unlisted-modulus", f"modulus {used!r} is not a named allowed menu row"))
        label = claim.get("labels_modulus_as") or yes.get("labels_modulus_as")
        if row and row.get("type") in {"GAUGE", "CLASS", "OPEN-FIELD", "FORBIDDEN"}:
            if label in {"FORCED", "derived", "locked", "G_N", "unique color", "the 4-fold"}:
                fired.append(
                    (
                        "R-modulus-called-lock",
                        f"labels {used!r} type {row.get('type')} as {label}",
                    )
                )
        if yes.get("modulus_called_lock"):
            if row and row.get("type") != "FORCED":
                fired.append(
                    (
                        "R-modulus-called-lock",
                        f"YES treats non-FORCED modulus {used!r} as lock",
                    )
                )
    return fired


def runCheck(claim: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
    fired = _fire(claim, facts)
    gates = [g for g, _ in fired]
    reasons = [r for _, r in fired]

    kind = claim.get("kind", "")

    if fired:
        bin_ = "REFUSED"
        return {"bin": bin_, "gates": gates, "reasons": reasons, "color_lock": False}

    # No refuse-gate. Assign from facts + question kind. One legal bin.
    if kind == "write_closed":
        ok = facts["knobs"] == 0 and facts["N_gen"] == 3 and not facts.get("isolate_written")
        return {
            "bin": "FORCED" if ok else "REFUSED",
            "gates": [],
            "reasons": ["isolate knobs=0 and N_gen=3 recorded; write-set closed"] if ok else ["write-closed failed"],
        }

    if kind == "five_metric":
        if facts.get("sigma_star_locked"):
            return {
                "bin": "FORCED",
                "gates": [],
                "reasons": ["σ* locked as T^{1,1} shape (5-metric), not g_μν"],
            }
        return {"bin": "UNKNOWN", "gates": [], "reasons": ["σ* not found"]}

    if kind == "unique_4fold":
        if facts.get("unique_4fold"):
            return {"bin": "FORCED", "gates": [], "reasons": ["unique 4-fold in facts"]}
        return {
            "bin": "REFUSED",
            "gates": [],
            "reasons": ["unique 4-fold pick failed; leftover X^4 is CLASS not a pick"],
            "leftover_class": True,
        }

    if kind == "warp":
        if facts.get("warp_forced"):
            return {"bin": "FORCED", "gates": [], "reasons": ["warp A fixed"]}
        return {
            "bin": "REFUSED",
            "gates": [],
            "reasons": ["warp A not in locked atoms; failed uniqueness = NO"],
        }

    if kind == "gmunu_is_sigma":
        # YES would have fired R-metric-swap. Asking the identity: facts say no.
        return {
            "bin": "REFUSED",
            "gates": ["R-metric-swap"],
            "reasons": ["σ* is 5-shape, not g_μν; identity refused"],
        }

    if kind == "iso_and_color":
        iso = facts.get("iso_group")
        return {
            "bin": "FORCED",
            "gates": [],
            "reasons": [f"Iso of locked 5-fold recorded as {iso}; not a color lock"],
            "color_lock": False,
            "iso_group": iso,
        }

    if kind == "unique_color":
        return {
            "bin": "REFUSED",
            "gates": ["R-color-lock"],
            "reasons": ["unique SU(3)_c not derived from isolate"],
            "color_lock": False,
        }

    if kind == "G_SM":
        return {
            "bin": "REFUSED",
            "gates": ["R-weld"],
            "reasons": ["G_SM not forced from isolate"],
        }

    if kind == "picked_4fold":
        return {
            "bin": "REFUSED",
            "gates": ["R-weld"],
            "reasons": ["ℂℙ² and K3 are CLASS options, not a unique pick"],
        }

    if kind == "port_identities":
        agree = facts.get("t_wall_n") == facts.get("t_wall_lam")
        return {
            "bin": "FORCED" if agree else "UNKNOWN",
            "gates": [],
            "reasons": [
                "P3/P4 are Fraction identities of locked ports"
                if agree
                else "T_wall sums disagree (live finding)"
            ],
            "spacetime_reading_forced": False,
            "is_G_N": False,
            "proves_SU3c": False,
        }

    if kind == "port_topology":
        return {
            "bin": "FORCED",
            "gates": [],
            "reasons": ["b2=b3=1 from T^{1,1}≃S²×S³ topology, not a flux pick"],
            "not_implied": ["flux"],
        }

    if kind == "port_iso":
        return {
            "bin": "FORCED",
            "gates": [],
            "reasons": ["Iso group of locked 5-fold"],
            "color_lock": False,
            "not_implied": ["SU(3)_c", "color"],
        }

    if kind == "port_twall":
        agree = facts.get("t_wall_n") == facts.get("t_wall_lam")
        return {
            "bin": "FORCED" if agree else "UNKNOWN",
            "gates": [],
            "reasons": ["T_wall = Σ n_η/4 = Σ λ̃/6" if agree else "T_wall sums disagree"],
            "not_implied": ["Chern index", "GeV^3 tension"],
        }

    if kind == "port_sigma_Geff":
        return {
            "bin": "FORCED",
            "gates": [],
            "reasons": ["σ*² and σ*²/C₂(3) as locked-port numbers"],
            "not_implied": ["G_N", "SU(3)_c"],
            "is_G_N": False,
            "proves_SU3c": False,
        }

    if kind == "class_pipes":
        return {
            "bin": "CLASS",
            "gates": [],
            "reasons": ["CLASS color pipes remain a family; no unique member forced"],
        }

    if kind == "iso_contains_su3":
        dim_iso = facts.get("dim_iso")
        dim_su3 = facts.get("dim_su3")
        if dim_iso is not None and dim_su3 is not None and dim_iso < dim_su3:
            return {
                "bin": "REFUSED",
                "gates": [],
                "reasons": [
                    f"dim(Iso)={dim_iso} < dim(SU(3))={dim_su3}; Iso cannot contain SU(3) as a Lie subgroup"
                ],
                "color_lock": False,
            }
        if facts.get("iso_contains_su3"):
            return {"bin": "FORCED", "gates": [], "reasons": ["Iso contains SU(3)"]}
        return {
            "bin": "REFUSED",
            "gates": [],
            "reasons": ["Iso does not force SU(3)_c"],
            "color_lock": False,
        }

    return {"bin": "UNKNOWN", "gates": [], "reasons": ["kind not decided by facts"]}
