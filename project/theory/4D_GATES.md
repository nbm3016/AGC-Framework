# The three gates after the sign family

This page does not lock. `continuous_knobs = 0`. The input is the five-member family in `4D_SPACE.md`: the unmodified operator built from \(\Gamma_{10},\Gamma_{11},\Gamma_{12},\Gamma_{13}\), and the four operators obtained by multiplying exactly one of those generators by \(i\). The labels \(0,1,2,3\) stand for those four generators, in that order. Nothing on this page is copied into `isolate_updated.json`. The on-shell count of \(\star\Psi=\Psi=\Psi^\star\) on \(Y^{14}\to M^4\) stays unperformed. These kernels are kernels of the five flat symbols. They are not that count.

The certificate is `d4_gates.py`. It reads the isolate and both baselines. It writes nothing.

## The quadratic form of each member

Let \(\eta_a=\pm 1\) be the square of generator \(a\), so \(\Gamma_a^2=\eta_a I_{128}\). The unmodified member has every \(\eta_a=+1\). The member with timelike slot \(t\) has \(\eta_t=-1\) and the other three signs positive. The symbol at momentum \(k\) is \(S(k)=\sum_{a=0}^{3} k_a\Gamma_a\). The cross terms cancel, and

\[
S(k)^2=Q(k)\,I_{128},
\]

where

\[
Q(k)=\sum_{a=0}^{3}\eta_a k_a^2.
\]

The unmodified quadratic form is \(k_0^2+k_1^2+k_2^2+k_3^2\). The member with timelike slot \(t\) has the form \(-k_t^2+\sum_{a\neq t}k_a^2\). Each coefficient is a constant. There is no zeroth-order term.

## Signature stays a family

The ordered product of the four unmodified generators is the slow address \(MJ_2=-XXIIIII\). Multiplying one generator by \(i\) multiplies that product by \(i\), so each one-flip volume equals \(i\,MJ_2\). That operator squares to \(-I_{128}\). Its eigenvalues are \(\pm i\). An address sign is an eigenvalue \(\pm 1\) of a Hermitian involution, so a one-flip volume is not an address sign.

The unmodified member is the unique member of the five whose volume equals \(MJ_2\). The same member is the unique one whose four generators are the Hermitian Pauli generators. Both descriptions single out the member that was written down first. They do not spend the extra \(g_{\mu\nu}\). The map `unique_g_mu_nu` still lists that extra, and \(\eta_{\mu\nu}\), FLRW, and RS stay occupants of it. The one-flip members remain computed. No member is locked. The family stays CLASS.

## Curvature stays off the lock

The square \(Q(k)I_{128}\) is a constant-coefficient quadratic form. The curvature endomorphism of each member, read as the order-zero term of that square, is the zero operator. A coframe that depends on a point of \(M^4\) is not among the fourteen generators. No locked atom supplies such a function.

The lock `EINSTEIN_SCALAR_G5` stores \(\mathrm{Ric}=4g\) and scalar \(20\) for the 5-metric. The lock `TRIPLE_T11` stores that the canonical 5-triple reconstructs \(T^{1,1}\) and is not a 4-metric. The lock `CONE_HOLONOMY` stores \(\mathrm{Hol}(g_C)=\mathrm{SU}(3)\) as holonomy of the cone. Flatness of these five symbols is a property of the symbols. It is not a lock of \(g_{\mu\nu}\), and it does not move the 5-metric identities onto \(M^4\).

## The plane algebra has dimension 6

Write \(L_{ab}=\Gamma_a\Gamma_b\). For three distinct labels,

\[
[L_{ab},L_{ac}]=-2\eta_a\,L_{bc}.
\]

The two planes that use complementary pairs, \(L_{01}\) with \(L_{23}\), \(L_{02}\) with \(L_{13}\), and \(L_{03}\) with \(L_{12}\), commute. Every commutator of the six products therefore stays in their span. The six words are distinct and non-scalar, so the span has dimension 6.

