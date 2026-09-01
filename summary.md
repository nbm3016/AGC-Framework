# AGC Stage 1 — Complete Summary

**Status:** PASS  
**Generated:** 2026-07-07T02:57:38.371401+00:00

## Results

| Stage | Key result | Value |
|-------|-----------|-------|
| 1A | Survivor modes | (½,0,0), (1,0,0), (3/2,0,0) |
| 1A | λ̃ spectrum | {4.5, 12.0, 22.5} |
| 1B | σ* equilibrium | √3/2 ≈ 0.866025403784 |
| 1C | Δη/π triple | {1/4, 2/3, 5/4} |
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
