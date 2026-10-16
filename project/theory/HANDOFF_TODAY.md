# FULL DAY HANDOFF - FORMULAS INCLUDED - ZERO KNOBS

Today's source is the locked frame plus the locked atoms. A candidate locks only when its type matches, the value is unique from those atoms, and extras \(= 0\). Otherwise the candidate stays a map and the formula is still written. `continuous_knobs = 0`.

`complete_baseline.json` was not rewritten. `--regenerate` was not run. The old engine files were not modified. Nothing was deleted. No commit and no push. The old tree was not touched. Trees were not moved.

## 1. Locked list

Ambient theory \(Y^{14} \to M^4\). Compact fibre only \(\Sigma^5 \times T^{1,1}\). Those factors are not the whole theory. `fibration_class` is not in this list.

Filter, one three-way lock, three parts equal at once:

\[
\star\Psi = \Psi = \Psi^\star.
\]

Barrier, separate: \(\star\Psi = -\Psi\).

Clock: \(\mathbb{Z}/24\), \(3\times 8\), face \(+8\).

Frozen numbers and groups, extras 0:

| atom | value |
|------|--------|
| \(N_{\mathrm{gen}}\) | \(3\), wall zeros \((1/2,0,0)\), \((1,0,0)\), \((3/2,0,0)\), dimensions \(2\oplus 3\oplus 4\) |
| \(n_\eta\) | \((3,8,15)\) |
| \(\tilde\lambda\) | \(9/2\), \(12\), \(45/2\) |
| \(\sigma^*\) | \(\sqrt{3}/2\), so \(\sigma^{*2}=3/4\) |
| \(T_{\mathrm{wall}}\) | \(13/2\) |
| \(\kappa = 8\pi G_{\mathrm{eff}}\) | \(9/16 = (3/4)/(4/3)\), a number, not \(G_N\) |
| \(b_2\), \(b_3\) | \(1\), \(1\) |
| Iso | \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times\mathrm{U}(1)\), dimension \(7=3+3+1\), stored as isometry |
| Vol | \(16\pi^3/27\) |
| Einstein | \(\mathrm{Ric}=4g\), scalar \(20\) |
| Cone | \(g_C = dr^2 + r^2 g_5\) |
| Holonomy | \(\mathrm{Hol}(g_C)=\mathrm{SU}(3)\), dimension 8, stored as holonomy, not color |
| 5-triple | reconstructs \(T^{1,1}\), not a 4D metric |
| Spin | unique spin structure; \(\mathrm{Dirac}(g_5)\) |
| `continuous_knobs` | \(0\) |

Kept generated locks, extras 0: Sasaki endomorphism, transverse Kähler data on \(S^2\times S^2\), one complex line of cone spinors, harmonic 2-class of rank 1, Killing eigenvalues \(\pm 5/2\), radial wedge forms, cone homothety as gauge.

Live identity of the same \(\kappa\), extras 0, recorded in section 5. It is not a new knob.

## 2. Map / open list

| open | extras | why it stays open |
|------|--------|-------------------|
| Unique color / \(\mathrm{SU}(3)_c\) | color name | Holonomy is \(\mathrm{SU}(3)\) as holonomy. Isometry does not contain \(\mathrm{SU}(3)\). |
| Unique \(g_{\mu\nu}\) | metric choice | \(\eta_{\mu\nu}\), FLRW, and RS stay occupants. |
| Unique warp value \(A(y)\) | \(A\), \(y\) | The cone does not fix a warp profile. |
| \(k\), RS slope; observer stick under R11 | \(k,L,y\) | Dimension length\(^{-1}\). R11 withdraws the stick. |
| \(c_2\) of an \(\mathrm{SU}(3)\) bundle on \(S^2\times S^2\) | \(c_2\) | Cup-square 2 is the \(\mathrm{U}(1)\) self-pairing. |
| Native GeV / \(M_R\) | GeV, \(M_R\) | Locked atoms are dimensionless. No conversion is written. |
| Landscape-wide 14D uniqueness | `fibration_class` | The fibration sentence is locked. The class is an extra. |
| Pair \(9/4\) as a lock-name | the name | \(4\kappa=9/4\) and \(4\kappa+1=13/4\). The name swaps those slots. |
| Hop-mass | \(\tau\), hop case | Formula in section 3. |
| Occupancy names | the name | Counts in section 4. Names stay names. |
| Dynamical 4D EOM slot | an EOM | The slot is empty. Emptiness is not an isolate atom. |
| \(G_N\) read as \(9/16\) | \(G_N\) | \(\kappa\) stays a pure number. |

