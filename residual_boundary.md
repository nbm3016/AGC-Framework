# Residual / regularity series — permanent boundary record

**Documentation only.** This file does not change any locked numeric. It does not promote any diagnostic residual or any new \(\sigma\) as the official lock.

| Item | Value |
|------|--------|
| Official \(\beta\) residual lock | **0.095716** (never replaced) |
| Official \(\sigma^*\) | \(\sqrt{3}/2\) (never replaced) |
| `continuous_knobs` | **0** |
| Continuum \(r\to 0\) | **Open** |
| Absolute scale | Observational conversion only |
| Numerical source of truth | [`complete_baseline.json`](complete_baseline.json) |
| Classification document | [`STATUS.md`](STATUS.md) |

**RESIDUAL SERIES BOUNDARY DOCUMENTED – OFFICIAL LOCK UNTOUCHED – CONTINUUM LIMIT STILL OPEN**

---

## Purpose of the series

The residual-stability and geometric-regularity series asked one structural question, under hard topological gates and `continuous_knobs = 0`:

Does the locked \(\Sigma^5\times T^{1,1}\) skeleton protect a positive Einstein–YM residual floor, or a positive lower bound \(\sigma\ge\sigma_{\min}>0\), once Stages 1–3 geometry is held fixed as the reference?

The gates applied after every candidate were:

- Native APS index \(\to N_{\mathrm{gen}}=3\)
- Self-duality \(\star\Psi=\Psi\)
- \(\eta\)-lattice / monodromy consistency

Diagnostic deformations were allowed. Official \(r=0.095716\), \(\sigma^*=\sqrt{3}/2\), \(\tilde\lambda\), \(N_{\mathrm{gen}}\), flavor angles, and Stage-4 phenomenology were never rewritten.

---

## Chronological summary

### 1. Residual-stability map (grid=24, \(N_h=24\))

Probe: [`stage_residual_stability_map.py`](stage_residual_stability_map.py)  
Record: [`residual_stability_map.json`](residual_stability_map.json)

Started from the official 24/24 slice (\(r=0.0957162820145647\), matches the lock to 6 dp). Controlled harmonic perturbations of \(\beta_{ij}\), limited \(\sigma\) excursions, and residual-direction steps were accepted whenever the three gates passed. Discrete-adjacent stresses (\(j_2\neq 0\), APS fiber \(r_{\mathrm{APS}}\neq 0\), \(n_\eta\) neighbors) were rejected.

| Finding | Value |
|---------|--------|
| Candidates / accepted / rejected | 96 / 83 / 13 |
| Min residual still inside the sector | 0.089856 (not promoted) |
| Gate fire counts (rejected stresses) | \(\eta\)-lattice 7, APS 3, self-duality 3 |
| Closest gate on accepted slice | native APS index (spectral-flow wall at \(j_1=3/2\)) |
| Continuous \(\beta/\sigma\) steps | all accepted |

### 2. Gated residual minimization, 24-mode slice

Probe: [`stage_residual_minimization_gated.py`](stage_residual_minimization_gated.py)  
Record: [`residual_minimization_gated.json`](residual_minimization_gated.json)

Unregularized L-BFGS-B plus Armijo descent on harmonic coefficients, then limited \(\sigma\) steps inside a \(\pm 5\%\) box. Gates checked every candidate.

| Finding | Value |
|---------|--------|
| Start residual | 0.0957162820145647 |
| Harmonic-only min (\(\sigma\) frozen) | 0.036616 |
| Lowest accepted residual | 0.034360 (not promoted) |
| \(\sigma\) at best | \(\sigma^*\) lower box wall (\(-5\%\)) |
| Gate rejections | **0** |
| What stopped further progress | numerical convergence; \(\sigma\) box active |
| Topological floor | not observed |

### 3. Higher-resolution gated minimization (grid=48, \(N_h=48\))

Probe: [`stage_residual_minimization_gated_hires.py`](stage_residual_minimization_gated_hires.py)  
Record: [`residual_minimization_gated_hires.json`](residual_minimization_gated_hires.json)

Same gates, elevated resolution. Start residual at 48/48 is a regularized analog of the official solver, **not** a new lock.

| Finding | Value |
|---------|--------|
| Start residual at 48/48 | 0.089715 |
| Harmonic-only min (\(\sigma\) frozen) | 0.035772 |
| Lowest accepted residual | 0.033532 (not promoted) |
| vs 24-mode floor 0.034360 | slightly lower (\(-0.000828\)) |
| Gate rejections | **0** |
| \(\sigma\) box | still \(\pm 5\%\); hit the \(-5\%\) wall |
| Topological floor | not observed |

Raising resolution did not produce a topological residual floor.

### 4. Gated minimization with the \(\sigma\) box removed

Probe: [`stage_residual_minimization_no_sigma_box.py`](stage_residual_minimization_no_sigma_box.py)  
Record: [`residual_minimization_no_sigma_box.json`](residual_minimization_no_sigma_box.json)

