#!/usr/bin/env python3
"""
Residual-β mass-gap / obstruction probe — locked quantities only.

Does not re-optimize Stages 1–3. Does not change r. continuous_knobs = 0.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "residual_massgap_probe.json")

C2 = 4.0 / 3.0
SIGMA = math.sqrt(3.0) / 2.0
LOCKED_R = 0.095716
LOCKED_R_FULL = 0.0957162820145647
LAMBDA0 = 4.5
T_WALL = 6.5
MONO = 24
N_GEN = 3


def load_locked() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def probe() -> Dict[str, Any]:
    b = load_locked()
    lr = b.get("locked_results") or {}
    r = float(lr.get("beta_residual_new") or LOCKED_R_FULL)
    sigma = float(lr.get("sigma_star") or SIGMA)
    tau = r * (sigma ** 2)
    # V(σ)=(3/2)σ²+(3/2)(λ̃₀/6)²/σ² ; m²_σ = 3 + 9 (λ̃₀/6)² / σ⁴
    flux = 1.5 * (LAMBDA0 / 6.0) ** 2
    m2_sigma = 3.0 + 6.0 * flux / (sigma ** 4)
    m2_phi = 2.0 * (1.0 + r) * (sigma ** 2) / C2
    # Linear tension as a would-be potential for r: V=τ_res=r σ*²
    dVdr_linear = sigma ** 2
    d2Vdr2_linear = 0.0
    rows: List[Dict[str, Any]] = [
        {
            "mechanism": "APS boundary (fiber r_APS=0)",
            "generates_protection": False,
            "form": "APS kernel / index flow forbids fiber r_APS≠0",
            "mass_squared_or_obstruction": "topological for APS r, not for EY residual r",
            "strictly_positive_or_forced": False,
            "result": "NO — different r; does not force Frobenius residual → 0",
        },
        {
            "mechanism": "self-dual 7-form ⋆Ψ=Ψ",
            "generates_protection": False,
            "form": "‖⋆Ψ−Ψ‖²=0 on j₂=0",
            "mass_squared_or_obstruction": 0.0,
            "strictly_positive_or_forced": False,
            "result": "NO — condensate already vanishes; no remaining source for r→0",
        },
        {
            "mechanism": "Σ⁵ domain wall T_wall",
            "generates_protection": False,
            "form": "T_wall=Σ j(j+1)=13/2 (independent of r)",
            "mass_squared_or_obstruction": 0.0,
            "strictly_positive_or_forced": False,
            "result": "NO — discrete Casimir; d²T_wall/dr²=0 (flat in r)",
        },
        {
            "mechanism": "monodromy order 24",
            "generates_protection": False,
            "form": "lcm(8,3,8)=24 cyclotomic integer",
            "mass_squared_or_obstruction": None,
            "strictly_positive_or_forced": False,
            "result": "NO — group integer; does not quantize or mass the EY residual",
        },
        {
            "mechanism": "residual tension τ_res=r σ*²",
            "generates_protection": False,
            "form": f"V(r)≟τ_res=r σ*²; dV/dr=σ*²={dVdr_linear:.6f}; d²V/dr²=0",
            "mass_squared_or_obstruction": d2Vdr2_linear,
            "strictly_positive_or_forced": False,
            "result": (
                "NO — linear in r: slope prefers smaller r but second variation "
                "is flat (not a mass gap). Quadratic V=τ_res² is not forced"
            ),
            "tau_res": tau,
        },
        {
            "mechanism": "native APS index N_gen=3",
            "generates_protection": False,
            "form": "dim ker D_APS = 3",
            "mass_squared_or_obstruction": None,
            "strictly_positive_or_forced": False,
            "result": "NO — integer cohomology; independent of EY residual r",
        },
        {
            "mechanism": "geometric V(σ)",
            "generates_protection": False,
            "form": f"m²_σ=d²V/dσ²|_*={m2_sigma:.6f}>0",
            "mass_squared_or_obstruction": m2_sigma,
            "strictly_positive_or_forced": True,
            "result": "NO for r — mass gap protects σ*, not the EY residual",
        },
        {
            "mechanism": "φ mass-gap proxy",
            "generates_protection": False,
            "form": f"m²_φ∼2(1+r)σ*²/C₂={m2_phi:.6f}>0",
            "mass_squared_or_obstruction": m2_phi,
            "strictly_positive_or_forced": True,
            "result": "NO for r — stabilizes the field φ, not the mismatch value r[φ]",
        },
    ]
    any_yes = any(x["generates_protection"] for x in rows)
    return {
        "banner": "RESIDUAL β PROTECTION PROBE COMPLETE – ZERO KNOBS PRESERVED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "locked_r_unchanged": True,
        "locked_r": LOCKED_R,
        "residual_protected": False,
        "decision": "NO",
        "reason": (
            "No locked structure supplies a strictly positive mass² for the "
            "Einstein–YM residual r, nor a topological obstruction that forces "
            "r→0. APS/self-duality/index/monodromy/T_wall act on other discrete "
            "data. V(σ) and m²_φ protect σ and φ. τ_res is linear in r "
            "(flat second variation). Continuum r→0 remains open."
        ),
        "mechanisms": rows,
        "locked_snapshot": {
            "n_gen": N_GEN,
            "sigma_star": sigma,
            "beta_residual_new": r,
            "tau_res": tau,
            "T_wall": T_WALL,
            "monodromy_order": MONO,
            "m2_sigma": m2_sigma,
            "m2_phi": m2_phi,
            "continuous_knobs": 0,
        },
    }


def main() -> None:
    print("AGC residual-β mass-gap / obstruction probe (zero knobs)\n")
    res = probe()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")
    print(f"{'Mechanism':<42} {'Protects r?':<12} Result")
    print("-" * 100)
    for row in res["mechanisms"]:
        yn = "YES" if row["generates_protection"] else "NO"
        print(f"{row['mechanism']:<42} {yn:<12} {row['result']}")
    print()
    print(f"Final status: residual protected? {res['decision']}")
    print(f"continuous_knobs: {res['continuous_knobs']}")
    print(f"locked r unchanged: {res['locked_r']}")
    print(res["banner"])
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
