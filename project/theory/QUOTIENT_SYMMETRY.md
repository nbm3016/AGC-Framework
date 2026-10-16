# Quotient by one symmetry

This page lives in `theory\`. Writing it does not lock. `continuous_knobs = 0`.

The proposal has two parts. The expression is the quotient formula. The lock-claim is that the formula annihilates the 15 sound extras and turns leftover volume ratios into physical scales. The expression is written below. The lock-claim stays refused.

## The groups the locks already contain

Three symmetry objects are locked.

| object | value | where it acts |
|--------|-------|----------------|
| isometry | \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times U(1)\), dimension 7 | the locked 5-metric |
| holonomy | \(\mathrm{Hol}(g_C)=\mathrm{SU}(3)\), dimension 8 | the cone \(g_C=dr^2+r^2 g_5\), stored as holonomy |
| clock | \(\mathbb{Z}/24\), order \(\mathrm{lcm}(8,3,8)\) | the monodromy of the wall data |

The isometry has dimension 7. Dimension 7 is smaller than dimension 8, so this group does not contain \(\mathrm{SU}(3)\). The action that is locked is the action on the 5-metric. That action is transitive on \(T^{1,1}\), and the quotient of a transitive action is a point. A point has no list of 15 invariants.

Holonomy is parallel transport on the frame bundle of the cone. The lock stores it as holonomy. It is not a diffeomorphism group of \(Y^{14}\), and it is not a color group.

The clock is a cyclic group of order 24 on the wall monodromy. Its quotient data are the numbers already locked: 3 lines, 8 seats, face \(+8\). Those integers are counts. They are not a metric, a Chern number, a warp, or a GeV.

No lock names \(G_2\), \(F_4\), \(E_6\), \(E_7\), or \(E_8\), and no lock names a discrete group other than the clock as a symmetry of the whole 14-fold. A new name for \(G\) would be an extra.

## The quotient that is already proved

`complete_baseline.json` stores the conformal quotient

\[
C_{\mathrm{phys}} = \mathrm{Riem}(Y^{14})\,/\,\mathrm{Conf}(Y^{14}).
\]

The gauge group is the positive rescalings \(g\mapsto \lambda^2 g\). The no-go theorem in that same record says: with `continuous_knobs = 0`, classical geometry and topology do not break that conformal invariance, so no unique absolute energy or length is generated from the locked data. Volume ratios and spectral invariants stay dimensionless. \(\mathrm{Vol}(T^{1,1})=16\pi^3/27\) is already one such ratio. It is a pure number.

A volume ratio left after a quotient is a pure number of the same kind. It has the type of \(\kappa\) and of the \(T^{1,1}\) volume. It does not have the type of a GeV, of \(M_R\), or of \(G_N\).

## Expression

A formula that fails uniqueness is still written. Its bin is MAP. Writing it does not promote it.

The groups whose action is already a locked atom are

\[
\mathcal{G}_{\mathrm{locked}} = \{\mathrm{Iso}(g_5),\; \mathbb{Z}/24,\; \mathrm{Conf}(Y^{14})\}.
\]

Holonomy stays off this list. The lock stores \(\mathrm{SU}(3)\) as holonomy of the cone, and a holonomy representation is not an action on the points of \(Y^{14}\).

The three quotients that can be written from those groups are

\[
\begin{aligned}
T^{1,1}\,/\,\mathrm{Iso}(g_5) &= \mathrm{pt},\\[4pt]
(\mathbb{Z}/24\mathbb{Z})\,/\,\langle 3\rangle &\cong \mathbb{Z}/3\mathbb{Z},\\[4pt]
(\mathbb{Z}/24\mathbb{Z})\,/\,\langle 8\rangle &\cong \mathbb{Z}/8\mathbb{Z},\\[4pt]
C_{\mathrm{phys}} &= \mathrm{Riem}(Y^{14})\,/\,\mathrm{Conf}(Y^{14}).
\end{aligned}
\]

Here \(\langle 3\rangle=\{0,3,6,9,12,15,18,21\}\) is the unique subgroup of order 8, and the quotient has order 3. The element \(+8\) has order 3, \(\langle 8\rangle=\{0,8,16\}\), and the quotient has order 8. Those orders are the locked clock counts: 3 lines and 8 seats. \(\mathrm{Vol}(T^{1,1})=16\pi^3/27\) is the locked volume ratio. It is dimensionless.

The overarching expression, with no group substituted, is

\[
Q(G) = Y^{14}/G, \qquad \rho(G) = \text{a volume ratio of } Q(G).
\]

\(G\) is an extra. No exceptional group is written in its place. \(\rho(G)\) is a pure number when the volumes exist. The formula is the whole family. No member is selected. Bin of the expression: MAP.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The quotient expression Q(G) = Y^14/G, and the volume-ratio readout ρ(G), may be written with G left unnamed.
Facts: The three locked quotients above. Vol(T^{1,1}) = 16π^3/27. continuous_knobs = 0. Write ≠ lock.
Bin: MAP
Gates: none
Reasons: The formula uses no new real and names no new group. G stays an extra, so the expression is not unique. It is written. It is not a lock.
Baseline written: NO
Lock changed: NO
```

