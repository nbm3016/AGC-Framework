# Dimensional scope of the β / T_wall solver

Audit from code and locked JSON only. No re-solve. Official lock untouched: \(r=0.095716\), \(\sigma^*=\sqrt{3}/2\), \(T_{\mathrm{wall}}=13/2\), `continuous_knobs=0`, 8/8 PASS.

## Verdict

Mixed: compact minimize + theoretical coupling to M^4 only through locked scalars.

The official β solve is an L-BFGS-B residual on a single conformal factor \(\varphi(\theta,\psi)\) on a 2D \(T^{1,1}\) torus grid. It is not a simultaneous 14D PDE. \(T_{\mathrm{wall}}=13/2\) is a discrete Casimir sum \(\sum j(j+1)\), not a live 14D wall energy.

## What the solver actually discretizes

Official path: `AGC_Theory._solve_beta_higher_res` in `AGC_Computational_Framework.py` (defaults `BETA_GRID_N=24`, `BETA_N_HARMONICS=24`). It imports `build_grid`, `beta_ij_tensor`, `ym_stress_tensor`, `einstein_ym_residual` from `stage2b_beta_variational.py`. Legacy 8/8 Stage 2B check uses `solve_variational(..., grid_n=12)` on the same 2D grid.

| quantity | coordinates / grid | dimension of the numerical problem |
|----------|--------------------|------------------------------------|
| \(\varphi\) field | \(\theta,\psi \in [0,2\pi)\) via `build_grid` | 2D array, shape `(grid_n, grid_n)` = 24×24 (official) or 12×12 (legacy 2B check) |
| harmonic basis | \(\sin(k\theta)\sin(k\psi)\), \(k=1\ldots 24\), plus Poisson warm-start | 25 scalar coefficients (1 Poisson amplitude + 24 Fourier modes) |
| \(\beta_{ij}\) tensor | reconstructed on the same \((\theta,\psi)\) cells; internal index \(i,j=0\ldots 4\) (`DIM=5`) | 24×24×5×5 array; only \((\theta,\psi)\) derivatives of \(\varphi\) are discrete |
| background metric \(\bar g_{ij}\) | `metric_bar(σ*) = diag(σ*², σ*², 1, 1, 1)` | 5×5 constant matrix; no extra grid |
| YM source \(F^2\) | locked \(n_\eta=(3,8,15)\), \(\Delta\eta\) on the same \((\theta,\psi)\) mesh | not an independent field; formula (2B.4) |
| Einstein–YM residual | `mean((β − 8πG_eff T^YM)²)` after subtracting the DC mode | 1 scalar objective |
| \(T_{\mathrm{wall}}\) | no grid | 3 Casimirs \(j\in\{1/2,1,3/2\}\); exact sum \(13/2\) |

```97:100:stage2b_beta_variational.py
def build_grid(n: int) -> Tuple[np.ndarray, np.ndarray, float]:
    theta = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    psi = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return theta, psi, theta[1] - theta[0]
```

```103:105:stage2b_beta_variational.py
def metric_bar(sigma_star: float) -> np.ndarray:
    s2 = sigma_star ** 2
    return np.diag([s2, s2, 1.0, 1.0, 1.0])
```

```756:786:AGC_Computational_Framework.py
        theta, psi, dtheta = build_grid(grid_n)
        ...
        for k in range(1, n_harmonics + 1):
            h = np.sin(k * th) * np.sin(k * ps)
        ...
        def objective(coeffs: Any) -> float:
            phi = assemble(coeffs)
            beta_full = beta_ij_tensor(locked, phi, dtheta)
            t_ym = ym_stress_tensor(locked, phi, theta, psi)
            mean_res, _ = einstein_ym_residual(beta_full, t_ym, g8)
```

`stage3_master_variational.py` writes the theoretical split \(S_{\mathrm{master}}=S_{\mathrm{APS}}|_{\Sigma^5}+\int_{T^{1,1}}d^5x\sqrt{g}[\ldots]\) and then reuses the same `build_grid(θ,ψ)` for \(\varphi\). APS on \(\Sigma^5\) is the locked Stage 1A survivor set, not a live 5D mesh.

## What is not discretized

- 4D metric \(g_{\mu\nu}\) on \(M^4\)
- 3-space coordinates \((x,y,z)\)
- time \(t\)
- a full \(Y^{14}\) mesh, or any 14-index residual array
- \(\Sigma^5\) as a live 5D grid (APS modes enter as locked \(j_1\) labels and volumes)
- the remaining three \(T^{1,1}\) angular directions as live coordinates (they appear only as constant \(\bar g_{aa}\) slots \(a=2,3,4\))
- a 14D energy density whose integral would define \(T_{\mathrm{wall}}\)

