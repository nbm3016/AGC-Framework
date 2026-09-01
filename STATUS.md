# AGC Status: Proven / Partial / Open

**Reviewer-facing classification of the locked skeleton.**  
This file does not change any locked numeric or physics claim. It only states, in one place, what is proven, what is proven only inside an explicit boundary, and what remains open after the probes already run.

| Item | Value |
|------|--------|
| Numerical source of truth | [`complete_baseline.json`](complete_baseline.json) |
| Machine-readable mirror of this file | `complete_baseline.json` → `status_classification` |
| Numerical strengthening checksums | [`numerical_strengthening.json`](numerical_strengthening.json) |
| `continuous_knobs` | **0** |
| Core verification | **8/8 PASS** |
| Framework version | `stage1+2+3+3B+4-higher-res` |

---

## Scope of the locked core

The locked AGC core is the zero-knob computational skeleton on \(\Sigma^5\times T^{1,1}\): native APS-neutral self-dual zero modes generate \(N_{\mathrm{gen}}=3\) (survivors \((1/2,0)\), \((1,0)\), \((3/2,0)\); derived \(\tilde\lambda=\{4.5,12,22.5\}\)); the squashing modulus is frozen at \(\sigma^*=\sqrt{3}/2\); the \(\eta\)-lattice is the unique triple \(n_\eta=(3,8,15)\) with \(\Delta\eta/\pi=\{1/4,2/3,5/4\}\); the official higher-resolution \(\beta\) residual is the computational lock \(r=0.095716\) (full Hessian, \(N_h=24\), grid 24); residual-NLO A4 supplies the official high-scale flavor angles; Stage-4 \(\mu_{\gamma\gamma}\), \(\Omega_\Lambda\), and \(w_0\) are strictly downstream. Absolute scale and overall volume \(R\) are not dynamical moduli: they are closed by observational conversion posture (geometry yields only dimensionless quantities and discrete invariants; a temporary observer-supplied conversion is used only for dimensionful comparison and is then withdrawn). Reproduce with `python AGC_Computational_Framework.py --full`.

---

## Proven

| Result | Locked value | Justification |
|--------|--------------|---------------|
| Native APS \(N_{\mathrm{gen}}\) | **3** | Geometry-generated APS-neutral self-dual zero-mode count on \(\Sigma^5\); not \(\tilde\lambda\)-seeded |
| Derived \(\tilde\lambda\) of zero modes | \(\{4.5,\,12.0,\,22.5\}\) | Output of the three survivors \((1/2,0)\), \((1,0)\), \((3/2,0)\); not an input filter |
| \(\sigma^*\) (shape / squashing) | \(\sqrt{3}/2\approx 0.866025\) | Stable minimum of geometric \(V(\sigma)\) with \(m^2>0\) |
| \(n_\eta\) / \(\Delta\eta/\pi\) | \((3,8,15)\) / \(\{1/4,\,2/3,\,5/4\}\) | Unique triple from native \(j_1\) |
| \(\beta\) residual (official computational lock) | **0.095716** | Full Hessian solve, \(N_h=24\), grid 24; bit-identical on official 24/24 in numerical strengthening. This is a frozen-slice proxy, not a proof that continuum \(r\to 0\) |
| Residual-NLO A4 flavor (high-scale) | \(\theta_{12}=31.003^\circ\), \(\theta_{23}=45.682^\circ\), \(\theta_{13}=7.953^\circ\), \(\delta_{\mathrm{CP}}=-146.694^\circ\) | A4 residual plus parameter-free \(\sqrt{r}\) NLO from the locked residual; official high-scale prediction; no further \(\theta_{13}\) corrections inside this package |
| Absolute \(m_1,m_2,m_3\) (eV) | \(4.206\times 10^{-3}\), \(9.643\times 10^{-3}\), \(5.063\times 10^{-2}\) | Stage-4 map from locked geometry plus the PDG \(\Delta m^2_{21}\) unit convention for the light sector (not a pure-geometry GeV) |
| \(\Sigma m_\nu\) | \(6.448\times 10^{-2}\) eV | Sum of the same light-sector map |
| \(\mu_{\gamma\gamma}\) | **1.086571** | Stage-4, strictly downstream of locked Stages 1–3 |
| \(\Omega_\Lambda\) | **0.679528** | Stage-4, same |
| \(w_0\) | **−0.987585** | Stage-4 residual-driven equation of state |
| `continuous_knobs` | **0** | Master variational closure; no free Wilson coefficients, fluxes, or potentials in the locked equations |
| Core verification | **8/8 PASS** | Stages 1A, 1B, 1C, 2A, 2B, 3, 3B, 4 |