\(\Pi_{s,t}(Y^{14})=0\) is an interface, extras 0. It is not a lock of \(g_{\mu\nu}\).

## 3. Hop-mass score

\[
m = \frac{\kappa \, n_\eta \, \tau}{3}, \qquad n_\eta \in \{3,8,15\}, \qquad \tau \in \{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}.
\]

No hop \(\Rightarrow\) \(m=0\). No GeV conversion.

Reduced on a hop, using locked \(\kappa=9/16\):

\[
m = \frac{3}{16}\, n_\eta \, \tau.
\]

| \(n_\eta\) | \(2-\sqrt{2}\) | \(3\) | \(2+\sqrt{2}\) |
|---:|---|---:|---|
| 3 | \((9/16)(2-\sqrt{2})\) | \(27/16\) | \((9/16)(2+\sqrt{2})\) |
| 8 | \((3/2)(2-\sqrt{2})\) | \(9/2\) | \((3/2)(2+\sqrt{2})\) |
| 15 | \((45/16)(2-\sqrt{2})\) | \(135/16\) | \((45/16)(2+\sqrt{2})\) |

| test | result |
|------|--------|
| Type of a dimensionless weight | pass |
| Type of a native GeV or \(M_R\) | fail |
| Unique from locked atoms | fail |
| Extras | \(\tau\), and the hop case |
| Status | MAP |

\(\kappa\) and \(n_\eta\) are locked. \(\tau\) is not fixed by those atoms, by the clock, by holonomy, or by isometry. The formula does not choose one pair. The zero is a separate case: none of \(3\), \(8\), \(15\) is zero.

## 4. Occupancy score

Counts only from Hol, Iso, and the clock.

| source | count |
|--------|-------|
| \(\mathrm{Hol}(g_C)=\mathrm{SU}(3)\), stored as holonomy | dimension \(8\) |
| \(\mathrm{Iso}=\mathrm{SU}(2)\times\mathrm{SU}(2)\times\mathrm{U}(1)\) | dimension \(7=3+3+1\) |
| Clock \(\mathbb{Z}/24\) | order \(24\), lines \(3\), seats \(8\), face \(+8\) |

| piece | type | unique | extras | status |
|-------|------|--------|--------|--------|
| Those counts | pass | pass | 0 | already the Hol, Iso, and clock locks |
| Occupancy names | fail | fail | the name | MAP |

Names stay names. They are not PDG masses. No mass number is attached to a name. The clock element \(+16\) is the inverse face of \(+8\) inside \(\mathbb{Z}/24\). It is not an occupancy population.

## 5. Live \(4\kappa\) identity

\[
\kappa = \frac{9}{16}.
\]

\[
4\kappa = 4\cdot\frac{9}{16} = \frac{9}{4}.
\]

\[
4\kappa+1 = \frac{9}{4}+1 = \frac{13}{4}.
\]

Extras 0. This is the locked number \(\kappa\), not a second gravity atom and not \(G_N\). The lock-name pair \(9/4\) stays in the map list.

## 6. Files written

| file | role |
|------|------|
| `HANDOFF_TODAY.md` | this record |
| `isolate_updated.json` | working isolate: three-way filter, live \(\kappa\) identity, twelve maps |
| `ISOLATE_UPDATE.md` | score table and V1–V6 |
| `UPDATED_ISOLATE.md` | theory sentences matched to the isolate |
| `VERIFY_TOE.md` | claim check |
| `PAGE_DERIVATION.md` | page order, with both formulas |
| `MASS_MAP.md` | hop-mass formula, image, and score |

Counts in the isolate: locks kept 30, locks added 2, locks changed 3, promotions refused 12. V1–V6 passed.

## Repo state, record only

Two repos. No monorepo. No selective push. No tree was moved in this session.

| repo | contents | terms |
|------|----------|-------|
| Public `nbm3016/AGC-Framework` | `core/` + `docs/` | MIT |
| Private `nbm3016/AGC_Framework_private` | `core`, `docs`, `falsifier`, `project`, `qec`, `dna`, `lab`, `lab2` | falsifier stays separate from project |

FULL DAY HANDOFF - FORMULAS INCLUDED - ZERO KNOBS
