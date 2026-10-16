# Witness audit

Audit only. No new lock. Nothing promoted. `complete_baseline.json` was not rewritten. `continuous_knobs = 0`.

The six lock statements are the public constitution list: the 14-dimensional fibration, the withdrawn observer stick, the wall-index reading of \(N_{\mathrm{gen}}=3\), cone holonomy as not color, the 5-metric spectral triple reconstructing \(T^{1,1}\) rather than \(M^4\), and the non-uniqueness of `fibration_class`.

## Locks

| lock | witness | on_disk |
|------|---------|---------|
| Ambient theory is \(Y^{14}\to M^4\). \(\Sigma^5\) and \(T^{1,1}\) are compact factors. A 5-fold is not the ambient theory. | `isolate_updated.json` (`ambient_statement`, `five_fold_is_ambient` false, `compact_fibre`); `ISOLATE_UPDATE.md` V1 | WITNESSED |
| Rule R11. The observer stick is not physics. Locks that enter are dimensionless. No compact radius and no GeV stick. | `MASTER_PLAN.md` rule 2; `theory/PAGE_DERIVATION.md` | WITNESSED |
| \(N_{\mathrm{gen}}=3\) is the Module A wall-index count. It is not \(\ker D_5\). | `MASTER_PLAN.md` rule 3; `native_aps_index.json` (`honest_name`) | WITNESSED |
| \(\mathrm{Hol}(g_C)=\mathrm{SU}(3)\) is holonomy of the cone, not color. | `CONE_CURVATURE_REPORT.md` F4; `CONNES_RECONSTRUCT_REPORT.md` | WITNESSED |
| The 5-metric spectral triple reconstructs \(T^{1,1}\), not \(M^4\). No unique 4D spectral triple. | `FINISH_CHAIN.md` (`TRIPLE_T11`); `CONNES_RECONSTRUCT_REPORT.md` | WITNESSED |
| `fibration_class` is not unique. A factor result is not a landscape-wide impossibility. | `isolate_updated.json` (`fibration_class_unique` false, map `fibration_class`); `STATUS.md` Open row “Global vacuum uniqueness” | WITNESSED |

## Holes

Diff of `STATUS.md` and `theory/THEORY_RULES.md` against `review_record.json`. Disagreements are listed. They are not resolved. Every review row has `promoted` false. Neither doc stores that field on these eight rows.

| hole | review bin | review extra | STATUS.md | THEORY_RULES.md |
|------|------------|--------------|-----------|-----------------|
| positive_eom | UNKNOWN | empty section | Says the dynamical ideal is empty and the positive equation is unscored. Does not use the bin UNKNOWN. | Silent. |
| unique_color | FORBIDDEN | SU(3)_c | Filing section says the menu types it FORBIDDEN. The Open table still lists H1 Color as Open, not forced. | Silent. |
| G_N | FORBIDDEN | G_N | Filing says \(G_N\) is a missing extra and \(\kappa=9/16\) is not \(G_N\). It does not use the bin FORBIDDEN for this row. | Calls Newton’s constant an open physics hole. Bans the reading \(9/16=G_N\). Does not use FORBIDDEN. |
| D5_spectrum | UNKNOWN | eigenvalue list | Silent. | Silent. |
| warp_factor | CONSISTENT | A, y | Filing says CONSISTENT, not FORCED. Partial row E3 still says the warp value is Open. | Silent. |
| g_mu_nu | OPEN-FIELD | g_mu_nu | Open table H0 says the live Einstein metric is not derived. Does not use the bin OPEN-FIELD. | Silent. |
| fibration_class | CLASS | fibration_class | Open table says landscape-wide uniqueness remains open. Does not use the bin CLASS. | Silent. |
| c2 | UNKNOWN | c2 | Silent. The filing says the filter does not project \(c_2\) out. It does not store the bin or the extra. | Silent. |

## Public defects

Public files checked: `README.md`, `STATUS.md`. `WORKING_GEOMETRY.md` is not on disk, so it contains no sentence to flag.

| file | sentence | defect |
|------|----------|--------|
| `STATUS.md` | “The locked AGC core is the zero-knob computational skeleton on \(\Sigma^5\times T^{1,1}\).” | Seats the locked core on the compact factors. The isolate says the ambient theory is \(Y^{14}\to M^4\) and `five_fold_is_ambient` is false. |

No sentence in `README.md` or `STATUS.md` deletes a topic by \(\star\Psi=\Psi\). The filing sentence says the filter does not delete topics. No sentence in those files states one of the eight holes as forced. `README.md` lists global uniqueness, unique HD coefficients, \(M_R\), continuum \(r\to 0\), and full anomaly cancellation as Open.

WITNESS AUDIT — NO NEW LOCKS — NOTHING PROMOTED

Unwitnessed locks: 0

Hole disagreements: 8

Public defects: 1