When every \(\eta_a=+1\), every bracket carries the sign \(-2\). That is the Euclidean algebra already split, in `4D_SPACE.md`, into the two commuting copies \(A_i\) and \(B_i\). When \(\eta_t=-1\), the three brackets whose common index is \(t\) flip sign, and the three spatial brackets keep the sign \(-2\). The quadratic form of that member has one minus and three pluses, and the bracket is the spin representation of that orthogonal algebra.

The lock `Iso_group` stores \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times\mathrm{U}(1)\) with dimension \(7\), as the isometry of \(T^{1,1}\). A 6-dimensional algebra is not that isometry. The missing factor is the \(\mathrm{U}(1)\). These matrices are supported on the slow qubits. They act on the base spinor.

## No common propagation, and no equation in the slot

If \(Q(k)\neq 0\), then \(S(k)\) is invertible and the plane-wave kernel is \(\{0\}\). If \(k=0\), then \(S(k)=0\) and the kernel is \(\mathbb{C}^{128}\). All \(128\) address lines lie in that kernel, for every member.

If \(Q(k)=0\) and \(k\neq 0\), the timelike square is the sum of the other three squares, so the timelike component \(k_t\) is nonzero. The generators anticommute, hence

\[
\{S(k),\Gamma_t\}=-2k_t\,I_{128}.
\]

For \(v\) in the kernel, \(S(\Gamma_t v)=-2k_t v\). The kernel is contained in the image. The identity \(S(k)^2=0\) gives the opposite inclusion. Rank-nullity on \(\mathbb{C}^{128}\) then gives rank \(64\) and kernel dimension \(64\).

A momentum that is null for every one-flip member satisfies \(2k_a^2=\sum_b k_b^2\) for every \(a\). The four squares are equal, the sum is four times one square, and \(2k_0^2=4k_0^2\). The only solution is \(k=0\). The unmodified symbol vanishes only at \(k=0\) as well. A plane wave annihilated by every member is a constant spinor. The whole \(\mathbb{C}^{128}\) occurs at that momentum. The intersection does not propagate.

The null kernel of one member has dimension \(64\). The wall zeros are the labels \((j_1,j_2)=(1/2,0)\), \((1,0)\), and \((3/2,0)\), with dimensions \(2\), \(3\), and \(4\). Those labels are not vectors in \(\mathbb{C}^{128}\). The sum \(2+3+4=9\) does not partition \(64\), and it does not partition \(128\). No address line is selected.

The five equations \(D\Psi=0\) are five equations, one for each member. The intersection, constant spinors, is what remains if a section is required to solve every member at once. No locked atom requires that. The isolate row `dynamical_4d_eom` is MAP, its slot is empty, and its extra is `EOM`. Emptiness is not an isolate atom. Filling the slot would need a type match, uniqueness, and extras \(= 0\), together. Uniqueness fails, and the extra is still present. The slot is not written.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-12
Claim: After the five-member sign family, a locked atom selects one signature, forces a curvature onto M^4, or fills dynamical_4d_eom.
Facts: Volume equals MJ2 only for the unmodified member. Each one-flip volume equals i MJ2. Q(k) is constant-coefficient for every member, with order-zero term 0. EINSTEIN_SCALAR_G5 is Ric=4g on the 5-metric. TRIPLE_T11 is not a 4-metric. CONE_HOLONOMY is Hol(g_C)=SU(3) as holonomy. The plane algebra of each member has dimension 6. Iso_group has dimension 7. The only momentum in every plane-wave kernel is k=0, with kernel C^128. The isolate slot is empty, status MAP, extra EOM. unique_g_mu_nu still carries g_mu_nu. continuous_knobs = 0.
Bin: REFUSED
Gates: promotion, which needs type match and uniqueness and extras = 0 together. The metric extra. The EOM extra. The 5-metric type of Ric=4g and of the 5-triple.
Reasons: The five members stay computable, so the signature stays CLASS. Flatness of a symbol is not a metric lock. Five equations are not one equation, and the constant intersection is not imposed. The slot stays empty.
Baseline written: NO
Lock changed: NO
```

\[
n_{\mathrm{LOCK}}=35, \qquad n_{\mathrm{promoted}}=0, \qquad n_{\mathrm{SOUND}}=15, \qquad \mathrm{continuous\_knobs}=0.
\]
