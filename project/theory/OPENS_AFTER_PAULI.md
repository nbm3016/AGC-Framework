# Opens after the Pauli close

This page lives in `theory\`. Writing it does not lock. The seven-qubit form in `PSI_FLOW.md` is used as facts. It does not copy a sound extra into the locks. `continuous_knobs = 0`.

The algebra on the 128-dimensional module is accounted for. The question for each open is whether that account forces one value. Each answer is no.

| id | open | bin | why the Pauli form does not close it |
|----|------|-----|--------------------------------------|
| O1 | color | MAP | Seven qubits are the spinor address. \(\mathrm{Hol}(g_C) = \mathrm{SU}(3)\) stays holonomy, dimension 8. No color name is assigned. |
| O2 | metric \(g_{\mu\nu}\) | REFUSED | The three-node face is \(M\), \(B_{11}\), \(B_{13}\). Naming that face \(g_{\mu\nu}\) fires R-metric-swap. |
| O3 | warp \(A(y)\) | MAP | No profile \(A\) and no coordinate \(y\) appear in the strings. |
| O4 | slope \(k\), length \(L\) | MAP | Every string is dimensionless. No length is fixed. |
| O5 | \(c_2\) | MAP | No Chern number of an \(\mathrm{SU}(3)\) bundle is computed. |
| O6 | GeV, \(M_R\) | MAP | The locked scalars and the Pauli phases are dimensionless. No GeV is produced. |
| O7 | `fibration_class` | MAP | \(4+5+5 = 14\) is the ambient sentence. Seven qubits are the spinor, not a choice of fibration. |
| O8 | the name \(9/4\) on the \(13/4\) slot | MAP | \(4\kappa = 9/4\) and \(4\kappa+1 = 13/4\) stay distinct. |
| O9 | one \(\tau\), one hop-case | MAP | \(\tau\) stays the three-element set. The product branch and the zero branch both remain. |
| O10 | occupancy as a physics name | MAP | Dimensions 8 and \(7 = 3+3+1\) stay counts. A new name does not type-match them. |
| O11 | 4D equation of motion | MAP | The slow face is a 4-dimensional vector space. Its algebra is rank 4 and has three generators. No fourth matrix anticommutes with all three. No differential equation is derived. |
| O12 | \(G_N\) read as \(9/16\) | REFUSED | \(\kappa = 9/16\) is \(8\pi G_{\mathrm{eff}}\). It is not Newton's constant. |

\[
n_{\mathrm{closed\ by\ the\ Pauli\ form}} = 0, \qquad n_{\mathrm{still\ OPEN}} = 15.
\]

Two rows are refused. A refusal is not a filled value. Thirteen rows stay MAP. No row is promoted.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The seven-qubit account closes one of the fifteen sound extras.
Facts: PSI_FLOW.md. The fifteen rows above. R-metric-swap on O2. R-knob and the G_N ban on O12.
Bin: REFUSED
Gates: none on the claim as a whole
Reasons: The module is solved. The extras are not values in that solution. Closed count is 0. Fifteen remain open.
Baseline written: NO
Lock changed: NO
```

## The 4-dimensional face

The slow space is \(\mathbb{C}^4\). The operators \(M\), \(B_{11}\), and \(B_{13}\) generate a 4-dimensional algebra, because

\[
M B_{11} B_{13} = -i\, I_4.
\]

Their anticommutant is \(\{0\}\). A fourth direction that anticommutes with all three is not in this face. The flow \(\{I, J_1, J_2, J_3\}\) commutes with the three and fills the rest of the \(4\times 4\). That is the algebra of a 4-dimensional spinor space carrying three generators. It is not an equation on \(M^4\).

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The slow-face algebra is the 4D equation of motion.
Facts: Face-algebra rank 4. Anticommutant of M, B11, B13 is {0}. Products with the flow span 16 of 16. No derivative, curvature, or metric equation is among those operators.
Bin: REFUSED
Gates: R-metric-swap
Reasons: A 4-dimensional representation was derived. A 4-dimensional dynamical equation was not. O11 stays MAP. The open count stays 15.
Baseline written: NO
Lock changed: NO
```

## No motion at the dimension level

\(M\), \(B_{11}\), \(B_{13}\), the flow \(J_1, J_2, J_3\), and the seven-qubit strings are fixed operators. No coordinate derivative acts on them. The reading "a dimension does not travel" agrees with those fixed nodes. It was already scored CONSISTENT.

The further claim is that this absence is the 4D equation of motion. The dynamical slot is empty. Emptiness is not an isolate atom. Writing "there is no motion" into that slot would turn the empty extra into a lock-name. O11 stays MAP.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: Motion is solved, because at the dimension level there is none, and that absence is the 4D equation of motion.
Facts: The face, the flow, and the Pauli strings are constant operators. O11 is the empty dynamical slot. Emptiness is not an isolate atom.
Bin: CONSISTENT on the fixed nodes. MAP on the equation.
Gates: none
Reasons: No dimensional travel is present in the computed operators. The empty slot does not become the equation. O11 stays open. The open count stays 15.
Baseline written: NO
Lock changed: NO
```