`eight_pi_g_eff` is \(\sigma^{*2}/C_2(3)\), a locked compact scalar, not a 4D Einstein tensor.

```39:44:stage2b_beta_variational.py
def eight_pi_g_eff(sigma_star: float) -> float:
    """
    Effective 8πG from locked Stage 1B modulus  [σ²/C₂(3) normalization].
    Replaces bare 8π to match compact T^{1,1} flux scale.
    """
    return sigma_star ** 2 / C2_SU3
```

## How T_wall = 13/2 is obtained

Function: `domain_wall_tension` in `stage_moduli_stabilization.py`, with volumes from Stage 1A Casimirs. Identity lemma: `vol` / `identity_lemma` in `stage_wall_tension_invariant.py`.

```339:342:stage_moduli_stabilization.py
    # Survivor volumes from Stage 1A geometric formula Vol = j1(j1+1)
    j1s = [0.5, 1.0, 1.5][:n_gen]
    vols = [j * (j + 1.0) for j in j1s]
    t_wall = domain_wall_tension(vols, n_gen)
```

```77:82:stage_moduli_stabilization.py
def domain_wall_tension(survivor_vols: List[float], n_gen: int) -> float:
    """
    Σ⁵ domain-wall tension proxy from locked survivor volumes.
    T_wall = Σ_k Vol_k  (dimensionless spectral volumes on j₂=0 line).
    """
    return float(sum(survivor_vols[:n_gen]))
```

```34:40:stage_wall_tension_invariant.py
def vol(j1: Fraction, j2: Fraction = Fraction(0)) -> Fraction:
    return j1 * (j1 + 1) + j2 * (j2 + 1)
...
    t_wall = sum(vols, Fraction(0))
```

Arithmetic: \(\frac12\cdot\frac32 + 1\cdot 2 + \frac32\cdot\frac52 = \frac34 + 2 + \frac{15}{4} = \frac{13}{2}\).

This does **not** depend on a 4D field, on \(\varphi(\theta,\psi)\), or on the β residual \(r\). Locked JSON (`complete_baseline.json` / `TIER1_Locked_Core_CLEAN/complete_baseline_locked.json`, `moduli_stabilization.json`) records `T_wall_exact = "13/2"`, `T_wall_float = 6.5`, `dimensionful_4d_tension = false`.

## How 14D enters

Theoretical ansatz / fibration split, not a live 14D residual.

- Stage 2B header: variational \(\beta_{ij}\) “on \(T^{1,1}\) conifold grid”; conformal ansatz \(g_{ij}=e^{2\varphi(\theta,\psi)}\bar g_{ij}\) with \(\bar g=\mathrm{diag}(\sigma^{*2},\sigma^{*2},1,1,1)\).
- Stage 3 header: \(S_{\mathrm{master}}=S_{\mathrm{APS}}|_{\Sigma^5}+\int_{T^{1,1}}d^5x\sqrt{g}[\ldots]\). Product split of the compact factors; APS is locked, \(\varphi\) is 2D.
- Status language in `AGC_Computational_Framework.py` / `complete_baseline_locked.json`: uniqueness is “within \(T^{1,1}+\Sigma^5\) APS self-dual sector”; “not all 14D fibrations.” That is a classification of the theoretical split, not a 14-dimensional mesh.
- Coupling from the compact solve toward 4D phenomenology is only through locked scalars: \(\sigma^*\), \(N_{\mathrm{gen}}\), \(\Delta\eta\), \(n_\eta\), \(8\pi G_{\mathrm{eff}}=\sigma^{*2}/C_2\), and the residual \(r\). No \(M^4\) metric components are degrees of freedom in the minimize.

There is no 14D PDE in these files.

## Quote-ready answer to the reviewer

The official β optimization does not treat all 14 dimensions as live fields. It minimizes an Einstein–YM residual for one conformal factor φ(θ,ψ) on a periodic 24×24 T^{1,1} grid, with 24 Fourier harmonics plus a Poisson warm-start (25 coefficients). The internal β_ij tensor is 5×5 because T^{1,1} is five-dimensional; only two angles are discretized. Four-dimensional spacetime, time, 3-space, and a Y^{14} mesh do not appear. The product split Y^{14} → M^4 × compact is the theoretical ansatz; numerical coupling to 4D is only through locked scalars such as σ* and 8πG_eff = σ*²/C₂(3). T_wall = 13/2 is not extracted from that residual. It is the Stage 1A Casimir sum Vol_k = j(j+1) over survivors (1/2, 1, 3/2), independent of φ, r, and any 4D field. Official lock: r = 0.095716, σ* = √3/2, continuous_knobs = 0, 8/8 PASS.

## Checks

continuous_knobs = 0

official residual unchanged

no physics files edited
