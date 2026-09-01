# Reviewer reproduction audit

This file answers a reviewer sentence using existing AGC artifacts only. No new masses, mixings, gates, or parameters. Official lock frozen: \(r=0.095716\), \(\sigma^*=\sqrt{3}/2\), \(T_{\mathrm{wall}}=13/2\), \(\theta_{13}=7.953^\circ\), `continuous_knobs=0`, 8/8 PASS.

Reviewer sentence: *If the solver and the 8-gate pipeline really close with zero free parameters and reproduce the full fermion spectrum, mixings, and cosmology from the same discrete network, that would be a genuine shift. Until those artifacts are run and checked by others, it remains an ambitious private construction rather than established physics.*

## Verdict

The documented 8-stage pipeline does close on disk: `--full` and `python AGC_Computational_Framework.py --full` reports 8/8 PASS with `continuous_knobs=0` and official \(r=0.095716\). That is not a full Standard Model fermion spectrum. Locked JSON contains residual-NLO A4 PMNS, APS zero-mode mass *ratios*, and light-neutrino eV values that use a PDG \(\Delta m^2_{21}\) anchor. Charged-lepton masses, quark masses, a locked physical CKM, unique \(M_R\), and a full cosmological model (\(H_0\), \(\Omega_m\), CMB, …) are **ABSENT** as keys. This audit does not convert the project into established physics. It documents what a third party can rerun and what the files already contain.

## How a third party can run it

From `README.md` Quick start (no `--regenerate`):

```
python AGC_Computational_Framework.py --full
```

This audit ran both (MPLBACKEND=Agg). Live `--full` printed 8/8 PASS, \(\beta\) residual 0.095716 (full Hessian), \(\mu_{\gamma\gamma}=1.086571\), \(\Omega_\Lambda=0.679528\). Trust demo printed verification seal 8/8 PASS and wrote demo JSON/PNG (those writes were reverted so this audit leaves only this markdown). Numbers below are quoted from the restored on-disk `verification_log.txt` and `predictions.json`, which match that live run.

`--regenerate` was not run.

## Claim table

| Reviewer claim | Classification | Artifact | Notes |
|----------------|----------------|----------|-------|
| Solver / 8-gate pipeline closes | DERIVED | `verification_log.txt`; live `--full` stdout | Eight stages PASS; score 8/8. Not eight extra “gates” beyond those stages. |
| Zero free parameters | DERIVED | `predictions.json` `continuous_knobs`; baseline; log Stage 3 | Value 0. Observational conversion is a unit convention, not a knob in the locked equations. |
| Full fermion spectrum | ABSENT | no keys `m_e`, `m_mu`, `m_tau`, quark masses | `physical_bridge.json` `not_determined_by_locked_geometry` already lists charged-lepton and quark maps as not forced. |
| Mixings (PMNS, official) | DERIVED | `predictions.pmns_angles_deg` / `final_flavor_prediction` | \(\theta_{12}=31.003^\circ\), \(\theta_{23}=45.682^\circ\), \(\theta_{13}=7.953^\circ\), \(\delta_{\mathrm{CP}}=-146.694^\circ\). High-scale geometric lock. |
| Mixings (CKM, physical) | ABSENT as locked CKM | `ckm_angles_status`: `exploratory_holonomy` | Exploratory holonomy angles exist; they are not the official flavor lock. |
| Cosmology (full ΛCDM) | ABSENT | no keys `H_0`, `Omega_m`, `Omega_b`, `sigma_8`, CMB | Only Stage-4 scalars \(\Omega_\Lambda\), \(w_0\) (and \(\mu_{\gamma\gamma}\)) are present. |
| Same discrete network | DERIVED | `predictions.locked_inputs` | Shared: \(\tilde\lambda=\{4.5,12,22.5\}\), \(\sigma^*\), \(N_{\mathrm{gen}}=3\), \(n_\eta=(3,8,15)\), \(\Delta\eta/\pi\), \(\beta\) residuals. |
| Artifacts can be run by others | DERIVED | README commands; this audit ran them | Third-party check is possible from the repo; that does not make the theory established physics. |
| Established physics | ABSENT | no such claim required by the files | This document does not assert established physics. |

## Fermion and mixing inventory

Fail-closed: if the key is not in `predictions.json` / `complete_baseline.json`, the row is ABSENT.

