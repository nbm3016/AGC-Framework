# The Theory of Absolute Geometric Coherence

A handwritten manuscript for a reader who does not compute.

This page does not lock. `continuous_knobs = 0`. Two kinds of sentence appear. A **proof** is a multiplication or a count that closes on the page. A **proposal** is a formula written so it can be read, which this ledger has not derived. A proposal is not a theorem.

## 1. Foundations

**Proof.** The ambient space is one 14-dimensional manifold \(Y^{14}\), fibred over a 4-dimensional base \(M^4\),

\[
Y^{14}\longrightarrow M^4.
\]

The compact fibre is a product of a 5-dimensional factor and the space \(T^{1,1}\),

\[
\Sigma^5\times T^{1,1}.
\]

Four dimensions of the base, five of \(\Sigma^5\), and five of \(T^{1,1}\) are the fourteen. The base is the observational cut. It is not a chosen metric \(g_{\mu\nu}\).

The gravity letter is the pure number

\[
\kappa=8\pi G_{\mathrm{eff}}=\frac{9}{16},
\]

and the two identities a reader should keep separate are

\[
4\kappa=\frac{9}{4}, \qquad 4\kappa+1=\frac{13}{4}.
\]

The isometry of the locked 5-metric is \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times U(1)\), dimension \(7\). The holonomy of the cone \(g_C=dr^2+r^2 g_5\) is \(\mathrm{SU}(3)\), dimension \(8\), stored as holonomy. A group of dimension \(7\) does not contain \(\mathrm{SU}(3)\). The volume of \(T^{1,1}\) is the pure number \(16\pi^3/27\).

Three generations are a wall-index. The filter keeps three zeros, on the harmonics \(1/2\), \(1\), and \(3/2\), and those zeros have dimensions \(2\), \(3\), and \(4\). The integer \(3\) counts the zeros. It is not the dimension of the kernel of a Dirac operator on \(\Sigma^5\).

\(\Sigma^5\) is stored only as dimension \(5\), odd, Euler characteristic \(0\). The on-shell boundary-value problem has not been solved. The two 5-fold candidates \(\mathrm{SU}(3)/\mathrm{SO}(3)\) and the sphere \(S^5\) both have dimension \(5\) and Euler characteristic \(0\), and they are not homeomorphic, because

\[
H_2(\mathrm{SU}(3)/\mathrm{SO}(3);\mathbb{Z})\cong\mathbb{Z}/2, \qquad H_2(S^5;\mathbb{Z})=0.
\]

The stored record does not contain \(H_2\), so neither candidate is selected.

## 2. What has been multiplied out

The letters \(X,Y,Z\) are the three Pauli matrices. They are Hermitian, each squares to \(1\), and

\[
XY=iZ, \qquad YZ=iX, \qquad ZX=iY,
\]

with the opposite order equal to the minus. A word such as \(XXYIIII\) is a tensor product. Letters on different places commute.

**Proof of the fourteen generators.** Begin with \(X\) and \(Y\) on the last place. Each new place on the left replaces an old word \(\Gamma\) by \(X\otimes\Gamma\) and appends \(Y\otimes I\) and \(Z\otimes I\). After six additions the words are

\[
\begin{aligned}
&\Gamma_0=XXXXXXX, &&\Gamma_1=XXXXXXY, &&\Gamma_2=XXXXXYI, &&\Gamma_3=XXXXXZI,\\
&\Gamma_4=XXXXYII, &&\Gamma_5=XXXXZII, &&\Gamma_6=XXXYIII, &&\Gamma_7=XXXZIII,\\
&\Gamma_8=XXYIIII, &&\Gamma_9=XXZIIII, &&\Gamma_{10}=XYIIIII, &&\Gamma_{11}=XZIIIII,\\
&\Gamma_{12}=YIIIIII, &&\Gamma_{13}=ZIIIIII.
\end{aligned}
\]

Each squares to the identity on a space of dimension \(128\). Every pair anticommutes, because the two words differ on exactly one place. There are \(2^{14}=16384\) subset products, and \(16384\) is the number of entries in a \(128\times 128\) matrix. Those products are a basis. Nothing is left over in that matrix algebra.

**Proof of the slow face.** On the first two places,

\[
M=YZ,\qquad B_{11}=XZ,\qquad B_{13}=ZI.
\]

