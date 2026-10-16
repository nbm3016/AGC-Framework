# Working page

Nothing on this page is copied into `isolate_updated.json`. `continuous_knobs = 0`. The formulae are the ones the atoms and the ordered generators actually support. A choice that is not forced is left visible.

## The 4D equation

The fourteen generators are produced in a fixed order by the Pauli lift. All of them square to \(+I\) and anticommute. On the coordinate space \(\mathbb{R}^{14}\) with that same order, the flat coframe operator is

\[
D_{14} = \sum_{k=0}^{13} \Gamma_k \frac{\partial}{\partial y^k}.
\]

No coupling is inserted. No metric \(g_{\mu\nu}\) is inserted. The base operator is not the sum over \(\Gamma_0,\ldots,\Gamma_3\). Those four move the fibre. The fibre-blind generators are \(\Gamma_{10},\Gamma_{11},\Gamma_{12},\Gamma_{13}\), and the flat Euclidean operator they define is derived in `4D_SPACE.md`. The five-member sign family is checked in `4D_GATES.md`. No signature is selected. The curvature endomorphism of each member is zero. The isolate slot `dynamical_4d_eom` stays empty.

## The boundary condition, as far as the atoms go

The filter already in the isolate is \(\star\Psi=\Psi=\Psi^\star\), and on the self-dual line that is \(j_2=0\). The charge conjugation already constructed satisfies \(C\Gamma_k C=\Gamma_k^{\mathsf T}\). Together they constrain the algebraic value of a section at a boundary point.

They do not yet define a differential boundary-value problem on \(Y^{14}\to M^4\). The operator \(D_{14}\) above is available for that problem. The domain, the fall-off, and the solution count are not evaluated on this page. The count stays unperformed. The matrix identity \(\ker\Omega\cap\ker C=\{0\}\) is not used as a substitute.

## The floor rule, from the weight

On the first-slice families the index barrier used by the expansion notes is

\[
\operatorname{index}=\max\bigl(0,\ \lfloor w(2j-3)\rfloor\bigr),
\]

with weight \(w=p+q\) on \(T^{p,q}\) and on \(Y^{p,q}\), and weight \(w=a+b+c\) on \(L^{a,b,c}\). For the locked base \(T^{1,1}\) one has \(p=q=1\), so \(w=2\) and

\[
w(2j-3)=2(2j-3)=4j-6.
\]

On the self-dual line \(j_2=0\) this is the Module A rule \(\max(0,\lfloor 4j_1-6\rfloor)\). The coefficient \(4\) and the shift \(6\) are the weight \(w=2\) of \(T^{1,1}\). The three zeros at \(j_1=1/2,1,3/2\) follow by the same arithmetic as before.

This is a specialization of the family rule. It is not \(\dim\ker D_5\), and closed \(T^{1,1}\) is not an APS carrier. The geometric 5-dimensional Dirac kernel remains empty under \(|\lambda|\ge 5/2\).

## \(\Sigma^5\), without a selection

Both cosets match dimension 5, oddness, and Euler characteristic 0. They differ by

\[
H_2(C_1;\mathbb{Z})\cong\mathbb{Z}/2, \qquad H_2(C_2;\mathbb{Z})=0.
\]

The fibration does not compute \(H_2(\Sigma^5)\). Spin is not required. The working alternative is the pair. No name is assigned.

## The cubic, the clock, \(\kappa\), and the page

The hop set is the root set of

\[
(x-3)(x^2-4x+2)=0,
\]

because \(x^2-4x+2=0\) gives \(x=2\pm\sqrt{2}\) and the remaining factor gives \(x=3\). No root is selected.

The clock order is \(\mathrm{lcm}(8,3,8)=24\). The unique subgroup of order 8 has index 3. The element \(+8\) has order 3.

\[
\kappa=\frac{\sigma^{*2}}{C_2(3)}=\frac{3/4}{4/3}=\frac{9}{16}=8\pi G_{\mathrm{eff}}.
\]

The page equation is \(\Pi_{s,t}(Y^{14})=0\). It is the cut. A measurement of a locked pure number \(\rho\) is written

\[
\text{reading}=\rho\cdot u,
\]

where \(u\) is one external unit. The theory does not vary \(u\), so \(u\) is not a continuous knob. No numeral is assigned to \(u\). The 15 sound rows are the translations this reading speaks. They stay sound. They are not locks, and \(\kappa\) is not \(G_N\).

\[
n_{\mathrm{LOCK}}=35, \qquad n_{\mathrm{promoted}}=0, \qquad n_{\mathrm{SOUND}}=15, \qquad \mathrm{continuous\_knobs}=0.
\]