| quantity | present? | classification | source key | notes |
|----------|----------|----------------|------------|-------|
| \(N_{\mathrm{gen}}=3\) | yes | DERIVED | `locked_inputs.n_gen` | Native APS count. |
| \(\tilde\lambda=\{4.5,12,22.5\}\) | yes | DERIVED | `locked_inputs.lambda_targets` | Survivors \((1/2,0),(1,0),(3/2,0)\). |
| Spectral ratios \(m_2/m_1=\sqrt{8/3}\), \(m_3/m_1=\sqrt{5}\) | yes | DERIVED | `predictions.mass_ratios` | APS zero-mode ratios; not a charged-fermion map. |
| PMNS residual-NLO A4 | yes | DERIVED | `pmns_angles_deg`, `final_flavor_prediction` | Official high-scale lock; \(\theta_{13}=7.953^\circ\). |
| PMNS LO A4 | yes | DERIVED | `pmns_angles_lo_A4_deg` | Pre-NLO geometric A4. |
| \(\delta_{\mathrm{CP}}=-146.694^\circ\) | yes | DERIVED | `delta_cp_deg` | Same NLO package. |
| Light \(m_{1,2,3}\) (eV) | yes | ANCHORED | `m_nu_eV` | File states eV values use PDG \(\Delta m^2_{21}\) and a \(10^{-2}\) eV convention (`REF_DELTA_M2_21=7.53e-5` in `stage4_phenomenology.py`; `physical_bridge.json`). |
| \(\Delta m^2_{21}\) | yes | ANCHORED | `delta_m2_21_eV2` = \(7.53\times 10^{-5}\) | PDG reference, not geometric. |
| \(\Delta m^2_{31}/\Delta m^2_{21}\) | yes | DERIVED (ratio) / ANCHORED (eV²) | `delta_m2_ratio_31_21` | Ratio from locked map; absolute eV² uses the PDG anchor. |
| Neutrino hierarchy | yes | DERIVED | `neutrino_hierarchy`: `normal` | From the locked ratio chain. |
| CKM angles | yes as exploratory | not official lock | `ckm_angles_deg` + `ckm_angles_status` | Status string is `exploratory_holonomy`. |
| CKM/PMNS unitarity deviation | yes | DERIVED | `ckm_unitarity_dev`, `pmns_unitarity_dev` | \(\sim 10^{-16}\). |
| \(M_R\) (GeV) | key null | ABSENT as unique GeV | `heavy_majorana_scale_test.M_R_GeV`: `null` | `unique_heavy_majorana_scale_forced`: false. |
| Low-energy RG \(\theta_{13}\) | key null | ABSENT | `low_energy_theta13_deg`: `null`; `rg_theta13_computed`: false | Stays 7.953°. |
| \(m_e, m_\mu, m_\tau\) | no keys | ABSENT | — | Fail-closed. |
| Quark masses \(m_u,\ldots,m_t\) | no keys | ABSENT | — | Fail-closed. |
| Physical low-energy CKM | no locked key | ABSENT | — | Exploratory holonomy is not this. |
| Full SM fermion spectrum | no | ABSENT | — | Do not claim it. |

## Cosmology inventory

| quantity | present? | classification | source key | notes |
|----------|----------|----------------|------------|-------|
| \(\Omega_\Lambda\) | yes | DERIVED | `omega_lambda` = 0.679528 | Stage-4 map of \(\sigma^*\), \(N_{\mathrm{gen}}\), \(\beta_{\mathrm{full}}\). |
| \(w_0\) | yes | DERIVED | `w0_dark_energy` = −0.987585 | \(w_0=-1+\beta_{\mathrm{full}}/(5\pi)\). |
| \(\mu_{\gamma\gamma}\) | yes | DERIVED | `mu_gammagamma` = 1.086571 | Diphoton signal strength, not a cosmological parameter. |
| Custodial \(\rho\) | yes | DERIVED | `rho_custodial` | Stage-4 scalar. |
| Proton lifetime log10 yr | yes | ANCHORED (label) | `proton_lifetime_log10_yr` | Geometric combination; “years” is a unit convention in `physical_bridge.json`. |
| \(H_0\) | no key | ABSENT | — | |
| \(\Omega_m\), \(\Omega_b\), \(\Omega_k\) | no keys | ABSENT | — | |
| \(\sigma_8\), \(n_s\) | no keys | ABSENT | — | |
| CMB / BAO spectra | no keys | ABSENT | — | |
| Full ΛCDM cosmology | no | ABSENT | — | Do not claim it. |

## Same discrete network?

Shared locked inputs in `predictions.json` → `locked_inputs`:

- \(\tilde\lambda=\{4.5,12,22.5\}\)
- \(\sigma^*=\sqrt{3}/2\)
- \(N_{\mathrm{gen}}=3\)
- \(n_\eta=(3,8,15)\), \(\Delta\eta/\pi=\{1/4,2/3,5/4\}\)
- \(\beta_\square\), \(\beta_{\mathrm{full}}\), official \(\beta_{\mathrm{residual,new}}=0.095716\)

Stage-4 maps and the 8-stage verify path consume this same list. That is a discrete compact network plus algebraic Stage-4 maps. It is not a live 4D Einstein–Hilbert cosmology or a complete fermion Yukawa matrix (`M4_BRIDGE.md`, `DIMENSIONAL_SCOPE.md`).

## What the reviewer asked that is not in the repo

- A full SM fermion spectrum (charged leptons + quarks + neutrinos as one derived set)
- Locked physical CKM (only exploratory holonomy)
- Unique heavy Majorana scale \(M_R\) in GeV (`M_R_GeV`: null)
- Parameter-free RG from \(\theta_{13}=7.953^\circ\) to low-energy \(\approx 8.5^\circ\)
- Full cosmological parameter set beyond \(\Omega_\Lambda\) and \(w_0\)
- A certification of “established physics”

No substitutes are invented for those rows.

## Checks

continuous_knobs = 0

official residual unchanged

theta13 = 7.953 deg unchanged

no physics files edited

no new parameters
