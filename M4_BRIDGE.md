# How the compact isolate maps to M^4

Audit from existing AGC files only. No re-solve. Official lock untouched: \(r=0.095716\), \(\sigma^*=\sqrt{3}/2\), \(T_{\mathrm{wall}}=13/2\), `continuous_knobs=0`, 8/8 PASS.

## Verdict

Mixed: theoretical fibration language + scalar maps; no live 4D metric.

The repo states a 14D fibration \(Y^{14}\to M^4\) as topology language. The numerical bridge is algebraic maps from locked compact scalars (\(\sigma^*\), \(N_{\mathrm{gen}}\), \(\Delta\eta\), \(\tilde\lambda\), \(\beta\) residuals, \(8\pi G_{\mathrm{eff}}=\sigma^{*2}/C_2\)). There is no derived \(Y^{14}\to M^4\) reduction: no live \(g_{\mu\nu}\), no Einstein–Hilbert \(\int d^4x\sqrt{-g}R_4\), and no Kaluza–Klein integral over extra dimensions.

## Fibration / 14D statements found

| file | location | quote | class |
|------|----------|-------|-------|
| `TECHNICAL_BRIEFING.md` | line 21 | “Fixed 14D fibration Y^{14} → M^4 with Σ^5 domain wall (no free radii after topology definition).” | ansatz |
| `stage3_master_variational.py` | header L3–5 | “Master variational equation on Σ⁵ × T^{1,1}.” \(S_{\mathrm{master}}=S_{\mathrm{APS}}|_{\Sigma^5}+\int_{T^{1,1}}d^5x\sqrt{g}[\ldots]\) | ansatz (compact product split; not \(M^4\)) |
| `complete_baseline.json` | `conformal_quotienting.physical_space_definition` | `C_phys = Riem(Y^{14}) / Conf(Y^{14})` | conformal quotient |
| `complete_baseline.json` | `no_go_statement` | cannot break global conformal invariance of the 14D fibration | conformal quotient / No-Go |
| `final_paper_draft.md` | §2.2.11 / L423–428 | No-Go on \(Y^{14}\); \(C_{\mathrm{phys}}=\mathrm{Riem}(Y^{14})/\mathrm{Conf}(Y^{14})\) | conformal quotient |
| `paper_appendix.tex` | ~L690–705 | same No-Go + Conformal Superspace | conformal quotient |
| `final_paper_draft.md` / `STATUS.md` | uniqueness tables | “not all 14D fibrations”; global uniqueness **Open** | uniqueness-scope |
| `AGC_Computational_Framework.py` | status_classification partial | “This sector only; not all 14D fibrations” | uniqueness-scope |
| `final_paper_draft.md` | L521 | “Eq. (2A.1) was never integrated on the 14D curvature.” | uniqueness-scope / negative (not a reduction formula) |
| `anomaly_beyond_index.json` | result string | “Eq. 2A.1 is schematic; Stage 2A never integrates it on 14D curvature” | negative (not a reduction formula) |

No row is a reduction formula (no \(\int_{Y^{10}}\), no 4D Einstein tensor from a 14D metric).

## Compact → 4D formulae found