Then \(MB_{11}=-i B_{13}\), so \(MB_{11}B_{13}=-i I_4\). If a \(4\times 4\) matrix anticommutes with all three, it both commutes and anticommutes with \(B_{13}\), hence it is zero. There is no fourth anticommuting direction. The matrices that commute with the three are \(I\) and

\[
J_1=ZX,\qquad J_2=-ZY,\qquad J_3=-IZ,
\]

with \(J_1 J_2=i J_3\). Face times flow is every \(4\times 4\) matrix.

**Proof of the volume and the exhaust.** Multiply the fourteen words in order, one place at a time. On each of the first six places the letters produce \(YZ=iX\). On the last place they produce \(XY=iZ\). The phase is \(i^7=-i\), and the word is \(XXXXXXZ\). The Hermitian volume is minus that word,

\[
\Omega=-XXXXXXZ.
\]

Charge conjugation, built by alternating \(Y\) and \(Z\) from the right, is

\[
C=ZYZYZYX,
\]

and \(C\Gamma_k C=\Gamma_k^{\mathsf T}\) for each of the fourteen. Their product is

\[
E=\Omega C=-i\,YZYZYZY, \qquad E^2=-I_{128}.
\]

\(E\) is anti-Hermitian and traceless. The eight signed elements \(\pm I,\pm\Omega,\pm C,\pm E\) close. \(\Omega\) and \(C\) share no eigenvector, because a common eigenvector would give \(E\) a real eigenvalue \(\pm 1\), while \(E^2=-I\) allows only \(\pm i\).

Seven commuting signs label \(2^7=128\) lines. The lines are a basis. No line is chosen. On the line with signs \((s_M,S)\),

\[
E=i\,s_M S.
\]

The face algebra is not \(g_{\mu\nu}\). That reading is refused.

**What the cosmological number is.** The verifier reports \(\Omega_\Lambda=0.679528\), next to a paper target \(0.680\). That is an output of the locked dimensionless closure. The geometry produces pure numbers. It does not produce an absolute energy.

## 3. The algebraic check, written without a machine

The fingerprint of the baseline file is the 64-digit hash

\[
1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a.
\]

A reader uses it to know the file has not been replaced. The hash is not a proof of a physical claim.

The exhaust above is already in closed form: \(E=-i\,YZYZYZY\). A reader sees \(E^2=-I_{128}\), \(E^\dagger=-E\), and \(\operatorname{Tr} E=0\) from that word, because the phase \(-i\) makes it anti-Hermitian and a non-scalar Pauli word has trace zero. The factorization that the multiplications give is slower factor times faster factor, \(E=i\,M\Sigma\), with \(\Sigma\) the word on the last five places.

The charge conjugation \(C\) shares no line with \(\Omega\). An expectation of \(C\) in a joint line of \(\Omega\) is therefore not defined, because there is no such line. That empty intersection is not a 4-dimensional current.

## 4. What may be compared, and what may not

The dimensionless outputs a reader may set beside the paper’s own targets are the ones the verifier already prints. They are not converted to GeV.

| quantity | reported | target used by the verifier |
|----------|----------|------------------------------|
| \(\mu_{\gamma\gamma}\) | \(1.086571\) | \(1.086400\) |
| \(\Omega_\Lambda\) | \(0.679528\) | \(0.680\) |
| \(w_0\) | \(-0.987585\) | \(-1\) |
| residual | \(0.095716\) | the higher-resolution closure |
| stages | \(8/8\) pass | the same closure |
| continuous knobs | \(0\) | \(0\) |

The fifteen open words — color, occupancy, one \(\tau\), one hop branch, a length, a warp, a Chern number, a GeV, a metric, a further fibration class, a 4-dimensional equation, and Newton’s constant — may be spoken beside the tokens. Speech does not select a member. \(\kappa\) is not Newton’s constant. The holonomy \(\mathrm{SU}(3)\) is not a color name.

## 5. How to read the formulae

Every displayed equation that is marked **proof** can be checked by the Pauli products in §2 and by counting places. Every displayed equation that is marked **proposal** is on the page so a reader can see it. It has no derivation under it.

\[
n_{\mathrm{LOCK}}=35, \qquad n_{\mathrm{promoted}}=0, \qquad n_{\mathrm{SOUND}}=15, \qquad \mathrm{continuous\_knobs}=0.
\]
