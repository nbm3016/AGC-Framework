# Verify the theory

Each claim is a sentence in `UPDATED_ISOLATE.md`. The source is a file already named here or a row in `isolate_updated.json`. A map stays a map when type, uniqueness, and extras do not all pass.

| claim | source | verdict | reason |
|-------|--------|---------|--------|
| Ambient dimension is 14 and the fibration is \(Y^{14}\to M^4\) | `isolate_updated.json` row `ambient_theory` | CONFIRMED | The row states the 14-dimensional fibration. |
| \(\Sigma^5\) and \(T^{1,1}\) are compact factors, not the whole theory | `isolate_updated.json` `compact_factors_only`; `five_fold_is_ambient` false | CONFIRMED | Both factors are listed. The 5-fold is not the ambient theory. |
| `fibration_class` is not selected | map `fibration_class`; `FINISH_CHAIN.md`; `falsifier/WALL_UNIQUENESS.md` | CONFIRMED | Uniqueness among 14-dimensional fibrations stays an extra. |
| Filter is the one equality \(\star\Psi=\Psi=\Psi^\star\) | isolate `filter.statement`; lock `filter_three_way` | CONFIRMED | Three parts, equal at once, extras 0. |
| Barrier \(\star\Psi=-\Psi\) is separate | isolate `barrier` | CONFIRMED | `is_the_filter` is false. It is not the wall-index formula. |
| Cone \(g_C=dr^2+r^2 g_5\) | isolate `CONE`; `cone_curvature.json` | CONFIRMED | Forced from the locked 5-metric. Homothety stays gauge. |
| \(\mathrm{Hol}(g_C)=\mathrm{SU}(3)\) as holonomy | isolate `CONE_HOLONOMY`; `CONE_CURVATURE_REPORT.md` | CONFIRMED | Stored as holonomy, dimension 8. |
| `cone_holonomy.json` was given a new equality row | `cone_holonomy.json` | CONFLICT | The older row still says UNKNOWN. It was not edited. The live holonomy lock is the curvature certificate. |
| Unique spin structure and 5-triple reconstruct \(T^{1,1}\) | `SPIN_DIRAC_REPORT.md`; isolate `SPIN_T11`, `TRIPLE_T11` | CONFIRMED | Reconstruction dimension is 5. |
| Isometry \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times\mathrm{U}(1)\), dimension 7 | isolate `Iso_group` | CONFIRMED | Stored as isometry. Dimension \(3+3+1\). It does not contain \(\mathrm{SU}(3)\). |
| \(\kappa=8\pi G_{\mathrm{eff}}=9/16\) is the gravity seat | isolate `eight_pi_G_eff_number` | CONFIRMED | Pure number \((3/4)/(4/3)\). |
| \(4\kappa=9/4\) and \(4\kappa+1=13/4\) | isolate `kappa_live_identity` | CONFIRMED | \(4\cdot(9/16)=9/4\) and \(9/4+1=13/4\). Extras 0. |
| \(G_N\) is \(9/16\) | map `G_N_equals_9_16` | CONFLICT | The theory keeps \(9/16\) as a pure number. \(G_N\) is an extra. |
| Pair \(9/4\) is a lock-name | map `pair_9_4_lock_name` | CONFLICT | \(4\kappa\) is \(9/4\). \(4\kappa+1\) is \(13/4\). The name that swaps those slots stays a map. |
| Clock: three lines, eight seats, shared face \(+8\) of order 3 | isolate `clock_Z24` | CONFIRMED | Unique order-8 subgroup has index 3. Least positive order-3 element is 8. |
| \(N_{\mathrm{gen}}=3\), harmonics \(2\oplus 3\oplus 4\) | isolate `wall_zero_count` | CONFIRMED | The integer 3 is frozen as the wall-zero count. |
| Volume \(16\pi^3/27\), \(\mathrm{Ric}=4g\), scalar 20 | isolate `VOL_T11`, `EINSTEIN_SCALAR_G5` | CONFIRMED | Both rows are locks, extras 0. |
| 4-dimensional spin of the three harmonics is known | `falsifier/SPIN4D_PROBE.md` | ABSENT | The probe leaves 4-dimensional spin unknown. The theory says unknown. |
| Hop-mass formula \(m=\kappa n_\eta\tau/3\) is written and is a MAP | `MASS_MAP.md`; map `hop_mass` | CONFIRMED | Dimensionless type matches. \(\tau\) and the hop case are extras. The image is not one atom. GeV conversion is false. |
| Hop-mass is a lock, or a GeV | map `hop_mass` | CONFLICT | Uniqueness fails. Native GeV stays a different map. |
| Occupancy counts are \(\dim\mathrm{Hol}=8\), \(\dim\mathrm{Iso}=7\), and the clock \(3\times 8\), face \(+8\) | locks `CONE_HOLONOMY`, `Iso_group`, `clock_Z24` | CONFIRMED | Those integers are unique and have extras 0. They stay those locks. |
| Occupancy names are locks or PDG masses | map `occupancy_names` | CONFLICT | A name is an extra. It is not a count and not a mass. |
| Page \(\Pi_{s,t}(Y^{14})=0\) is a cut | isolate `page_interface` | CONFIRMED | Status INTERFACE. `is_g_mu_nu` is false. |
| A specific \(\eta_{\mu\nu}\), FLRW, or RS metric was locked | map `unique_g_mu_nu` | CONFLICT | Those occupants stay maps. |
| Unique \(A(y)\), RS \(k\), or \(c_2\) was locked | maps `unique_warp_A`, `warp_k`, `chern_c2` | CONFLICT | Each still carries an extra. |
| Photon coupling is determined | `FOUR_ROWS.md`; `physical_bridge.json` | ABSENT | The seat is the locked \(\mathrm{U}(1)\) factor, dimension 1. The coupling is not written. No extra is added. |
| Higgs number is locked | `FOUR_ROWS.md`; no scalar row in `locks` | ABSENT | \(\sigma^*\) is a 5-fold shape. The Higgs seat stays empty. No vacuum number is added. |
| Dynamical 4D EOM is an isolate atom | map `dynamical_4d_eom`; `4D_GATES.md` | CONFLICT | The slot is empty. Emptiness is not an atom. `EOM` is already one of the fifteen. No second extra is added. |
| Wall inflow \(26/9\) | baseline identity \(C_2(3)\sum n_k/12=26/9\) | CONFIRMED | \((4/3)\cdot(26/12)=26/9\). It is a finding. It is not a new coupling. |
| `continuous_knobs = 0` | isolate `continuous_knobs` | CONFIRMED | Value 0. |
| Native GeV or \(M_R\) is a lock | map `native_GeV_M_R`; `FOUR_ROWS.md` | CONFLICT | Both are dimensionful extras already among the fifteen. The hop-mass image stays dimensionless. No GeV numeral is added. |

No theory sentence above treats a CONFLICT or ABSENT item as a lock.