| quantity | formula | function | inputs | 4D field as argument? |
|----------|---------|----------|--------|------------------------|
| \(8\pi G_{\mathrm{eff}}\) | \(\sigma^{*2}/C_2(3)\), \(C_2=4/3\) | `eight_pi_g_eff` in `stage2b_beta_variational.py` | locked \(\sigma^*\) | no |
| Einstein–YM coupling in β residual | \(\beta_{ij}-8\pi G_{\mathrm{eff}}\,T^{\mathrm{YM}}_{ij}\) | `einstein_ym_residual` | compact \(\beta_{ij}\), \(T^{\mathrm{YM}}\) on \((\theta,\psi)\); scalar \(G_{\mathrm{eff}}\) | no |
| \(\mu_{\gamma\gamma}\) | \(1+\sigma^{*2}|\sum_g e^{i\Delta\eta_g}|^2/(4 N_{\mathrm{gen}})+\beta_\square/(2\pi C_2)\) | `predict_mu_gammagamma` / `kk_interference_amplitude` | \(\sigma^*\), \(\Delta\eta\), \(N_{\mathrm{gen}}\), \(\beta_\square\) | no |
| \(\Omega_\Lambda\) | \(\sigma^*\sqrt{2/N_{\mathrm{gen}}}\,(1-\beta_{\mathrm{full}}/5)\) | `predict_omega_lambda` | \(\sigma^*\), \(N_{\mathrm{gen}}\), \(\beta_{\mathrm{full}}\) | no |
| \(w_0\) | \(-1+\beta_{\mathrm{full}}/(5\pi)\) | `predict_w0_dark_energy` | \(\beta_{\mathrm{full}}\) only | no |
| Weyl \(\lambda\) | \(g\to\lambda^2 g\) identified as gauge on \(C_{\mathrm{phys}}\) | prose + `conformal_quotienting` JSON; not a solver DOF | overall conformal factor | no (quotiented, not a field) |
| Observational conversion | one external yardstick, withdrawn after comparison | posture in `STATUS.md` / draft / baseline; not a function of \(g_{\mu\nu}\) | observer unit | no |
| Volume probes \(m_k\sim\sqrt{\tilde\lambda_k}/R\) | tested then rejected as a stabilizer | `volume_final_squeeze` in `stage_moduli_stabilization.py` | locked \(\tilde\lambda\); \(R\) not solved | no live 4D metric |

```39:44:stage2b_beta_variational.py
def eight_pi_g_eff(sigma_star: float) -> float:
    """
    Effective 8πG from locked Stage 1B modulus  [σ²/C₂(3) normalization].
    Replaces bare 8π to match compact T^{1,1} flux scale.
    """
    return sigma_star ** 2 / C2_SU3
```

```144:187:stage4_phenomenology.py
def kk_interference_amplitude(locked: LockedPhenomenology) -> float:
    """|Σ_g exp(i Δη_g)|² from locked η-lattice phases."""
    z = sum(complex(math.cos(d), math.sin(d)) for d in locked.delta_eta)
    return float(abs(z) ** 2)

def predict_mu_gammagamma(locked: LockedPhenomenology) -> Tuple[float, float, float]:
    """Diphoton signal strength: KK tower + β dressing (unchanged formula)."""
    ...
def predict_omega_lambda(locked: LockedPhenomenology) -> float:
    return locked.sigma_star * math.sqrt(2.0 / locked.n_gen) * (1.0 - locked.beta_full / 5.0)

def predict_w0_dark_energy(locked: LockedPhenomenology) -> float:
    ...
    return -1.0 + locked.beta_full / (5.0 * PI)
```

`kk_interference_amplitude` is a phase sum over locked \(\Delta\eta_g\). It is not a Kaluza–Klein reduction integral.

`complete_baseline.json` lists \(8\pi G_{\mathrm{eff}}\), \(\mu_{\gamma\gamma}\), \(\Omega_\Lambda\), \(w_0\) as dimensionless conformal scalars, invariant under \(g\to\lambda^2 g\).

## Live 4D metric / Einstein–Hilbert / KK

**Absent as code.** Present only as naming or as rejected probes.

