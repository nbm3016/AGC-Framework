#!/usr/bin/env python3
"""
AGC Stage 1 — integrated verification, consolidation, and baseline export.

Runs all Stage 1A/1B/1C solvers, verifies artifacts, exports consolidated
tables/proofs/LaTeX appendix, and writes agc_core_baseline.json.
"""

from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "agc_core_baseline.json")
LATEX_PATH = os.path.join(ARTIFACT_DIR, "stage1_appendix.tex")
SUMMARY_PATH = os.path.join(ARTIFACT_DIR, "summary.md")

REQUIRED_ARTIFACTS = [
    "validated_modes.json",
    "r0_modes.json",
    "sigma_fixed.json",
    "delta_eta_predicted.json",
]


def _import_stage_modules():
    from neutrality_proof import assert_aps_neutrality, build_r0_modes, neutrality_proof_text
    from stage1a_validator import (
        LAMBDA_TARGETS,
        SURVIVOR_MODES,
        assert_unique_three_modes,
        enumerate_lattice,
        minima_table,
        uniqueness_proof,
    )
    from stage1b_sigma_solver import (
        SIGMA_SUSY_EXACT,
        assert_stable_supersymmetric_minimum,
        equilibrium_table as sigma_table,
        load_locked_stage1a,
        proof_snippet as sigma_proof,
        solve_equilibrium,
    )
    from stage1c_predictive import (
        assert_predictive_delta_eta,
        build_predictive_set,
        discrete_search,
        equilibrium_table as delta_table,
        load_locked_inputs,
        proof_snippet as delta_proof,
    )

    return {
        "assert_aps_neutrality": assert_aps_neutrality,
        "build_r0_modes": build_r0_modes,
        "neutrality_proof": neutrality_proof_text,
        "assert_unique_three_modes": assert_unique_three_modes,
        "enumerate_lattice": enumerate_lattice,
        "minima_table": minima_table,
        "uniqueness_proof": uniqueness_proof,
        "LAMBDA_TARGETS": LAMBDA_TARGETS,
        "SURVIVOR_MODES": SURVIVOR_MODES,
        "assert_stable_supersymmetric_minimum": assert_stable_supersymmetric_minimum,
        "sigma_table": sigma_table,
        "load_locked_stage1a": load_locked_stage1a,
        "sigma_proof": sigma_proof,
        "solve_equilibrium": solve_equilibrium,
        "SIGMA_SUSY_EXACT": SIGMA_SUSY_EXACT,
        "assert_predictive_delta_eta": assert_predictive_delta_eta,
        "build_predictive_set": build_predictive_set,
        "discrete_search": discrete_search,
        "delta_table": delta_table,
        "load_locked_inputs": load_locked_inputs,
        "delta_proof": delta_proof,
    }


def verify_artifacts_exist() -> List[str]:
    missing = [f for f in REQUIRED_ARTIFACTS if not os.path.isfile(os.path.join(ARTIFACT_DIR, f))]
    if missing:
        raise FileNotFoundError(f"Missing artifacts: {missing}")
    return REQUIRED_ARTIFACTS


