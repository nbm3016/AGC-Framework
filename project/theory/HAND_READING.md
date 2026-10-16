# A hand reading

This page is for a reader with a pencil. It does not lock. `continuous_knobs = 0`. No step below asks for a machine. Each identity is a multiplication of Pauli matrices.

The computational certificates remain in `PAULI_PROOF.md` and `COMPLETION_PROOF.md`. They check the same identities. They are not a second theory.

## 1. What is fixed before any matrix

The ambient space is a 14-dimensional manifold \(Y^{14}\) fibred over a 4-dimensional base \(M^4\). The compact fibre is a product \(\Sigma^5\times T^{1,1}\). That sentence is the whole geometric postulate used here.

The pure number carried by the gravity letter is

\[
\kappa = 8\pi G_{\mathrm{eff}} = \frac{9}{16}.
\]

Multiply by 4:

\[
4\kappa = \frac{9}{4}, \qquad 4\kappa+1 = \frac{13}{4}.
\]

Thirty-five quantities of this kind are locked, each with no extra choice attached. Three fermion generations are the wall-index: three zeros, on harmonics \(1/2\), \(1\), and \(3/2\), with dimensions \(2\), \(3\), and \(4\). That count is not the dimension of the kernel of a Dirac operator on a 5-fold.

The isometry of the locked 5-metric is \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times U(1)\), dimension 7. The holonomy of the cone \(g_C=dr^2+r^2 g_5\) is \(\mathrm{SU}(3)\), dimension 8, stored as holonomy. Dimension 7 does not contain a copy of \(\mathrm{SU}(3)\). The volume of \(T^{1,1}\) is \(16\pi^3/27\), a pure number.

Fifteen further words are spoken beside these tokens and are not locks: a color name, an occupancy name, one value of \(\tau\), one hop branch, a length, a warp, a Chern number, a GeV, a metric, a fibration class beyond the sentence above, a 4-dimensional equation, and Newton's constant. \(\kappa\) is not Newton's constant.

## 2. The only algebra used

On one qubit the matrices are

\[
X=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad
Y=\begin{pmatrix}0&-i\\i&0\end{pmatrix},\quad
Z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
\]

Each is Hermitian and squares to \(1\). The products a reader needs are \(XY=iZ\), \(YZ=iX\), and \(ZX=iY\). The opposite order is the minus of each. Distinct letters from \(\{X,Y,Z\}\) anticommute.

A word such as \(XXYIIII\) means a tensor product, left factor slowest. Factors on different qubits commute. A word of phase \(+1\) is Hermitian and squares to the identity, because each letter does. Its trace is zero unless every letter is \(I\), because the trace of \(X\), of \(Y\), and of \(Z\) is zero and trace multiplies across a tensor product.

Two such words anticommute when the number of qubits on which both letters lie in \(\{X,Y,Z\}\) and differ is odd. They commute when that number is even.

## 3. How the fourteen generators are built

Begin with two generators on the rightmost qubit: \(\Gamma_0=X\) and \(\Gamma_1=Y\). To add a qubit on the left, replace every old generator \(\Gamma\) by \(X\otimes\Gamma\), and append \(Y\otimes I\) and \(Z\otimes I\).

Do this until there are fourteen generators. They sit on seven qubits. Writing \(X\) for the letter \(X\) and leaving \(I\) blank in the reading, the list is:

\[
\begin{aligned}
\Gamma_0 &= XXXXXXX, &
\Gamma_1 &= XXXXXXY, &
\Gamma_2 &= XXXXXYI, &
\Gamma_3 &= XXXXXZI,\\
\Gamma_4 &= XXXXYII, &
\Gamma_5 &= XXXXZII, &
\Gamma_6 &= XXXYIII, &
\Gamma_7 &= XXXZIII,\\
\Gamma_8 &= XXYIIII, &
\Gamma_9 &= XXZIIII, &
\Gamma_{10}&= XYIIIII, &
\Gamma_{11}&= XZIIIII,\\
\Gamma_{12}&= YIIIIII, &
\Gamma_{13}&= ZIIIIII.
\end{aligned}
\]