The artificial \(\pm 5\%\) box was lifted. \(\sigma\) was free except for a numerical positivity domain \(\sigma\in[10^{-4},20]\) (overflow / division-by-zero only). Free \(\sigma\) here is a probe of the Einstein–YM residual functional, **not** a continuous knob of the theory.

| Finding | Value |
|---------|--------|
| Start residual at 48/48 | 0.089715 |
| Lowest accepted residual | 0.011021 (not promoted) |
| Final \(\sigma\) | \(10^{-4}\) (numerical positivity bound) |
| Final \(\Delta\sigma/\sigma^*\) | \(-0.99988\) |
| Gate rejections | **0** |
| What stopped further progress | \(\sigma\to 0^+\); positivity bound, **not** a gate |
| Official \(\sigma^*\) | still \(\sqrt{3}/2\) (not replaced) |

### 5. Geometric regularity / non-degeneracy probe for \(\sigma\)

Probe: [`stage_geometric_regularity_sigma.py`](stage_geometric_regularity_sigma.py)  
Record: [`geometric_regularity_sigma.json`](geometric_regularity_sigma.json)

Structural test: do locked structures force \(\sigma\ge\sigma_{\min}>0\)?

| Mechanism | Forced? | \(\sigma_{\min}\) | Type |
|-----------|---------|-------------------|------|
| APS / spectral-flow | NO | none | topological (independent of \(\sigma\)) |
| Self-duality \(\star\Psi=\Psi\) | NO | none | topological |
| Positive \(\Sigma^5\) / mode volume | NO | none | topological |
| Metric non-degeneracy \(\bar g=\mathrm{diag}(\sigma^2,\sigma^2,1,1,1)\) | NO | none (only \(\sigma>0\); inf = 0) | open cone, not a floor |
| Domain-wall tension \(T_{\mathrm{wall}}=13/2\) | NO | none | spectral |
| Einstein–YM positivity / curvature | NO | none | residual prefers smaller \(\sigma\) |
| Monodromy / \(\eta\)-lattice | NO | none | topological |
| Geometric \(V(\sigma)\) flux wall | NO | not a regularity floor; \(V\)-minimizer is already locked \(\sigma^*\) | variational, different functional |

**Binary answer: NO.** Locked geometry does not force \(\sigma\ge\sigma_{\min}>0\).

\(V(\sigma)\to\infty\) as \(\sigma\to 0^+\) is how \(\sigma^*=\sqrt{3}/2\) is already frozen as the Stage-1B minimizer. It does not police the Einstein–YM residual, which continues to fall as \(\sigma\to 0^+\).

---

## Key numerical findings (diagnostic only)

| Quantity | Official lock | Diagnostic (not promoted) |
|----------|---------------|---------------------------|
| \(\beta\) residual | **0.095716** | 24-mode min 0.034360; 48-mode boxed min 0.033532; free-\(\sigma\) min 0.011021 |
| \(\sigma^*\) | \(\sqrt{3}/2\) | free-\(\sigma\) search reached \(10^{-4}\) |
| \(N_{\mathrm{gen}}\) | 3 | held on every accepted step |
| Gate rejections on continuous \(\beta/\sigma\) paths | — | **0** |
| Gate rejections on discrete-adjacent stresses | — | 13 (stability map only) |

No diagnostic value in the right-hand column is the official lock.

---

## Boundary conclusions (permanent)

1. **No topological residual floor was observed.** APS, self-duality, and the \(\eta\)-lattice did not stop residual reduction along continuous harmonic or \(\sigma\) steps.
2. **Locked geometry does not force \(\sigma\ge\sigma_{\min}>0\).** Metric non-degeneracy requires only \(\sigma>0\) (infimum 0). The topological sector remains open down to \(\sigma\to 0^+\).
3. **The official lock remains the reference and was never replaced:** \(r=0.095716\), \(\sigma^*=\sqrt{3}/2\), native \(N_{\mathrm{gen}}=3\), \(\tilde\lambda=\{4.5,12,22.5\}\), residual-NLO A4 high-scale angles, Stage-4 phenomenology.
4. **Continuum \(r\to 0\) is still Open.** This series does not close that gap. It records that the locked gates do not protect a positive floor on the 24-mode or 48-mode slices.
5. **`continuous_knobs = 0`.** No external scale, flux, or free coefficient was introduced. Absolute scale remains observational conversion only.

The Open list in [`STATUS.md`](STATUS.md) is unchanged. Future parameter-free geometric structures may reduce it; until then, continuum \(r\to 0\) stays Open.

---

## Source files

| Role | File |
|------|------|
| This boundary record | `residual_boundary.md` |
| Stability map | `residual_stability_map.json` |
| 24-mode gated min | `residual_minimization_gated.json` |
| 48-mode gated min | `residual_minimization_gated_hires.json` |
| \(\sigma\) box removed | `residual_minimization_no_sigma_box.json` |
| Regularity probe | `geometric_regularity_sigma.json` |
| Numerical source of truth | `complete_baseline.json` (`residual_boundary` block) |
| Verification log | `verification_log.txt` |

Reproduce the locked core with `python AGC_Computational_Framework.py --full` (8/8 PASS). That command does not promote diagnostic residuals.