| object | status | evidence |
|--------|--------|----------|
| 4D metric \(g_{\mu\nu}(t,\mathbf{x})\) | ABSENT | `build_grid` returns only \(\theta,\psi\); `DIM=5` is the compact \(\beta_{ij}\) index; `DIMENSIONAL_SCOPE.md` lists \(M^4\), time, 3-space as not discretized |
| \(\int d^4x\sqrt{-g}\,R_4\) | ABSENT | no such integrand in `stage4_phenomenology.py`, `stage2b_beta_variational.py`, or `_solve_beta_higher_res` |
| KK measure \(\int_{Y^{10}}\) or \(\int_{Y^{14}}\) | ABSENT as code | `kk_interference_amplitude` is \(\lvert\sum e^{i\Delta\eta_g}\rvert^2\); Stage 3 integrates \(d^5x\) on \(T^{1,1}\) for \(\varphi\), not 4D |
| Time / 3-space coordinates | ABSENT | not arguments of `predict_*` or `einstein_ym_residual` |
| 14D curvature integral | ABSENT | `anomaly_beyond_index.json`: “Eq. 2A.1 is schematic; Stage 2A never integrates it on 14D curvature” |
| Identifying \(8\pi G_{\mathrm{eff}}\) with \(M_{\mathrm{Pl}}\) | prose only, rejected as dynamics | `moduli_stabilization.json` / `volume_final_squeeze`: “Identifying it with a physical Planck mass chooses an external unit system, not a volume-stabilizing potential” |

```97:100:stage2b_beta_variational.py
def build_grid(n: int) -> Tuple[np.ndarray, np.ndarray, float]:
    theta = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    psi = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return theta, psi, theta[1] - theta[0]
```

## What is not a reduction

- “Fixed 14D fibration \(Y^{14}\to M^4\)” in `TECHNICAL_BRIEFING.md` is topology language. It does not supply a metric ansatz \(ds^2_{14}=g_{\mu\nu}dx^\mu dx^\nu+g_{mn}dy^m dy^n\) as a coded object.
- “Not all 14D fibrations” / global uniqueness **Open** is a landscape-scope disclaimer, not a map to 4D GR.
- Weyl gauge \(\lambda\) and \(C_{\mathrm{phys}}=\mathrm{Riem}(Y^{14})/\mathrm{Conf}(Y^{14})\) remove overall scale; they do not reduce 14D Einstein equations to 4D Einstein equations.
- Observational conversion is an external unit convention, withdrawn after comparison; it is not a derived 4D Einstein–Hilbert coefficient.
- Stage-4 “KK tower” in comments is the locked \(\eta\)-lattice phase sum plus \(\beta\) dressing, not a KK tower of 4D graviton modes.
- \(T_{\mathrm{wall}}=13/2\) remains \(\sum j(j+1)\); `dimensionful_4d_tension` is false in the locked JSON.
- `physical_bridge.json` inventories dimensionless geometric maps vs quantities not determined (\(\alpha_{\mathrm{em}}\), CKM, \(M_R\)). It does not add a 14D→4D PDE.

## Quote-ready answer to the reviewer

The compact \(T^{1,1}\) isolate does not come with a derived \(Y^{14}\to M^4\) reduction in this repository. Briefing and appendix language fix a 14D fibration and a product \(\Sigma^5\times T^{1,1}\); the solvers never assemble a 4D metric or an Einstein–Hilbert term. The coded bridge is algebraic. Effective \(8\pi G_{\mathrm{eff}}=\sigma^{*2}/C_2(3)\) is a locked compact ratio used as the coupling in the \((\theta,\psi)\) Einstein–YM residual. Stage-4 \(\mu_{\gamma\gamma}\), \(\Omega_\Lambda\), and \(w_0\) are closed-form functions of \(\sigma^*\), \(N_{\mathrm{gen}}\), \(\Delta\eta\), and the locked \(\beta\) residuals; none takes \(g_{\mu\nu}\) as an argument. A function named `kk_interference_amplitude` sums locked phases \(\sum e^{i\Delta\eta_g}\); it is not a Kaluza–Klein integral. Weyl \(\lambda\) is quotiented, and observational conversion is an external yardstick, not a 4D field. Official lock: \(r=0.095716\), \(\sigma^*=\sqrt{3}/2\), \(T_{\mathrm{wall}}=13/2\), `continuous_knobs=0`, 8/8 PASS.

## Checks

continuous_knobs = 0

official residual unchanged

T_wall = 13/2 unchanged

no physics files edited
