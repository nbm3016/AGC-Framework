# Theory complete

This page lives in `theory\`. Writing it does not lock. A formula here is not an isolate atom. `continuous_knobs = 0`. No PDG name is attached. No value is converted to GeV.

`theory\OCCUPANCY.md` is not in this folder. Occupancy below is taken from `HANDOFF_TODAY.md`, `PAGE_DERIVATION.md`, `UPDATED_ISOLATE.md`, and `OPENS_UNPACKED.md`.

## A. Ambient constitution

The ambient theory is 14-dimensional:

\[
Y^{14} \to M^4.
\]

The compact fibre is \(\Sigma^5 \times T^{1,1}\). Those factors are compact factors. They are not the ambient theory. \(4 + 5 + 5 = 14\) is the dimension of this sentence. `fibration_class` is not chosen by that arithmetic.

The filter is one three-way lock. The three parts are equal at once:

\[
\star\Psi = \Psi = \Psi^\star.
\]

The barrier is the separate eigenspace \(\star\Psi = -\Psi\).

Frozen numerics on the isolate:

\[
\begin{align*}
N_{\mathrm{gen}} &= 3, \\
n_\eta &= (3, 8, 15), \\
\tilde\lambda &= \{9/2,\, 12,\, 45/2\}, \\
\sigma^* &= \sqrt{3}/2, \\
T_{\mathrm{wall}} &= 13/2, \\
\kappa &= 9/16, \\
4\kappa &= 9/4, \\
4\kappa+1 &= 13/4.
\end{align*}
\]

\[
\frac{3+8+15}{4} = \frac{13}{2} = \frac{9/2 + 12 + 45/2}{6}.
\]

\[
\kappa = \frac{3/4}{4/3}.
\]

The swapped label \(4\kappa+1 = 9/4\) is banned in `THEORY_RULES.md`. The reading "\(9/16\) is \(G_N\)" is banned there too.

## B. Isolate locks

Continuous knobs on this list: 0.

Ambient sentence and fibre. Filter. Barrier. Clock \(\mathbb{Z}/24\), \(3 \times 8\), face \(+8\). \(N_{\mathrm{gen}} = 3\) with wall zeros \((1/2,0,0)\), \((1,0,0)\), \((3/2,0,0)\) and dimensions \(2 \oplus 3 \oplus 4\). \(n_\eta\). \(\tilde\lambda\). \(\sigma^*\) and \(\sigma^{*2} = 3/4\). \(T_{\mathrm{wall}}\). \(\kappa = 9/16\) with the live identity \(4\kappa = 9/4\) and \(4\kappa+1 = 13/4\). \(b_2 = b_3 = 1\). Isometry \(\mathrm{SU}(2) \times \mathrm{SU}(2) \times \mathrm{U}(1)\), dimension \(7 = 3+3+1\), stored as isometry. Volume \(16\pi^3/27\). \(\mathrm{Ric} = 4g\), scalar \(20\). Cone \(g_C = dr^2 + r^2 g_5\). Holonomy \(\mathrm{Hol}(g_C) = \mathrm{SU}(3)\), dimension 8, stored as holonomy. Unique spin structure and \(\mathrm{Dirac}(g_5)\). The 5-triple reconstructs \(T^{1,1}\).

## C. Forced descendants already on disk

These generated objects are already locks with extras 0. They are recorded in `HANDOFF_TODAY.md`:

- Sasaki endomorphism
- transverse Kähler data on \(S^2 \times S^2\)
- one complex line of cone spinors
- harmonic 2-class of rank 1
- Killing eigenvalues \(\pm 5/2\)
- radial wedge forms
- cone homothety as gauge

The wall inflow already computed from locked atoms is \(26/9\):

\[
\frac{4}{3} \cdot \frac{3+8+15}{12} = \frac{26}{9}.
\]

That value is a finding already fixed. It is not a new coupling.

## D. Mass map

\[
m = \frac{\kappa \, n_\eta \, \tau}{3} = \frac{3}{16}\, n_\eta \, \tau
\]

on a hop, with \(n_\eta \in \{3, 8, 15\}\) and \(\tau \in \{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}\). The zero branch is \(m = 0\).

The nine products are a CLASS/MAP family. They are written in `MASS_MAP.md`.

\(\tau\) did not close. Hop-case did not close. No locked atom selects one element of the \(\tau\) set. The integer 3 is already \(N_{\mathrm{gen}}\) in the denominator, the filter's part count, the clock index, and one entry of \(n_\eta\). \(2-\sqrt{2}\) and \(2+\sqrt{2}\) equal none of the locked rationals, and \(\sigma^{*2} = 3/4\) equals neither of their squares. The product branch and the zero branch both remain. Leftover extras: the \(\tau\) set, and hop-case.

## E. Occupancy

The counts that are already locks, extras 0:

| source | count |
|--------|-------|
| \(\mathrm{Hol}(g_C) = \mathrm{SU}(3)\), stored as holonomy | dimension \(8\) |
| \(\mathrm{Iso} = \mathrm{SU}(2) \times \mathrm{SU}(2) \times \mathrm{U}(1)\) | dimension \(7 = 3+3+1\) |
| Clock \(\mathbb{Z}/24\) | order \(24 = 3 \times 8\), face \(+8\) |

The occupancy reading did not close. A physics name is not forced by those counts. Names stay maps. No PDG mass is attached. The clock element \(+16\) is the inverse face of \(+8\). It is not a population count.

## F. Maps that survive

| map | status | extras still OPEN |
|-----|--------|-------------------|
| Warp | MAP | \(A\), \(y\), and from the slope under R11: \(k\), \(L\), \(y\) |
| Metric | MAP | metric choice |
| Color pipe | MAP | color, \(c_2\) |
| Higher derivative | MAP | coefficient unfixed |

The higher-derivative record already on disk has `n_coefficients_forced = 0` and `unique_hd_coefficients_forced = false`. The operator form is not a forced coefficient. This pass does not assign a value to that coefficient and does not add a new real. The coefficient was not one of the O1–O12 extras, so it is not folded into the count of 15 below.

Hop-mass stays MAP, with extras \(\tau\) and hop-case. Occupancy reading stays MAP.

## G. Remainder

Every extra below was asked one question: does a locked atom already force it to one value, with no new name and no new real? Each answer is no. Each stays OPEN.

| extra | kind | closed? | why it did not close |
|-------|------|---------|----------------------|
| color | NAME | No | \(\mathrm{Hol}(g_C) = \mathrm{SU}(3)\) is stored as holonomy, dimension 8. Iso has dimension \(7 = 3+3+1\). That holonomy lock does not assign unique color. |
| occupancy reading | NAME | No | Dimensions 8 and \(7 = 3+3+1\), and the clock \(3 \times 8\) with face \(+8\), are already locks. The physics reading of those counts is not forced. |
| \(\tau\) set | DISCRETE | No | The set stays \(\{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}\). No locked atom selects one element. |
| hop-case | DISCRETE | No | The nine-product branch and the zero branch \(m = 0\) both remain. |
| \(k\) | DIMENSIONFUL | No | \(T_{\mathrm{wall}} = 13/2\) is the dimensionless spectral identity. It does not fix a slope of dimension length\(^{-1}\). |
| \(L\) | DIMENSIONFUL | No | No locked atom is a length. |
| \(y\) | DIMENSIONFUL | No | No locked atom is an interval. No radius \(R_c\) is introduced. |
| GeV | DIMENSIONFUL | No | The locked scalars are dimensionless. The observer stick stays off. |
| \(M_R\) | DIMENSIONFUL | No | No locked atom is a mass scale in GeV. |
| Newton \(G_N\) | DIMENSIONFUL | No | \(\kappa = 9/16\) is the locked pure number. It does not fix Newton's constant. The reading that identifies them is banned. |
| metric choice | STRUCTURE | No | The 5-triple reconstructs \(T^{1,1}\). It does not select \(g_{\mu\nu}\). \(\eta_{\mu\nu}\), FLRW, and RS remain occupants. |
| \(A\) | STRUCTURE | No | The cone is \(g_C = dr^2 + r^2 g_5\). \(\sigma^* = \sqrt{3}/2\) is the 5-fold shape. Neither fixes the warp profile. |
| \(c_2\) | STRUCTURE | No | The Euler cup-square 2 is the \(\mathrm{U}(1)\) self-pairing. It does not fix \(c_2\) of an \(\mathrm{SU}(3)\) bundle on \(S^2 \times S^2\). |
| `fibration_class` | STRUCTURE | No | \(4+5+5 = 14\) fixes this ambient sentence with this fibre. It does not select a class among 14-dimensional fibrations. |
| 4D EOM | STRUCTURE | No | The dynamical slot is empty. Emptiness is not an isolate atom. |

\[
n_{\mathrm{isolate\_continuous\_knobs}} = 0, \qquad n_{\mathrm{distinct\ extras\ still\ OPEN}} = 15.
\]

`PROMOTION_CANDIDATES.md` records no candidate.

## H. Ambient gamma algebra

Solved in `AMBIENT_GAMMA_SOLVE.md`. Not promoted.

\[
E = \Omega C, \qquad \Omega^2 = C^2 = +I_{128}.
\]

The real-symmetric generators are \(\{0, 3, 5, 7, 9, 11, 13\}\). The imaginary-antisymmetric generators are \(\{1, 2, 4, 6, 8, 10, 12\}\). Dropping \(\Gamma_{11}\) and \(\Gamma_{13}\) leaves the solved list \(\{0, 3, 5, 7, 9\}\). Each squares to \(+I_{128}\). The slow \(4 \times 4\) anticommutant of \(M\), \(B_{11}\), and \(B_{13}\) is \(\{0\}\).

The gate needs one value. Five values fail uniqueness. No index is selected. C1 and C2 stay UNKNOWN.

## I. Joint boundary test

The count of solutions of \(\star\Psi = \Psi = \Psi^\star\) as an asymptotic on-shell boundary condition on \(Y^{14} \to M^4\) was opened. No file exports that operator. The solution count is not a number. The test stays UNPERFORMED. The record is `JOINT_BOUNDARY.md`. The Cl(14) bracket was not counted in its place.

## J. Psi flow

Recorded in `PSI_FLOW.md`. Not promoted.

The nodes stay fixed. Data flows through them. Three nodes, \(M\), \(B_{11}\), and \(B_{13}\), meet as the observed face. Their product \(B_4 = M B_{11} B_{13}\) squares to \(-I_4\) and does not share that face. The ambient exhaust is \(E = \Omega C\). The higher residual is the unperformed joint boundary count. No index is selected. C1 and C2 stay UNKNOWN.

## K. Completion

The theory is complete as isolate + maps + remainder. The ambient gamma test is part of that completion: its solution is the five-index list, and that list is not a lock.

Completion does not mean every map became a lock.

THEORY COMPLETE - CLOSE OR LEAVE - ZERO KNOBS

Any extra closed? No

Any promotion candidate? No

Baseline touched? No

## L. Pauli proof

Proved in `PAULI_PROOF.md`. Not promoted.

The fourteen generators are the Pauli strings of the lift. The face \(M,B_{11},B_{13}\) has anticommutant \(\{0\}\) and commutant spanned by \(I,J_1,J_2,J_3\). The ordered product is \(-i\,XXXXXXZ\), the Hermitian volume is \(\Omega = -i\) times that product, the charge conjugation is \(C = ZYZYZYX\), and the cyclic bracket equals \(E = \Omega C = -i\,YZYZYZY\). The \(128\) address lines are a basis. The phase table of `PSI_FLOW.md` holds after the quadratic rephasing in the proof.

The certificate `theory/pauli_proof.py` returned `PAULI PROOF CERTIFICATE PASS` on 2026-10-08, by exact arithmetic, and matched `gammas(14)`, `charge_conjugation`, and `ambient_exhaust`.

Any extra closed by the proof? No

Any promotion candidate from the proof? No

Baseline touched by the proof? No

## M. \(C_1\) and \(C_2\)

Derived in `C1_C2_DERIVATION.md`. Not selected.

\(C_1=\mathrm{SU}(3)/\mathrm{SO}(3)\) and \(C_2=S^5=\mathrm{SU}(3)/\mathrm{SU}(2)\) both have dimension \(5\). The long exact sequences give \(H_2(C_1;\mathbb{Z})\cong\mathbb{Z}/2\) and \(H_2(C_2;\mathbb{Z})=0\), so the cosets are not homeomorphic. Every closed orientable \(5\)-fold has Euler characteristic \(0\), and the stored value selects neither. The normal metric of \(C_1\) has holonomy \(\mathrm{SO}(3)\) and one scale. The invariant metrics on \(C_2\) are \(\operatorname{diag}(p,q,q,q,q)\). The ratio \(p/q\) is not set. The round point \(p=q\) has holonomy \(\mathrm{SO}(5)\) and isometry dimension \(15\).

Each identification stays UNKNOWN. The pair is CLASS. Fixing \(p/q\) is REFUSED. `continuous_knobs` stays \(0\).

Any extra closed by this derivation? No

Any promotion candidate from this derivation? No

Baseline touched by this derivation? No

## N. One quotient group

Scored in `QUOTIENT_SYMMETRY.md`. Bin REFUSED. Not promoted.

The expression \(Q(G)=Y^{14}/G\) is written. \(G\) stays an extra, so the expression is MAP. The locked quotients that can be evaluated are a point, \(\mathbb{Z}/3\), \(\mathbb{Z}/8\), and the conformal quotient of the metrics. The claim that one such quotient locks the 15 extras stays REFUSED. Volume ratios stay pure numbers. The 15 extras are sound. They are not locks.

Any extra closed by this quotient? No

Any promotion candidate from this quotient? No

Baseline touched by this quotient? No

## O. Translation

Written in `TRANSLATION.md`. Not promoted.

Each of the 15 sound extras has a spoken word beside its engine token. Dimensionful words share one unnamed unit \(u\), with no numeral. Families are spoken by listing every member. The face stays the observed face. \(\kappa\) stays \(8\pi G_{\mathrm{eff}}\).

Any extra closed by the translation? No

Any promotion candidate from the translation? No

Baseline touched by the translation? No

## P. Sound without a single winner

Recorded in `THEORY_RULES.md`. Not a new lock.

Uniqueness is the promotion gate. A computed family can be functional, structurally sound, and leak-proof while several members remain. The conformal class, the 128 address lines, the five slow indices, the hop-mass products, the six \(\tau\) labelings, and the pair \(C_1,C_2\) are in that state. `continuous_knobs` stays \(0\). The 15 extras are sound. They are not locks.

Any extra closed by this distinction? No

Any promotion candidate from this distinction? No

Baseline touched by this distinction? No

## Q. Completion

Proved in `COMPLETION_PROOF.md`. The family is complete. The 15 extras are not promoted.

The certificate `theory/completion_proof.py` returned `COMPLETION PROOF CERTIFICATE PASS`. It counted 35 locks with extras 0, `continuous_knobs = 0`, and 12 map rows, and it left the baseline hash unchanged. The nine hop products are distinct. The clock quotients are \(\mathbb{Z}/3\) and \(\mathbb{Z}/8\).

Any extra closed by this completion? No

Any promotion candidate from this completion? No

Baseline touched by this completion? No