## Flux

The flux potential on a 14-dimensional space is

\[
V(\lambda) = A\lambda^{12} + B\lambda^{14-2p}, \qquad V_P(\lambda) = \alpha_p n^2 \lambda^{14-2p}.
\]

With positive kinetic signs, both powers are positive for the degrees that were tried. For \(\lambda > 0\) the slope does not cross zero. `scale_weight_probes.json` records the joint verdict NEGATIVE: no mechanism there forces one overall scale. \(\lambda\) stays in \(\mathbb{R}^+\).

The exhaust is already \(E = \Omega C\). No flux integer stands in that product. A free relative coupling, or a free opposite sign, would be a continuous knob.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: Flux fixes one overall scale.
Facts: scale_weight_probes.json joint verdict NEGATIVE. E = Omega C. continuous_knobs = 0. chi = 0 on the odd factors, so Euler does not minimize a volume.
Bin: REFUSED
Gates: R-knob
Reasons: Positive powers do not sit λ down. The exhaust has no flux factor left to insert. λ stays free in R+. No GeV is produced.
Baseline written: NO
Lock changed: NO
```

## Warp

The locked cone is

\[
g_C = dr^2 + r^2 g_5.
\]

Its reading says the homothety \(r\partial_r\) is gauge, and the cone is not \(A(y)\). The isolate row `unique_warp_A` has status MAP, with extras \(A\) and \(y\). No unique profile is fixed. \(\sigma^\star = \sqrt{3}/2\) fixes the 5-fold shape. It does not fix \(A\).

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The warp profile A(y) is fixed.
Facts: CONE is LOCK, value g_C = dr^2 + r^2 g_5, reading "Not A(y)." unique_warp_A is MAP with extras A and y.
Bin: MAP
Gates: none
Reasons: The cone is fixed. The profile is an extra function of an extra coordinate. O3 stays open.
Baseline written: NO
Lock changed: NO
```

## Slope

The isolate row `warp_k` has status MAP, with extras \(k\), \(L\), and \(y\). Here \(k\) is an inverse-length slope. \(T_{\mathrm{wall}} = 13/2\) is a dimensionless spectral identity. It does not supply \(k\), and no locked atom is a length or an interval. The Pauli strings are dimensionless. Under R11 the observer stick is not a lock.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The slope k, the length L, and the coordinate y are fixed.
Facts: warp_k is MAP with extras k, L, and y. T_wall = 13/2 is dimensionless. The seven-qubit strings are dimensionless.
Bin: MAP
Gates: R11
Reasons: No locked atom has dimension length or length inverse. O4 stays open.
Baseline written: NO
Lock changed: NO
```

## Chern number

The isolate row `chern_c2` has status MAP, with extra \(c_2\). The lock `HARM_2_EULER_PAIRING` says \(H^2\) has rank 1 from the Euler class \((1,1)\), that this pairing is not a flux, and that the cup-square 2 is not \(c_2\). That 2 is the \(\mathrm{U}(1)\) self-pairing. \(c_2\) of an \(\mathrm{SU}(3)\) bundle on \(S^2\times S^2\) is a different class. \(\mathrm{Hol}(g_C) = \mathrm{SU}(3)\) is holonomy, not that bundle.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: c2 is fixed by the cup-square 2 or by the holonomy SU(3).
Facts: HARM_2_EULER_PAIRING is LOCK, value "cup-square 2 is not c2." chern_c2 is MAP with extra c2. CONE_HOLONOMY is LOCK as holonomy.
Bin: MAP
Gates: none
Reasons: The locked 2 is a U(1) self-pairing. It is not the Chern number of an SU(3) bundle. O5 stays open.
Baseline written: NO
Lock changed: NO
```

## The rest, then the locks