---

## Partial

Each row is proven only inside the stated boundary. Crossing that boundary is not claimed.

| Topic | What is proven | Exact boundary of the proof |
|-------|----------------|-----------------------------|
| Shape stabilization (\(\sigma^*\)) | Full shape freeze at \(\sqrt{3}/2\) by geometric \(V(\sigma)\) plus residual tension | Not a dynamical freeze of overall volume; volume \(R\) is closed by observational conversion, not by a unique volume potential |
| Sector vacuum uniqueness | Alternatives to \(N_{\mathrm{gen}}\), \(r\), \(j_2\), \(\sigma\), \(\eta\)-lattice ruled out **within** the \(T^{1,1}+\Sigma^5\) APS self-dual sector | This sector only; not all 14D fibrations |
| Controlled-class uniqueness \(\mathcal{G}_{\mathrm{SE}}\) | Theorem: \(N_{\mathrm{gen}}=3\) is shared (28/28 first-slice SE bases); locked \(\tilde\lambda/\sigma^*\) isolate \(T^{1,1}\) inside the first-slice Sasaki–Einstein class | Landscape-wide uniqueness remains open; bases outside the first slice untested |
| \(\varphi\) / APS / domain-wall freeze | Massive \(\varphi\); topological freeze of off-sector modes and wall position | Proven within the locked sector only |
| \(\Sigma^5\) domain-wall tension \(T_{\mathrm{wall}}\) | Discrete spectral invariant \(13/2=\sum j(j+1)\); independent of residual \(r\) | Not a Chern index; not a \(\mathrm{GeV}^3\) tension |
| Flavor monodromy completion | A4 plus locked \(\sqrt{r}\) NLO is the completion inside that package; official high-scale angles unchanged | No further discrete completion is forced; S4/S3 appear only if APS evenness is dropped |
| Discrete anomaly sector | APS / analytic-torsion / trace-mod-6 sector forced by locked topology | Wall residual \(\eta=26/9\neq 0\); full 4D / Green–Schwarz / Witten polynomial cancellation is not forced |

---

## Resolved / closed (not Open)

These items are **not** open derivation targets and are **not** continuous knobs.

| Topic | Status | Boundary |
|-------|--------|----------|
| Absolute scale | **Closed by observational conversion posture** | Geometry produces only dimensionless quantities and discrete invariants. Absolute scale is not a free parameter of the dynamics and is not generated by the geometry. A single external observational conversion (measurement yardstick) is supplied by the observer when a dimensionful comparison is required; it is temporary, task-dependent, and withdrawn after the comparison. It never appears in the locked equations. |
| Overall volume modulus \(R\) | **Closed by observational conversion posture** | Same as absolute scale. Internally, residual \(\lambda\in\mathbb{R}^+\) is Weyl gauge on \(C_{\mathrm{phys}}=\mathrm{Riem}(Y^{14})/\mathrm{Conf}(Y^{14})\). |

`continuous_knobs` remains **0**.

---

## Open

These entries remain open **after** the probes already run. They are **not** closed, re-interpreted, or absorbed into Proven/Partial. Negative probes are recorded as reasons the gap is still open, not as a proof that no future parameter-free geometry could exist.