## What a quotient can force

Suppose a group \(G\) were already one of the 35 locks, acted on \(Y^{14}\), and the quotient were unique. A sound extra would become a lock only if that quotient returned one value, of the same type as the extra, with no further choice. The 15 extras do not become locks under that test. They stay sound.

| extra | output of the locked quotients |
|-------|--------------------------------|
| color | holonomy stays holonomy; the isometry does not contain \(\mathrm{SU}(3)\) |
| occupancy name | the counts 8, \(7=3+3+1\), and \(Z/24\) stay counts |
| \(\tau\), hop-case | the sets stay sets |
| \(k\), \(L\), \(y\), \(A\) | no length and no warp profile is a conformal invariant that the no-go isolates |
| \(c_2\) | the cup-square 2 stays the \(U(1)\) self-pairing |
| GeV, \(M_R\) | the no-go: no absolute energy or length |
| metric | conformal superspace is a space of classes, and no class is selected as one \(g_{\mu\nu}\) |
| `fibration_class` | the locked fibration is unchanged |
| 4D equation | a quotient manifold is not a derivative |
| \(G_N\) | \(\kappa=9/16\) stays \(8\pi G_{\mathrm{eff}}\) |

Choosing an exceptional \(G\) in order to make one of these rows unique would be a new structure. Its embedding, if it had a modulus, would be a continuous knob. The knob count is a lock equal to 0, so that choice is not made.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: One global symmetry group of Y^14, exceptional or discrete, quotients the 14-fold and thereby locks the 15 sound extras, with physical scales equal to the leftover volume ratios.
Facts: Iso_group SU(2)×SU(2)×U(1), dimension 7, stored as isometry of the 5-metric. CONE holonomy SU(3), dimension 8, stored as holonomy. clock Z/24 on the wall monodromy. complete_baseline.json conformal quotient C_phys = Riem(Y^14)/Conf(Y^14), no-go theorem, continuous_knobs = 0. Vol(T^{1,1}) = 16π^3/27. The 15 extras in PROMOTION_CANDIDATES.md.
Bin: REFUSED
Gates: R-knob on naming a new G. The absolute-scale no-go on reading a volume ratio as an energy or a length. The G_N ban on reading 9/16 as Newton's constant. R-metric-swap on reading the quotient as one g_μν.
Reasons: The symmetry groups that are locked act on the 5-metric, on the cone frames, and on the wall clock. The quotient already proved on the 14-fold is the conformal quotient, and its theorem is that no absolute scale comes out. No locked group returns one value for any of the 15 extras. The 15 are sound. They are not locks. The lock count stays 35.
Baseline written: NO
Lock changed: NO
```

\[
n_{\mathrm{LOCK}} = 35, \qquad n_{\mathrm{promoted}} = 0, \qquad n_{\mathrm{SOUND}} = 15, \qquad \mathrm{continuous\_knobs} = 0.
\]