def load_json(name: str) -> Dict[str, Any]:
    with open(os.path.join(ARTIFACT_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def run_full_verification(mods: Dict) -> Dict[str, Any]:
    """Execute all Stage 1 assertion chains."""
    records = mods["enumerate_lattice"]()
    mods["assert_unique_three_modes"](records)
    mods["assert_aps_neutrality"]()

    locked_1a = mods["load_locked_stage1a"]()
    eq = mods["solve_equilibrium"](locked_1a)
    mods["assert_stable_supersymmetric_minimum"](eq)

    locked_1c = mods["load_locked_inputs"]()
    modes = mods["build_predictive_set"](locked_1c)
    passing, winner = mods["discrete_search"](locked_1c)
    mods["assert_predictive_delta_eta"](modes, locked_1c, winner)

    return {
        "records": records,
        "locked_1a": locked_1a,
        "equilibrium": eq,
        "locked_1c": locked_1c,
        "delta_modes": modes,
        "delta_winner": winner,
        "delta_passing_count": len(passing),
    }


def build_latex_appendix(mods: Dict, ctx: Dict) -> str:
    validated = load_json("validated_modes.json")
    sigma = load_json("sigma_fixed.json")
    delta = load_json("delta_eta_predicted.json")

    return r"""\section{AGC Stage 1 Appendix}
\subsection{Stage 1A --- $\Sigma^5$ spectral survivors}
""" + validated.get("latex_snippet", "") + r"""

\subsection{Stage 1B --- $T^{1,1}$ $\sigma$-equilibrium}
\begin{align}
V(\sigma) &= \tfrac{3}{2}\sigma^2 + \tfrac{3}{2}\!\left(\frac{\tilde\lambda_0}{6}\right)^{\!2}\!\frac{1}{\sigma^2}
  - \tfrac{5}{3}r_0^2, \\
\sigma_* &= \sqrt{\tilde\lambda_0/6} = \sqrt{3}/2 = """ + f"{sigma['sigma_star']:.12f}" + r""".
\end{align}

\subsection{Stage 1C --- predictive $\Delta\eta$}
\begin{align}
\Delta\eta_k &= \frac{n_k\pi}{12}, \quad n_k = 4\,j_1(j_1+1), \\
(n_1,n_2,n_3) &= (3,8,15), \quad
\frac{n_2}{n_1}=\frac{8}{3},\;
\frac{n_3}{n_1}=5,\;
\frac{n_3}{n_2}=\frac{15}{8}.
\end{align}

\subsection{Consolidated survivor table}
\begin{center}
\begin{tabular}{cccccc}
\hline
$j_1$ & $j_2$ & $r$ & $\tilde\lambda$ & $\sigma_*$ & $\Delta\eta/\pi$ \\
\hline
0.5 & 0 & 0 & 4.5  & """ + f"{sigma['sigma_star']:.6f}" + r""" & 1/4 \\
1.0 & 0 & 0 & 12.0 & """ + f"{sigma['sigma_star']:.6f}" + r""" & 2/3 \\
1.5 & 0 & 0 & 22.5 & """ + f"{sigma['sigma_star']:.6f}" + r""" & 5/4 \\
\hline
\end{tabular}
\end{center}
"""


def build_consolidated_tables(mods: Dict, ctx: Dict) -> str:
    parts = [
        mods["minima_table"](ctx["records"]),
        "",
        mods["sigma_table"](ctx["locked_1a"], ctx["equilibrium"]),
        "",
        mods["delta_table"](ctx["delta_modes"]),
    ]
    return "\n".join(parts)


def build_consolidated_proofs(mods: Dict, ctx: Dict) -> str:
    parts = [
        mods["neutrality_proof"](),
        "",
        mods["uniqueness_proof"](ctx["records"]),
        "",
        mods["sigma_proof"](ctx["locked_1a"], ctx["equilibrium"]),
        "",
        mods["delta_proof"](
            ctx["locked_1c"],
            ctx["delta_modes"],
            [ctx["delta_winner"]],
            ctx["delta_winner"],
        ),
    ]
    return "\n\n".join(parts)


def export_baseline(mods: Dict, ctx: Dict, tables: str, proofs: str, latex: str) -> Dict:
    validated = load_json("validated_modes.json")
    sigma = load_json("sigma_fixed.json")
    delta = load_json("delta_eta_predicted.json")
    r0 = load_json("r0_modes.json")

    baseline = {
        "version": "stage1-complete",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "lambda_targets": list(mods["LAMBDA_TARGETS"]),
        "survivor_modes": list(mods["SURVIVOR_MODES"]),
        "sigma_star": sigma["sigma_star"],
        "sigma_susy_exact": mods["SIGMA_SUSY_EXACT"],
        "n_eta_triple": delta["n_triple"],
        "delta_eta_over_pi": delta["delta_eta_over_pi"],
        "artifacts": {name: os.path.join(ARTIFACT_DIR, name) for name in REQUIRED_ARTIFACTS},
        "stage1a": {
            "survivors": validated["survivors"],
            "r0_modes": r0["modes"],
        },
        "stage1b": {
            "sigma_star": sigma["sigma_star"],
            "v_sigma_star": sigma["v_sigma_star"],
            "stable": sigma["stable"],
        },
        "stage1c": {
            "modes": delta["modes"],
            "discrete_candidates_count": delta["discrete_candidates_count"],
        },
        "verification": {
            "unique_three_modes": True,
            "aps_neutral": True,
            "sigma_sqrt3_over_2": True,
            "delta_eta_unique_triple": True,
        },
        "consolidated_tables": tables,
        "consolidated_proofs": proofs,
        "latex_appendix": latex,
    }
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
    return baseline


def write_summary_md(baseline: Dict) -> None:
    content = f"""# AGC Stage 1 — Complete Summary

**Status:** PASS  
**Generated:** {baseline['timestamp_utc']}

## Results

| Stage | Key result | Value |
|-------|-----------|-------|
| 1A | Survivor modes | (½,0,0), (1,0,0), (3/2,0,0) |
| 1A | λ̃ spectrum | {{4.5, 12.0, 22.5}} |
| 1B | σ* equilibrium | √3/2 ≈ {baseline['sigma_star']:.12f} |
| 1C | Δη/π triple | {{1/4, 2/3, 5/4}} |
| 1C | η-lattice n | (3, 8, 15) |

## Verification chain

- `assert_unique_three_modes()` — exactly 3 APS-neutral survivors
- `assert_aps_neutrality()` — r=0 kernel, index=0, ⋆Ψ=Ψ
- `assert_stable_supersymmetric_minimum()` — σ* = √3/2, d²V > 0
- `assert_predictive_delta_eta()` — unique discrete (3,8,15) triple

## Artifacts

- `agc_core_baseline.json` — consolidated locked baseline
- `stage1_appendix.tex` — LaTeX appendix
- `validated_modes.json`, `r0_modes.json`, `sigma_fixed.json`, `delta_eta_predicted.json`

## Stage 2 entry point

Stage 1 baseline locks N_gen = 3 survivor count for anomaly inflow descent (Stage 2A).
"""
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    print("AGC Stage 1 complete integration — starting\n")
    mods = _import_stage_modules()

    artifacts = verify_artifacts_exist()
    print(f"Artifacts present: {artifacts}")

    ctx = run_full_verification(mods)
    print("All Stage 1 assertions passed.\n")

    tables = build_consolidated_tables(mods, ctx)
    proofs = build_consolidated_proofs(mods, ctx)
    latex = build_latex_appendix(mods, ctx)

    with open(LATEX_PATH, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Saved {LATEX_PATH}")

    baseline = export_baseline(mods, ctx, tables, proofs, latex)
    print(f"Saved {BASELINE_PATH}")

    write_summary_md(baseline)
    print(f"Saved {SUMMARY_PATH}")

    print("\n" + "=" * 72)
    print("CONSOLIDATED TABLES")
    print("=" * 72)
    print(tables)
    print("\nStage 1 integration complete — baseline locked for Stage 2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())