| Gap | Why it remains open after probes already run |
|-----|-----------------------------------------------|
| Global vacuum uniqueness (all 14D fibrations) | Controlled-class uniqueness isolates \(T^{1,1}\) only inside \(\mathcal{G}_{\mathrm{SE}}\). The global-uniqueness probe does not test bases outside the first slice. Landscape-wide uniqueness is therefore still open. |
| Unique higher-derivative Wilson coefficients | Controlled HD / UV Wilson probe: no unique coefficient (0/9); Lovelock form only; residual-NLO \(\sqrt{r}\) already consumed. Unique HD beyond residual NLO remains open. |
| Heavy Majorana scale \(M_R\) | Locked data are dimensionless. No parameter-free \(\mathrm{GeV}\) for \(M_R\) is generated by the geometry. Observational conversion sets units for comparison only and is withdrawn; it does not determine \(M_R\) as a geometric output. |
| Continuum \(\beta\) residual \(r\to 0\) | Residual-protection probes P1 (decimal rigidity) and P2 (positive floor) both fail. Residual mass-gap probe: \(\tau_{\mathrm{res}}=r\sigma^{*2}\) is linear in \(r\) (\(d^2V/dr^2=0\)). Official \(r=0.095716\) is unchanged as the computational lock; continuum vanishing is not protected. |
| Full anomaly cancellation beyond the index | Discrete APS/AS/trace-mod-6 sector is forced (Partial). \(\mathrm{Tr}\,F^3\), mixed, \(\mathrm{tr}\,R^4\), Green–Schwarz, and Witten polynomials are not forced; wall residual \(26/9\neq 0\). |
| \(\theta_{13}\) high-scale \(\to\) low-energy remainder (\(\sim 0.55^\circ\)) | Bridge probe: no parameter-free geometric map from the locked high-scale \(\theta_{13}=7.953^\circ\) to \(\sim 8.5^\circ\). Official high-scale angle is unchanged. The remainder sits outside topological determination (RG / \(M_R\) / higher-order effects are not supplied by the locked skeleton). |

Controlled ansatz expansion (five finite enlargements) produced **no** new parameter-free closure of any row above. That is why the open list was not reduced by those enlargements; it is not a sixth independent physics claim.

---

## The open list is current, not final forever

The Open table is the **current** status of the locked skeleton after the probes already run. It is **not** declared complete for all time. Future **parameter-free** geometric structures — no new continuous knobs, no re-optimization of Stages 1–3, no alteration of locked numerics, and no re-interpretation of existing negative probes — may reduce this list. Until such a structure is exhibited and verified at `continuous_knobs = 0`, every Open entry remains Open.

---

## `continuous_knobs = 0` and 8/8 PASS

- `continuous_knobs = 0` in the locked equations, in `complete_baseline.json`, and in numerical strengthening.
- Core verification: **8/8 PASS** (`python AGC_Computational_Framework.py --full`).
- Official \(\beta\) residual lock remains **0.095716**. Diagnostic grids in `numerical_strengthening.json` do **not** replace that lock.

---

## Pointers

1. **Numerical source of truth:** [`complete_baseline.json`](complete_baseline.json) — locked values, `final_locked_state`, and `status_classification`.
2. **Numerical strengthening checksums:** [`numerical_strengthening.json`](numerical_strengthening.json)

Recorded SHA-256 at strengthening time (certifies bit-reproducibility of the official 24/24 residual, 8/8 PASS, and locked phenomenology digits; it does **not** freeze later documentation wrappers such as `status_classification`):

| File | SHA-256 (strengthening record) |
|------|--------------------------------|
| `complete_baseline.json` (locked numerics snapshot) | `0f209b8e829d8f136ebf965d1ead23a7475ac547f8c600cb3c2d758c3a5f6b41` |
| `predictions.json` | `e0520f7b48c5d3c66b068deb9d7624ae3a539de838d7fa7839aaf3000c250ef6` |
| `verification_log.txt` (before log append) | `8f3bf91d1cca1633d3e2d97d22b3b3c04ab62ff5e68d9b311d4e5a4a0d774f8a` |
| `verification_log.txt` (after log append) | `8b7a9d0f70e1b34d082532f76b70a5de4943c6390eb597125bf42cfbaed3669e` |

Adding or updating `status_classification` changes the live hash of `complete_baseline.json` without changing locked numeric fields. The strengthening record remains the checksum of the locked-numerics snapshot.

---

**DOCUMENTATION HARDENED – PROVEN / PARTIAL / OPEN STATUS LOCKED – DOOR LEFT OPEN FOR FUTURE GEOMETRIC INSIGHT**