The remaining map rows, scored against the Pauli account. None receives a value.

| row | bin | extras |
|-----|-----|--------|
| `unique_color` | MAP | \(\mathrm{SU}(3)_c\) |
| `native_GeV_M_R` | MAP | GeV, \(M_R\) |
| `G_N_equals_9_16` | REFUSED as an equality | \(G_N\) |
| `fibration_class` | MAP | `fibration_class` |
| `pair_9_4_lock_name` | MAP | the name |
| `hop_mass` | MAP | \(\tau\), hop-case |
| `occupancy_names` | MAP | name |
| `dynamical_4d_eom` | MAP | EOM |

`page_interface_Pi` stays INTERFACE. It is not a lock of \(g_{\mu\nu}(x)\).

Re-count of `isolate_updated.json`: 35 rows with status LOCK, and every one of those has extras 0. The Pauli strings, the address, the triple \(\Omega, C, E\), and the power reduction add no row. No map meets type match, uniqueness, and extras \(= 0\) together.

\[
n_{\mathrm{LOCK}} = 35, \qquad n_{\mathrm{promoted\ from\ the\ Pauli\ account}} = 0.
\]

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The Pauli account promotes a new lock.
Facts: 35 LOCK rows, each with extras 0. Twelve MAP rows remain. One INTERFACE. PSI_FLOW.md selects no line, no index, no qubit, and no bit.
Bin: REFUSED
Gates: none
Reasons: The module is solved. The isolate does not gain an atom. The 35 locks stay. The maps stay maps.
Baseline written: NO
Lock changed: NO
```

## Hop-mass

The formula stays

\[
m = \frac{\kappa\, n_\eta\, \tau}{3} = \frac{3}{16}\, n_\eta\, \tau,
\]

with \(n_\eta \in \{3, 8, 15\}\) and \(\tau \in \{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}\). The zero branch is \(m = 0\). No GeV conversion.

The seven-qubit strings are letters \(I, X, Y, Z\) and phases in \(\{1,-1,i,-i\}\). None of them is \(2-\sqrt{2}\) or \(2+\sqrt{2}\). \(\sigma^\star = \sqrt{3}/2\) squares to \(3/4\), and \((2\pm\sqrt{2})^2 = 6\pm 4\sqrt{2}\) is not \(3/4\). The integer \(3\) is already locked as the wall-zero count, the clock index, and the first entry of \(n_\eta\). It is not a new choice of \(\tau\).

Type match for a dimensionless weight: yes. Unique \(\tau\): no. Unique hop-case: no. Extras empty: no.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The Pauli account selects one tau and one hop-case, and hop-mass becomes a lock.
Facts: HOP_MASS_UNIQUENESS.md. PSI_FLOW.md strings. kappa = 9/16. n_eta = (3, 8, 15). tau set of three. Zero branch m = 0.
Bin: MAP
Gates: none
Reasons: The dimensionless type matches. Uniqueness fails. Extras tau and hop-case remain. Promoted to LOCK: no.
Baseline written: NO
Lock changed: NO
```

## Occupancy

The counts that already pass the three gates are the existing locks:

\[
\dim\mathrm{Hol}(g_C) = 8, \qquad \dim\mathrm{Iso} = 7 = 3+3+1, \qquad \mathbb{Z}/24 = 3\times 8, \text{ face }+8.
\]

