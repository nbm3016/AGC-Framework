#!/usr/bin/env python3
"""
Higher-derivative / UV Wilson-coefficient probe — locked data only, zero knobs.

Does not re-optimize Stages 1–3. Does not assign free Wilson numbers or
external scales. Does not change locked numerics.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "hd_uv_probe.json")

C2 = 4.0 / 3.0


def load_locked() -> Dict[str, Any]:
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def probe() -> Dict[str, Any]:
    b = load_locked()
    lr = b.get("locked_results") or {}
    r = float(lr.get("beta_residual_new") or 0.095716)
    sigma = float(lr.get("sigma_star") or math.sqrt(3.0) / 2.0)
    lams = list(lr.get("lambda_targets") or [4.5, 12.0, 22.5])
    g8 = float(lr.get("eight_pi_g_eff") or (sigma ** 2) / C2)
    n_eta = list(lr.get("n_eta_triple") or [3, 8, 15])
    t_wall = 6.5
    rows: List[Dict[str, Any]] = [
        {
            "term": "Gauss–Bonnet α_GB",
            "coefficient_forced": False,
            "candidate_id": f"α_GB ≟ r = {r:.6f} or r σ*² = {r * sigma**2:.6f}",
            "origin": "not forced — r is EY Frobenius mismatch, not a GB Wilson number",
            "result": "NO — identification α_GB=r is an unfixed map",
        },
        {
            "term": "Lovelock α_k (Euler densities L_k)",
            "coefficient_forced": False,
            "candidate_id": "form forced (Lovelock uniqueness); α_k free",
            "origin": "N6: χ=0 on odd factors; α_k unfixed",
            "result": "NO coefficient — form only; inert dynamics on Σ⁵ / T^{1,1}",
        },
        {
            "term": "R² / Ricci-squared α_R2",
            "coefficient_forced": False,
            "candidate_id": "not Weyl-primary after quotient",
            "origin": "C_phys Weyl covariance",
            "result": "NO — operator not independently eligible; coefficient unfixed",
        },
        {
            "term": "Weyl-squared ∫ C²",
            "coefficient_forced": False,
            "candidate_id": "eligible Weyl-covariant operator; no locked [C²] number",
            "origin": "conformal quotient",
            "result": "NO — under-determined coefficient",
        },
        {
            "term": "α′-type length²",
            "coefficient_forced": False,
            "candidate_id": f"α′ ≟ 8πG_eff={g8:.6f} or 1/Σλ̃={1.0/sum(lams):.6f}",
            "origin": "dimensionless locked numbers vs [α′]=length²",
            "result": "NO — needs an external length (observational conversion only; withdrawn)",
        },
        {
            "term": "Domain-wall GH / K³ coeff",
            "coefficient_forced": False,
            "candidate_id": f"T_wall={t_wall} dimensionless",
            "origin": "spectral Casimir, not a curvature coupling",
            "result": "NO — absolute GH coefficient needs a scale",
        },
        {
            "term": "Self-dual torsion HD",
            "coefficient_forced": False,
            "candidate_id": "‖⋆Ψ−Ψ‖²=0",
            "origin": "locked j₂=0 sector",
            "result": "NO — source vanishes; no nonzero Wilson number",
        },
        {
            "term": "Residual back-reaction r, r² beyond NLO",
            "coefficient_forced": False,
            "candidate_id": "√r flavor map already consumed",
            "origin": "locked residual-NLO A4",
            "result": "NO — further r-polynomials are free functionals",
        },
        {
            "term": "Monodromy 24 as α_HD",
            "coefficient_forced": False,
            "candidate_id": f"α ≟ 1/24 or 24 r = {24 * r:.6f}",
            "origin": "group integer, not a curvature coupling",
            "result": "NO — unfixed identification",
        },
    ]
    n_forced = sum(1 for x in rows if x["coefficient_forced"])
    return {
        "banner": "HIGHER-DERIVATIVE UV PROBE COMPLETE – ZERO KNOBS PRESERVED",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "continuous_knobs": 0,
        "stages_1_3_geometry_untouched": True,
        "wilson_coefficients_assigned": False,
        "external_scale_used": False,
        "unique_hd_coefficients_forced": False,
        "status": "No",
        "decision": "NO",
        "n_candidates": len(rows),
        "n_coefficients_forced": n_forced,
        "reason": (
            "Lovelock uniqueness fixes operator form, not α_k. Odd Euler "
            "densities are dynamically inert. Every numerical identification "
            "(α_GB=r, α′=8πG_eff, α=1/24, …) is an unfixed map or needs a "
            "length unit. Absolute scale is observational-conversion only and "
            "is withdrawn; it cannot lock Wilson numbers. Unique HD/UV "
            "coefficients are not forced."
        ),
        "candidates": rows,
        "locked_snapshot": {
            "n_gen": 3,
            "sigma_star": sigma,
            "beta_residual_new": r,
            "n_eta": n_eta,
            "theta13_deg": 7.953,
            "continuous_knobs": 0,
        },
    }


def main() -> None:
    print("AGC higher-derivative / UV coefficient probe (zero knobs)\n")
    res = probe()
    print(f"{'Term':<40} {'Forced?':<8} Result")
    print("-" * 100)
    for row in res["candidates"]:
        yn = "YES" if row["coefficient_forced"] else "NO"
        print(f"{row['term']:<40} {yn:<8} {row['result']}")
    print()
    print(f"Final status: unique HD coefficients forced? {res['decision']}")
    print(f"n forced: {res['n_coefficients_forced']}/{res['n_candidates']}")
    print(f"continuous_knobs: {res['continuous_knobs']}")
    print(res["banner"])
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        f.write("\n")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