The pattern is the induction. On \(n\) qubits there are \(2n\) generators. \(\Gamma_0\) is \(X\) on every qubit. \(\Gamma_1\) is \(Y\) on the last qubit and \(X\) before it. After that, the generators come in pairs: a \(Y\) and a \(Z\) on one qubit, \(X\) to the left of that qubit, and \(I\) to the right. Adding a qubit on the left puts one \(X\) in front of each old word and adds the new pair on the new leftmost qubit. At seven qubits the list above is that pattern.

## 4. They anticommute, and they fill the matrices

Each word has phase \(+1\), so each \(\Gamma_k\) is Hermitian and \(\Gamma_k^2=I_{128}\).

For the anticommutator, count sites. \(\Gamma_0\) is \(X\) everywhere. Every later word has exactly one letter in \(\{Y,Z\}\). That one site anticommutes with \(X\), and \(X\) against \(X\) commutes. One site is odd.

\(\Gamma_1\) is \(Y\) on qubit 7. Against a later word whose special letter sits further left, that site is \(X\) against \(Y\) or \(Z\), and qubit 7 is \(Y\) against \(I\). One site.

Two later words have special letters on qubits \(q<q'\). Qubits before \(q\) are \(X\) against \(X\). Qubit \(q\) is \(X\) against the special letter. Qubits after \(q\) are \(I\) against the other word. One site.

So every pair anticommutes.

A product of a subset of these generators, taken in increasing index, is a phase times one Pauli word. There are \(2^{14}=16384\) subsets, and \(16384=128^2\) is the dimension of all \(128\times 128\) complex matrices. The empty product is the only one that can be a scalar: if a nonempty product were scalar it would commute with one of its own factors or with a factor left outside, and the sign count forbids that. Every other product is a non-scalar Pauli word and has trace zero. Distinct Pauli words are orthogonal under \(\operatorname{Tr}(A^\dagger B)\). A set of \(128^2\) orthogonal nonzero elements is a basis. The fourteen generators therefore produce every matrix. Nothing is left over inside \(M_{128}(\mathbb{C})\).

## 5. The slow face

The first two qubits carry

\[
\begin{aligned}
M &= YZ, & B_{11} &= XZ, & B_{13} &= ZI,\\
J_1 &= ZX, & J_2 &= -ZY, & J_3 &= -IZ.
\end{aligned}
\]

Compute the product that matters:

\[
M B_{11} = (YX)\otimes(ZZ) = (-iZ)\otimes I = -i\, B_{13},
\]

and therefore

\[
M B_{11} B_{13} = -i\, I_4.
\]

The three face matrices are Hermitian, square to \(I_4\), and anticommute, by the same one-site count on two qubits.

Suppose a \(4\times 4\) matrix \(T\) anticommutes with all three. Then \(T\) commutes with the product \(M B_{11}=-i B_{13}\), hence with \(B_{13}\). It also anticommutes with \(B_{13}\). So \(2TB_{13}=0\). Since \(B_{13}^2=I_4\), one gets \(T=0\). There is no fourth matrix in the \(4\times 4\) algebra that anticommutes with these three.

The matrices that commute with all three are exactly \(I,J_1,J_2,J_3\). A reader can see this by listing the sixteen Pauli words on two qubits. \(B_{13}=Z\otimes I\) commutes with a word only when the first letter is \(I\) or \(Z\). That leaves eight words. Imposing commutation with \(M=Y\otimes Z\) leaves four: \(II\), \(IZ\), \(ZX\), and \(ZY\), which are \(I\), \(-J_3\), \(J_1\), and \(-J_2\). Commutation with \(M\) and \(B_{13}\) gives commutation with \(B_{11}=-iMB_{13}\).

One further multiplication:

\[
J_1 J_2 = (Z\otimes X)(-Z\otimes Y) = -I\otimes(iZ) = i J_3.
\]

The sixteen products of \(\{I,M,B_{11},B_{13}\}\) with \(\{I,J_1,J_2,J_3\}\) are sixteen different Pauli words, hence a basis of all \(4\times 4\) matrices. The face and the flow fill the slow algebra. They do not leave a free entry.

Read the slow letters off the fourteen words. For indices \(0\) through \(9\) the first two letters are \(XX\), and

\[
MJ_2 = (Y\otimes Z)(-Z\otimes Y) = -XX,
\]

so \(XX=-MJ_2\). Indices \(0,3,5,7,9\) are that slow factor tensored with a fast word of phase \(+1\). Indices \(1,2,4,6,8\) put the phase \(i\) on the slow factor and on the fast \(Y\)-word, because \(i\cdot i=-1\) restores \(XX\). Index \(10\) is \(-(MJ_1)\). Index \(11\) is \(B_{11}\). Index \(12\) is \(-(MJ_3)\). Index \(13\) is \(B_{13}\). The last four are the identity on the five fast qubits.

## 6. Volume, conjugation, and the exhaust

Multiply \(\Gamma_0\Gamma_1\cdots\Gamma_{13}\) one qubit at a time.

On each of qubits \(1\) through \(6\) the letters are an even string of \(X\), then \(Y\), then \(Z\). Even powers of \(X\) are \(I\), and \(YZ=iX\). On qubit \(7\) the letters are \(X\) then \(Y\), and \(XY=iZ\). The word is \(XXXXXXZ\). The phase is \(i^7=-i\). So

\[
P=\Gamma_0\cdots\Gamma_{13}=-i\,XXXXXXZ.
\]

A phase \(-i\) is anti-Hermitian. Multiply by \(-i\) to make it Hermitian:

\[
\Omega=-i\,P=-XXXXXXZ.
\]

Then \(\Omega^2=I_{128}\).

The charge conjugation is built the same way, from the right. Start with \(X\) on the last qubit. Alternate left factors \(Y,Z,Y,Z,Y,Z\). The last left factor is \(Z\), so

\[
C=ZYZYZYX.
\]

A phase-\(+1\) word squares to \(I\), so \(C^{-1}=C\).

Transposition changes the sign of a word once for each \(Y\). So \(\Gamma_k^{\mathsf T}=\Gamma_k\) when the special letter is \(Z\) or the word is \(\Gamma_0\), and \(\Gamma_k^{\mathsf T}=-\Gamma_k\) when the special letter is \(Y\). Conjugation by \(C\) multiplies \(\Gamma_k\) by the commutation sign of the pair. The letters of \(C\) are \(Z,Y,Z,Y,Z,Y,X\). Against \(\Gamma_0\), qubits \(1\) through \(6\) anticommute and qubit \(7\) is \(X\) against \(X\): six sites, even, so they commute, and \(\Gamma_0\) has no \(Y\). For a special letter \(L\) on qubit \(q\), every qubit before \(q\) contributes one anticommuting site. The site \(q\) contributes when \(L\) differs from the letter of \(C\). The resulting counts are odd for every \(Y\)-type index and even for every \(Z\)-type index. Therefore

\[
C\Gamma_k C^{-1}=\Gamma_k^{\mathsf T}
\]

for every \(k\), with one sign for the whole list.

Now multiply \(\Omega\) by \(C\), qubit by qubit. The letters of \(\Omega\) are \(X,X,X,X,X,X,Z\) with a leading minus. The letters of \(C\) are \(Z,Y,Z,Y,Z,Y,X\).

| qubit | product | phase | letter |
|------:|---------|------:|:------:|
| 1 | \(XZ\) | \(-i\) | \(Y\) |
| 2 | \(XY\) | \(i\) | \(Z\) |
| 3 | \(XZ\) | \(-i\) | \(Y\) |
| 4 | \(XY\) | \(i\) | \(Z\) |
| 5 | \(XZ\) | \(-i\) | \(Y\) |
| 6 | \(XY\) | \(i\) | \(Z\) |
| 7 | \(ZX\) | \(i\) | \(Y\) |

The local phases multiply to \(i\). The leading minus makes the total phase \(-i\). The letters are \(YZYZYZY\). Define

\[
E=\Omega C=-i\,YZYZYZY.
\]

Seven sites of \(\Omega\) against \(C\) anticommute, so \(\Omega C=-C\Omega\) and

\[
E^2=\Omega C\Omega C=\Omega(-\Omega C)C=-I_{128}.
\]

\(E\) is anti-Hermitian, because its phase is \(-i\), and its trace is zero, because the word is not scalar. The eight elements \(\pm I,\pm\Omega,\pm C,\pm E\) multiply among themselves. \(\Omega\) and \(C\) have order \(2\). \(E\) has order \(4\).

A common eigenvector of \(\Omega\) and \(C\) would be an eigenvector of \(E=\Omega C\) with eigenvalue \(\pm 1\). The only eigenvalues of an operator with \(E^2=-I\) are \(\pm i\). So \(\Omega\) and \(C\) share no eigenvector.

Let \(\mu=\tfrac12(I+\Omega)\). Then \(\mu\) commutes with \(\Omega\). The commutator \([\Omega,C]=\Omega C-C\Omega=2E\), and \([C,\mu]=-E\). The sum of the three cyclic commutators is \(E\). That is the exhaust, obtained by multiplication, not by a search.

## 7. The one hundred twenty-eight lines

Seven Hermitian words square to \(I\) and commute with one another:

\[
\begin{aligned}
M&=YZIIIII, & J_2&=-ZYIIIII,\\
D&=IIIYZII, & B&=IIIZYII,\\
A&=IIIIIZY, & C_{\mathrm{bit}}&=IIIIIYX,\\
\Sigma&=-IIYZYZY.
\end{aligned}
\]

\(C_{\mathrm{bit}}\) is an address bit. It is not the charge conjugation \(C\).

A nonempty product that includes \(\Sigma\) has the letter \(Y\) on qubit \(3\), so it is not scalar. A product that omits \(\Sigma\) factors over the three pairs of qubits \((1,2)\), \((4,5)\), and \((6,7)\). On each pair a nonempty product is a non-scalar Pauli word. The whole product is scalar only for the empty word. Seven independent commuting involutions have \(2^7=128\) joint characters, each of multiplicity one. The lines are a basis of \(\mathbb{C}^{128}\). No line is chosen.

\(M\) and \(\Sigma\) commute and occupy different qubits, so

\[
i\,M\Sigma=i\,(YZ)\otimes(-YZYZY)=-i\,YZYZYZY=E.
\]

On the line with signs \((s_M,S)\),

\[
E=i\,s_M S.
\]

The \(+i\) eigenspace is the set of lines with \(s_M S=+1\). The \(-i\) eigenspace is the complementary set. Each has dimension \(64\).

The pairs of generators reproduce the address bits:

\[
\begin{aligned}
\Gamma_{11}\Gamma_{13}&=-i\,M, &
\Gamma_{10}\Gamma_{12}&=-i\,J_2,\\
\Gamma_1\Gamma_2&=i\,A, &
\Gamma_4\Gamma_6&=i\,B,\\
\Gamma_0\Gamma_3&=-i\,C_{\mathrm{bit}}, &
\Gamma_5\Gamma_7&=-i\,D.
\end{aligned}
\]

Each of these is two words multiplied on the two qubits where those words are not \(X\) against \(X\). And

\[
\Gamma_8=MJ_2AB\Sigma,
\]

which a reader checks by multiplying \(-XXIIIII\) by \(B\), then \(A\), then \(\Sigma\): the two minuses cancel, qubits \(4\) through \(7\) square to \(I\), and qubit \(3\) contributes \(Y\). The result is \(XXYIIII\).

Nested neighbors give one letter on each qubit: \(iX\) on qubits \(1\) through \(6\), because \(YZ=iX\), and \(iZ\) on qubit \(7\), because \(XY=iZ\).

## 8. Two cosets, written by hand

\[
\dim\mathrm{SU}(3)=8,\qquad \dim\mathrm{SO}(3)=3,\qquad \dim\mathrm{SU}(2)=3.
\]

So both

\[
C_1=\mathrm{SU}(3)/\mathrm{SO}(3), \qquad C_2=\mathrm{SU}(3)/\mathrm{SU}(2)
\]

have dimension \(5\). \(C_2\) is the unit sphere in \(\mathbb{C}^3\), because \(\mathrm{SU}(3)\) acts transitively on unit vectors and the stabilizer of the first basis vector is \(\mathrm{SU}(2)\). The sphere has one cell in degree \(0\) and one cell in degree \(5\), so its Euler characteristic is \(1+(-1)^5=0\).

The fibration \(\mathrm{SU}(2)\to\mathrm{SU}(3)\to S^5\) and the fact that \(\pi_k(S^n)=0\) for \(k<n\) give \(\pi_1(\mathrm{SU}(3))=\pi_2(\mathrm{SU}(3))=0\). The quaternion double cover gives \(\pi_1(\mathrm{SO}(3))\cong\mathbb{Z}/2\). The coset sequences then give

\[
H_2(C_1;\mathbb{Z})\cong\mathbb{Z}/2, \qquad H_2(C_2;\mathbb{Z})=0.
\]

The two 5-folds are not homeomorphic. The stored record of \(\Sigma^5\) has dimension, oddness, and Euler characteristic \(0\), and every closed orientable 5-fold has Euler characteristic \(0\). The record does not contain \(H_2\). Both cosets remain candidates. Neither is selected.

On \(C_1\) the normal metric is unique up to scale, and its holonomy is \(\mathrm{SO}(3)\), because the brackets of the five-dimensional complement span \(\mathfrak{so}(3)\) and that action on the tangent space is faithful. On \(C_2\) the invariant metrics are \(\operatorname{diag}(p,q,q,q,q)\). The ratio \(p/q\) is not given a number. The round sphere is the point \(p=q\).

## 9. What a hand reader is not asked to grant

The multiplications above close the module. They do not produce a metric \(g_{\mu\nu}\), a derivative, a GeV, or a color name. The face is the algebra of \(M\), \(B_{11}\), and \(B_{13}\). Calling that algebra the spacetime metric is a refused reading.

A volume ratio, including \(16\pi^3/27\), is a pure number. The conformal quotient of the metrics on \(Y^{14}\) does not break rescaling, so the geometry does not hand the reader an energy or a length.

The clock \(\mathbb{Z}/24\) has a subgroup \(\{0,8,16\}\) of order \(3\), generated by \(+8\), and a unique subgroup of order \(8\), of index \(3\). The quotients are \(\mathbb{Z}/8\) and \(\mathbb{Z}/3\). Those are the locked counts: eight seats and three lines. They are not a mass.

Six ways to order \(\{2-\sqrt{2},\,3,\,2+\sqrt{2}\}\) may be written next to the three generations. The formula on a hop is \(m=(3/16)\,n_\eta\tau\), with \(n_\eta\in\{3,8,15\}\), and the empty hop is \(m=0\). No ordering is selected, and no product is a GeV.

\[
n_{\mathrm{LOCK}}=35, \qquad n_{\mathrm{promoted}}=0, \qquad n_{\mathrm{SOUND}}=15, \qquad \mathrm{continuous\_knobs}=0.
\]