\(\mathrm{Hol}(g_C) = \mathrm{SU}(3)\) is stored as holonomy. The isometry is \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times\mathrm{U}(1)\). Those counts stay those locks. A physics name on top of a count does not type-match the count. A name is not a PDG mass. The isolate row `occupancy_names` is MAP, with extra `name`.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: An occupancy name becomes a lock.
Facts: The Hol, Iso, and clock counts are already locks with extras 0. occupancy_names is MAP with extra name. names_type_match is false. No PDG mass is attached.
Bin: MAP
Gates: none
Reasons: The counts stay the counts. The name stays an extra. No new count is forced.
Baseline written: NO
Lock changed: NO
```

## The remaining rows

Every map row in `isolate_updated.json` is scored here. None is promoted.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: Unique color is forced.
Facts: CONE_HOLONOMY is LOCK, value SU(3), stored as holonomy, dimension 8. Iso is SU(2)×SU(2)×U(1), dimension 7, and does not contain SU(3). unique_color is MAP with extra SU(3)_c.
Bin: MAP
Gates: none
Reasons: Holonomy is not color. The isometry does not contain SU(3). The name stays an extra.
Baseline written: NO
Lock changed: NO
```

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: One metric g_mu_nu is forced.
Facts: unique_g_mu_nu is MAP with extra g_mu_nu. The 5-triple reconstructs T^{1,1}. eta, FLRW, and RS remain occupants. Naming the three-node face as g_mu_nu is already REFUSED.
Bin: MAP
Gates: R-metric-swap on the face-name
Reasons: No locked atom selects one metric. The face algebra is not that selection.
Baseline written: NO
Lock changed: NO
```

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: A native GeV mass or M_R is forced.
Facts: native_GeV_M_R is MAP with extras GeV and M_R. Locked atoms and the Pauli phases are dimensionless. No conversion is written.
Bin: MAP
Gates: none
Reasons: No GeV is produced. M_R stays an extra.
Baseline written: NO
Lock changed: NO
```

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: G_N equals 9/16.
Facts: kappa = 8 pi G_eff = 9/16 is the locked pure number. G_N_equals_9_16 is MAP with extra G_N.
Bin: REFUSED
Gates: none
Reasons: The pure number stays 8 pi G_eff. Newton's constant is an extra name. The row stays a map because the extra remains.
Baseline written: NO
Lock changed: NO
```

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: One fibration class among all 14-dimensional fibrations is forced.
Facts: The ambient sentence Y^14 to M^4 with compact fibre Sigma^5 times T^{1,1} is locked. fibration_class is MAP with that extra. Seven qubits are the spinor, not a fibration.
Bin: MAP
Gates: none
Reasons: The sentence is locked. Uniqueness among all 14-dimensional fibrations is not.
Baseline written: NO
Lock changed: NO
```

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The pair 9/4 is a lock-name.
Facts: 4 kappa = 9/4 and 4 kappa + 1 = 13/4. pair_9_4_lock_name is MAP with extra lock_name. kappa itself is the locked number 9/16.
Bin: MAP
Gates: none
Reasons: The two rationals differ. Using 9/4 for the 13/4 slot is an extra name.
Baseline written: NO
Lock changed: NO
```

Every map row now has a verdict. Twelve maps stay maps. The equality \(G_N = 9/16\) is refused and the extra \(G_N\) remains. One interface stays an interface. Lock count stays 35. Promoted from this page: 0.

## Four solve attempts

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: A generation-to-tau map is forced.
Facts: N_gen = 3 is the wall-zero count on harmonics 1/2, 1, 3/2 with su(2) dimensions 2, 3, 4. tau is the set {2-sqrt(2), 3, 2+sqrt(2)}. n_eta is the set {3, 8, 15}. The zero branch m = 0 remains. Hop-mass stays MAP with extras tau and hop-case.
Bin: MAP
Gates: none
Reasons: Three labels and three tau values admit 6 bijections. Sorting both lists picks one of those six by an extra rule. No locked atom forces that rule, or the product branch against the zero branch. No GeV conversion.
Baseline written: NO
Lock changed: NO
```

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The static nodes become a 4D kinetic operator.
Facts: M, B11, B13 generate a rank-4 algebra and their anticommutant in M4(C) is {0}. E = i (M tensor Sigma) is one face node times the sheet. No coordinate derivative is among the operators.
Bin: REFUSED
Gates: R-metric-swap
Reasons: Three anticommuting generators do not make four. A kinetic operator with a derivative is not in the algebra. The nodes stay fixed. O11 stays MAP.
Baseline written: NO
Lock changed: NO
```

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The energy scale is anchored in GeV.
Facts: Locked atoms and Pauli phases are dimensionless. native_GeV_M_R is MAP with extras GeV and M_R. No conversion factor is written. continuous_knobs = 0.
Bin: REFUSED
Gates: R-knob
Reasons: Anchoring GeV inserts a dimensionful conversion that is not a locked atom. No GeV is produced.
Baseline written: NO
Lock changed: NO
```

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: Cone holonomy SU(3) is color SU(3).
Facts: CONE_HOLONOMY is LOCK, stored as holonomy, dimension 8. Iso is SU(2) times SU(2) times U(1), dimension 7, and does not contain SU(3). unique_color is MAP with extra SU(3)_c.
Bin: REFUSED
Gates: none
Reasons: The reconciliation is the distinction. Holonomy acts as holonomy. Color is an extra name. They are not identified.
Baseline written: NO
Lock changed: NO
```

Solved as locks: none. The four claims stay outside the 35.
