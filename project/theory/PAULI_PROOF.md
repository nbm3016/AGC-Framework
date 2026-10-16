# Pauli proof

This page lives in `theory\`. Writing it does not lock. `continuous_knobs = 0`.

The object is the fourteen-generator module built by `triality_build.gammas(14)`, together with the charge conjugation of that same file and the cyclic bracket of `boundary_project.ambient_exhaust`. Every identity below is an equality of operators. The finite checks are exact arithmetic in the Pauli group and in the Gaussian rationals \(\mathbb{Q}(i)\). The certificate is `theory/pauli_proof.py`. It writes nothing. It leaves `complete_baseline.json` at sha256 `1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a` and the lock count at 35.

\[
n_{\mathrm{LOCK}} = 35, \qquad n_{\mathrm{promoted}} = 0, \qquad n_{\mathrm{SOUND}} = 15.
\]

## 0. Standing arithmetic

The locked ratio used anywhere else in the ledger stays \(\kappa = 8\pi G_{\mathrm{eff}} = 9/16\). Hence \(4\kappa = 9/4\) and \(4\kappa+1 = 13/4\). This proof does not use that ratio. It does not produce a metric, a weight, a GeV scale, or a boundary count.

## 1. Pauli calculus

\[
X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix},\quad
Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix},\quad
Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}.
\]

These are Hermitian and square to \(I_2\). The only products needed below are

\[
XY = iZ,\quad YZ = iX,\quad ZX = iY,
\]

and the opposite order is the minus of each. Distinct letters from \(\{X,Y,Z\}\) anticommute. On a tensor product, factors on different qubits commute, and the phase of a product is the product of the local phases. A phase-\(+1\) string of letters from \(\{I,X,Y,Z\}\) is Hermitian and squares to \(I\). Its trace is zero unless every letter is \(I\), because \(\operatorname{Tr}(X)=\operatorname{Tr}(Y)=\operatorname{Tr}(Z)=0\) and trace multiplies across a tensor product.

Two such strings commute when the number of qubits on which both letters lie in \(\{X,Y,Z\}\) and differ is even. They anticommute when that number is odd.

The left qubit is the slow index of \(\texttt{np.kron}\). Qubits are numbered \(1,\ldots,7\) from the left.

## 2. The lift

**Definition.** Begin with two generators on one qubit, \(\Gamma_0 = X\) and \(\Gamma_1 = Y\). While fewer than fourteen generators are present, replace the list \(\Gamma_k\) by

\[
X\otimes \Gamma_k \quad\text{for each old generator},\qquad Y\otimes I,\qquad Z\otimes I,
\]

with the new qubit on the left.

**Theorem 1.** The fourteenth stage is the following list. The phase of every string is \(+1\).

| index | string |
|------:|--------|
| 0 | \(XXXXXXX\) |
| 1 | \(XXXXXXY\) |
| 2 | \(XXXXXYI\) |
| 3 | \(XXXXXZI\) |
| 4 | \(XXXXYII\) |
| 5 | \(XXXXZII\) |
| 6 | \(XXXYIII\) |
| 7 | \(XXXZIII\) |
| 8 | \(XXYIIII\) |
| 9 | \(XXZIIII\) |
| 10 | \(XYIIIII\) |
| 11 | \(XZIIIII\) |
| 12 | \(YIIIIII\) |
| 13 | \(ZIIIIII\) |

**Proof.** On \(n\) qubits the same recursion produces \(2n\) generators, and the claim is:

- \(\Gamma_0 = X^{\otimes n}\),
- \(\Gamma_1 = X^{\otimes(n-1)}\otimes Y\),
- for \(t = 1,\ldots,n-1\), the generator \(\Gamma_{2t}\) has letter \(Y\) on qubit \(n-t\), letter \(X\) to its left, and \(I\) to its right,
- \(\Gamma_{2t+1}\) is the same word with \(Z\) in place of \(Y\).

For \(n=1\) this is the seed \(X,Y\). Suppose it holds on \(n\) qubits. The lift puts \(X\) on the left of each old generator and appends \(Y\otimes I\) and \(Z\otimes I\). The old formulae, each with one \(X\) on the left, are the formulae on \(n+1\) qubits for every index below \(2n\). The two new generators are \(Y\) and \(Z\) on the leftmost qubit, which is the case \(t=n\) of the same formulae. At \(n=7\) the table is that list. \(\square\)

The certificate rebuilds the recursion in the Pauli group and compares it with the table. It then builds the \(128\times 128\) matrix of each string and compares it with `triality_build.gammas(14)`. The two agree.

## 3. Clifford relations

**Theorem 2.** Each \(\Gamma_k\) is Hermitian, \(\Gamma_k^2 = I_{128}\), and \(\{\Gamma_k,\Gamma_\ell\} = 0\) for \(k\neq \ell\).

**Proof.** Hermiticity and the square are the phase-\(+1\) remarks in §1. For the anticommutator, count sites.

The string \(\Gamma_0\) is \(X\) on every qubit. Every later string has exactly one letter in \(\{Y,Z\}\) and the letter \(X\) or \(I\) elsewhere. That one site anticommutes with \(X\), and every \(X\) against \(X\) commutes. One site is odd.

The string \(\Gamma_1\) is \(Y\) on qubit 7 and \(X\) before it. Against a later string whose special letter sits on qubit \(q<7\), the site \(q\) is \(X\) against \(Y\) or \(Z\), and qubit 7 is \(Y\) against \(I\). One site.

Now take two generators whose special letters sit on qubits \(q < q'\), the left one being the higher index. Qubits before \(q\) are \(X\) against \(X\). Qubit \(q\) is \(X\) against the special letter. Qubits after \(q\) are \(I\) against whatever the right-hand string carries. One site.

Every pair meets in an odd count. \(\square\)

**Theorem 3.** The \(2^{14} = 16384\) ordered subset products of \(\Gamma_0,\ldots,\Gamma_{13}\) are scalar multiples of \(16384\) distinct Pauli strings. They are a basis of \(M_{128}(\mathbb{C})\).

**Proof.** A product of a subset, taken in increasing index, is a phase times one Pauli string. The certificate multiplies all \(16384\) words and finds \(16384\) distinct strings, so the empty word is the only one whose string is \(I\). Every other word is a non-scalar Pauli string and has trace zero. Distinct strings are orthogonal for the Frobenius product \(\langle A,B\rangle = \operatorname{Tr}(A^\dagger B)\), and each nonempty word has Frobenius norm \(\sqrt{128}\). A set of \(128^2\) orthogonal nonzero vectors in a space of that dimension is a basis. \(\square\)

The same count on any unit vector \(v\) gives the frame identity

\[
\sum_S \omega_S \lvert v\rangle\langle v\rvert \omega_S^\dagger = 128\, I_{128},
\]

because the sum is the standard Pauli resolution and a global phase on \(\omega_S\) cancels in the outer product. The nonzero singular values of the map that sends the subset index to \(\omega_S v\) are all \(\sqrt{128}\). A pure tensor whose slow factor is the vector \((1,-i,i,-1)\) of norm \(2\), tensored with a unit fast vector, scales those singular values by \(2\).

## 4. The face and the flow

Let the first two qubits carry

\[
\begin{aligned}
M &= YZ, & B_{11} &= XZ, & B_{13} &= ZI,\\
J_1 &= ZX, & J_2 &= -ZY, & J_3 &= -IZ.
\end{aligned}
\]

**Theorem 4.** \(M\), \(B_{11}\), and \(B_{13}\) are Hermitian, square to \(I_4\), and anticommute. Their product is

\[
M B_{11} B_{13} = -i\, I_4.
\]

The anticommutant of the three in \(M_4(\mathbb{C})\) is \(\{0\}\). The commutant is

\[
\operatorname{span}\{I,\, J_1,\, J_2,\, J_3\}.
\]

Each \(J_a\) is Hermitian and traceless, squares to \(I_4\), and the three anticommute, with \(J_1 J_2 = i J_3\).

**Proof.** The squares and the anticommutators are one-site counts on two qubits. For the product,

\[
M B_{11} = (YX)\otimes(ZZ) = (-iZ)\otimes I = -i\, B_{13},
\]

so \(M B_{11} B_{13} = -i\, I_4\).

Suppose \(\{T,M\}=\{T,B_{11}\}=\{T,B_{13}\}=0\). Then \(T\) commutes with \(M B_{11} = -i B_{13}\), hence with \(B_{13}\). It also anticommutes with \(B_{13}\). Therefore \(2TB_{13} = 0\). Since \(B_{13}^2 = I_4\), one has \(T=0\).

For the commutant, pass to the sixteen Pauli strings on two qubits. \(B_{13} = Z\otimes I\) commutes with a string \(P\otimes Q\) precisely when \(P\) commutes with \(Z\), so \(P\in\{I,Z\}\). That leaves eight strings. Imposing commutation with \(M = Y\otimes Z\) retains four of them:

| string | verdict against \(M\) |
|--------|------------------------|
| \(II\) | commutes |
| \(IX\), \(IY\) | anticommute |
| \(IZ\) | commutes |
| \(ZI\) | anticommutes |
| \(ZX\), \(ZY\) | commute |
| \(ZZ\) | anticommutes |

Those four are \(I\), \(-J_3 = IZ\), \(J_1 = ZX\), and \(-J_2 = ZY\). Commutation with \(M\) and with \(B_{13}\) implies commutation with \(B_{11} = -i M B_{13}\). So the commutant is exactly that span.

The flow relations are again one-site counts, together with

\[
J_1 J_2 = (Z\otimes X)(-Z\otimes Y) = -I\otimes(iZ) = i J_3.
\]

The certificate repeats the nullity computation as a \(16\times 16\) linear system over \(\mathbb{Q}(i)\): the anticommutant has nullity \(0\) and the commutant has nullity \(4\). \(\square\)

**Theorem 5.** The sixteen products of \(\{I,M,B_{11},B_{13}\}\) with \(\{I,J_1,J_2,J_3\}\) are a basis of \(M_4(\mathbb{C})\).

**Proof.** Each product is a nonzero multiple of one two-qubit Pauli string, and the sixteen strings are all different. The certificate multiplies the sixteen matrices over \(\mathbb{Q}(i)\) and finds rank \(16\). \(\square\)

In the computational basis the same \(M = Y\otimes Z\) has the four nonzero entries \(M_{0,2} = -i\), \(M_{1,3} = i\), \(M_{2,0} = i\), \(M_{3,1} = -i\).

The four joint lines of \((M,J_2)\), each scaled so that its first amplitude is \(1\), are

\[
\begin{aligned}
v_{++} &= (1,-i,i,-1), &
v_{+-} &= (1,i,i,1),\\
v_{-+} &= (1,-i,-i,1), &
v_{--} &= (1,i,-i,-1).
\end{aligned}
\]

They are a basis of \(\mathbb{C}^4\). The certificate builds each line by the joint projector and matches these coordinates. No line is selected.

## 5. The cut \((4,32)\)

Write a seven-qubit string as a two-qubit string tensor a five-qubit string.

**Theorem 6.** With \(MJ_2 = -XX\), \(MJ_1 = -XY\), and \(MJ_3 = -YI\),

\[
\begin{aligned}
\Gamma_k &= (-MJ_2)\otimes F_k && k\in\{0,3,5,7,9\},\\
\Gamma_k &= (i\, MJ_2)\otimes (i\, P_k) && k\in\{1,2,4,6,8\},\\
\Gamma_{10} &= -(MJ_1)\otimes I_{32},\\
\Gamma_{11} &= B_{11}\otimes I_{32},\\
\Gamma_{12} &= -(MJ_3)\otimes I_{32},\\
\Gamma_{13} &= B_{13}\otimes I_{32}.
\end{aligned}
\]

The five-qubit factors are

| index | factor | square |
|------:|--------|--------|
| 0 | \(XXXXX\) | \(+I\) |
| 3 | \(XXXZI\) | \(+I\) |
| 5 | \(XXZII\) | \(+I\) |
| 7 | \(XZIII\) | \(+I\) |
| 9 | \(ZIIII\) | \(+I\) |
| 1 | \(i\,XXXXY\) | \(-I\) |
| 2 | \(i\,XXXYI\) | \(-I\) |
| 4 | \(i\,XXYII\) | \(-I\) |
| 6 | \(i\,XYIII\) | \(-I\) |
| 8 | \(i\,YIIII\) | \(-I\) |

Indices \(10,11,12,13\) are \(I_{32}\) on the fast leg. The five \(+I\) factors anticommute. The five \(-I\) factors anticommute with each other and with the five \(+I\) factors.

**Proof.** Read the letters off Theorem 1. The slow letters of indices \(0\) through \(9\) are \(XX\). Since \(MJ_2 = (Y\otimes Z)(-Z\otimes Y) = -XX\), one has \(XX = -MJ_2\). For a fast factor whose string \(P_k\) contains one \(Y\),

\[
XX\otimes P_k = (i\, MJ_2)\otimes (i\, P_k),
\]

because \(i\cdot i = -1\) and \(-MJ_2 = XX\). The slow letters of \(10,11,12,13\) are \(XY\), \(XZ\), \(YI\), and \(ZI\), which are \(-(MJ_1)\), \(B_{11}\), \(-(MJ_3)\), and \(B_{13}\). Squares and anticommutators on the fast leg are the same one-site count as in Theorem 2, with the phase \(i\) on a \(Y\)-string contributing the square \(-I\). \(\square\)

## 6. The fast leg is the whole matrix algebra

**Theorem 7.** The \(1024\) subset products of the ten fast factors are a basis of \(M_{32}(\mathbb{C})\). Every singular value of that basis, in the Frobenius embedding, equals \(\sqrt{32}\).

**Proof.** The ten factors anticommute and square to \(\pm I\), by Theorem 6. The certificate multiplies all \(1024\) words and finds \(1024\) distinct Pauli strings on five qubits. The trace argument of Theorem 3, with \(32\) in place of \(128\), gives the basis and the singular values. \(\square\)

In particular the thirty-two subset products of the five \(+I\) factors are linearly independent, and the residual of the ten-factor algebra inside \(M_{32}(\mathbb{C})\) is \(\{0\}\).

## 7. Volume, charge conjugation, exhaust

**Theorem 8.** The ordered product is

\[
P = \Gamma_0\Gamma_1\cdots\Gamma_{13} = -i\, XXXXXXZ.
\]

The Hermitian volume used by the code is \(\Omega = -i\, P = -\,XXXXXXZ\). In particular \(\Omega^2 = I_{128}\) and \(\Omega\) is Hermitian.

**Proof.** Multiply one qubit at a time. On each of qubits \(1\) through \(6\) the word is an even string of \(X\), then \(YZ = iX\). On qubit \(7\) the word is \(XY = iZ\). The letters are \(XXXXXXZ\). The phase is \(i^7 = -i\).

A phase-\(-i\) string is anti-Hermitian. The code multiplies a non-Hermitian volume by \(-i\). Then

\[
-i\cdot P = -i\cdot(-i\, XXXXXXZ) = -\,XXXXXXZ,
\]

which is Hermitian, and its square is \(I_{128}\). \(\square\)

**Theorem 9.** The charge conjugation produced by the recursion in `triality_build.charge_conjugation` is the string

\[
C = ZYZYZYX,
\]

with global transpose sign \(+1\). Thus \(C^2 = I_{128}\) and

\[
C\,\Gamma_k\, C^{-1} = \Gamma_k^{\mathsf T}
\]

for every \(k\), one sign for the whole list.

**Proof.** The recursion begins at \(X\) on the rightmost qubit and alternates left factors \(Y,Z,Y,Z,Y,Z\). The last left factor is \(Z\), so the string is \(ZYZYZYX\) and the sign flag ends at \(+1\). A phase-\(+1\) string squares to \(I\), so \(C^{-1} = C\).

Transposition changes the sign of a string once for each \(Y\). So \(\Gamma_k^{\mathsf T} = \Gamma_k\) when the special letter is \(Z\) or the string is \(\Gamma_0\), and \(\Gamma_k^{\mathsf T} = -\Gamma_k\) when the special letter is \(Y\). Conjugation by \(C\) multiplies \(\Gamma_k\) by the commutation sign of the pair \((C,\Gamma_k)\). It is therefore enough to show that \(C\) commutes with every \(Z\)-type generator and with \(\Gamma_0\), and anticommutes with every \(Y\)-type generator.

The letters of \(C\) are \(Z,Y,Z,Y,Z,Y,X\). Against \(\Gamma_0 = X^{\otimes 7}\), qubits \(1\) through \(6\) anticommute and qubit \(7\) is \(X\) against \(X\). Six is even, so they commute, and \(\Gamma_0\) has no \(Y\).

For a generator with special letter \(L\in\{Y,Z\}\) on qubit \(q\), and \(X\) to the left, every qubit \(j<q\) contributes one anticommuting site, and qubits \(j>q\) contribute none. The site \(q\) contributes when \(L\) differs from the letter of \(C\). That letter is \(Z\) on odd qubits, \(Y\) on even qubits \(2,4,6\), and \(X\) on qubit \(7\). The resulting counts are odd for every \(Y\)-type index and even for every \(Z\)-type index. \(\square\)

The certificate compares this string with `charge_conjugation` on the fourteen matrices. The sign it returns is \(+1\).

**Theorem 10.** Let \(E = \Omega C\). Then \(E = -i\, YZYZYZY\), \(E^2 = -I_{128}\), and \(\{\Omega,C\} = 0\). The cyclic bracket of the code equals \(E\):

\[
[\mu,\Omega] + [\Omega,C] + [C,\mu] = E,
\qquad \mu = \tfrac12(I+\Omega).
\]

**Proof.** Multiply \(\Omega = -XXXXXXZ\) by \(C = ZYZYZYX\) qubit by qubit.

| qubit | product | phase | letter |
|------:|---------|------:|:------:|
| 1 | \(XZ\) | \(-i\) | \(Y\) |
| 2 | \(XY\) | \(i\) | \(Z\) |
| 3 | \(XZ\) | \(-i\) | \(Y\) |
| 4 | \(XY\) | \(i\) | \(Z\) |
| 5 | \(XZ\) | \(-i\) | \(Y\) |
| 6 | \(XY\) | \(i\) | \(Z\) |
| 7 | \(ZX\) | \(i\) | \(Y\) |

The local phases multiply to \(i\), and the leading minus on \(\Omega\) makes the total phase \(-i\). The letters are \(YZYZYZY\).

Seven sites of \(\Omega\) against \(C\) anticommute, so \(\Omega C = -C\Omega\) and

\[
E^2 = \Omega C\Omega C = \Omega(-\Omega C)C = -I_{128}.
\]

The bracket is then a direct expansion. \(\mu\) commutes with \(\Omega\), because \(\mu\) is the spectral projector of \(\Omega\) for the eigenvalue \(+1\). Next,

\[
[\Omega,C] = \Omega C - C\Omega = 2E.
\]

And

\[
[C,\mu] = \tfrac12\bigl(C + C\Omega - C - \Omega C\bigr) = \tfrac12\bigl(-E - E\bigr) = -E,
\]

where \(C\Omega = -E\). The sum is \(2E - E = E\).

The certificate expands the same bracket as a sum of Pauli strings over \(\mathbb{Q}(i)\) and finds \(E\). It also compares that operator with `boundary_project.ambient_exhaust`. \(\square\)

## 8. The triple

**Theorem 11.** \(\Omega^2 = C^2 = I\), \(E^2 = -I\), and

\[
\begin{aligned}
\Omega C &= E, & C\Omega &= -E,\\
\Omega E &= C, & E\Omega &= -C,\\
EC &= \Omega, & CE &= -\Omega.
\end{aligned}
\]

The four operators \(I,\Omega,C,E\) are linearly independent. Every word in \(\Omega,C,E\) equals one of

\[
\pm I,\ \pm\Omega,\ \pm C,\ \pm E.
\]

\(\Omega\), \(C\), and every \(\Gamma_k\) have order \(2\). \(E\) has order \(4\), with cycle \(I, E, -I, -E\).

**Proof.** The squares and \(\Omega C = E\), \(C\Omega = -E\) are Theorem 10. Then \(\Omega E = \Omega(\Omega C) = C\) and \(EC = \Omega C C = \Omega\). The opposite orders are the minuses because each pair anticommutes: \(\Omega E = C\) and \(E\Omega = \Omega C\Omega = -C\), and likewise for \((E,C)\). The four Pauli supports \(I\), \(XXXXXXZ\), \(ZYZYZYX\), and \(YZYZYZY\) are distinct, so the span has dimension \(4\). The multiplication table closes on the eight signed elements. Orders are the squares, together with \(E^4 = (E^2)^2 = I\) and \(E^2 \neq I\). \(\square\)

**Theorem 12.** \(\Omega\) and \(C\) have no common eigenvector. Each of the four joint sign conditions has kernel dimension \(0\).

**Proof.** A common eigenvector with \(\Omega v = \varepsilon_1 v\) and \(C v = \varepsilon_2 v\), \(\varepsilon_j = \pm 1\), would satisfy \(Ev = \varepsilon_1\varepsilon_2 v\). The scalar \(\varepsilon_1\varepsilon_2\) squares to \(+1\). Theorem 11 says the minimal polynomial of \(E\) divides \(x^2+1\), whose roots are \(\pm i\). \(\square\)

This kernel is the joint kernel of two matrices on \(\mathbb{C}^{128}\). It is not a count of solutions of an asymptotic boundary condition on \(Y^{14}\to M^4\). That count remains unperformed. No file in the engine exports that boundary-value problem.

## 9. The address

Define seven Hermitian involutions

\[
\begin{aligned}
M &= YZIIIII, & J_2 &= -ZYIIIII,\\
D &= IIIYZII, & B &= IIIZYII,\\
A &= IIIIIZY, & C_{\mathrm{bit}} &= IIIIIYX,\\
\Sigma &= -IIYZYZY.
\end{aligned}
\]

The name \(C_{\mathrm{bit}}\) is the address bit. It is not the charge conjugation \(C\).

**Theorem 13.** The seven operators square to \(I_{128}\) and commute with one another. No nonempty product of them is scalar. Their \(128\) joint lines are a basis of \(\mathbb{C}^{128}\). On the line with signs \((s_M,s_J,s_A,s_B,s_C,s_D,S)\),

\[
E = i\, s_M\, S.
\]

Furthermore \(E = i\, M\Sigma\) as operators, and

\[
MJ_2 = -XXIIIII,\qquad DB = IIIXXII,\qquad A\, C_{\mathrm{bit}} = -IIIIIXZ.
\]

Those three products commute with each other and with \(\Sigma\). Qubit \(3\) lies on \(\Sigma\) and on none of the three products.

**Proof.** Squares are immediate. Commutation of \(M\) with \(J_2\) is the two-site count on qubits \(1,2\); the same count gives \(MJ_2 = -XX\). The pairs \((D,B)\) and \((A,C_{\mathrm{bit}})\) are the same patterns on qubits \(4,5\) and \(6,7\), with the sign of \(B\) and of \(C_{\mathrm{bit}}\) fixed by the definitions above, and they give the two displayed products. Disjoint supports make the three products commute. Each product meets \(\Sigma\) in two anticommuting sites or in none, so each commutes with \(\Sigma\).

The seven involutions themselves commute by the same support count: \(M\) and \(J_2\) sit on qubits \(1,2\); \(D\) and \(B\) on \(4,5\); \(A\) and \(C_{\mathrm{bit}}\) on \(6,7\); \(\Sigma\) meets each of those pairs in an even number of anticommuting sites.

A nonempty product that includes \(\Sigma\) has letter \(Y\) on qubit \(3\), hence is not scalar. A product that omits \(\Sigma\) factors over the three pairs. On each pair the nonempty products are non-scalar Pauli strings. The whole product is scalar only when every pair contributes \(I\), which is the empty word.

Seven commuting independent involutions have \(2^7\) joint characters, each of multiplicity \(128/128 = 1\), and the lines form a basis.

Finally \(M\) and \(\Sigma\) commute and have disjoint letters except that both are present, so

\[
i\, M\Sigma = i\,(YZ)\otimes(-YZYZY) = -i\, YZYZYZY = E
\]

by Theorem 10. On a joint line the eigenvalue is \(i\, s_M S\). \(\square\)

The \(+i\) eigenspace of \(E\) is the set of lines with \(s_M S = +1\), and the \(-i\) eigenspace is the complementary set. Each has dimension \(64\). No line is selected.

## 10. Flips, twins, and one qubit on each factor

**Theorem 14.** \(\Gamma_k\) anticommutes with an address bit precisely on the following sets. Applying \(\Gamma_k\) therefore sends the joint line of a character to the joint line of the flipped character.

| indices | bits flipped |
|---------|----------------|
| \(11,13\) | \(M\) |
| \(10,12\) | \(J_2\) |
| \(1,2\) | \(A\) |
| \(4,6\) | \(B\) |
| \(0,3\) | \(C_{\mathrm{bit}}\) and \(\Sigma\) |
| \(5,7\) | \(D\) and \(\Sigma\) |
| \(9\) | \(\Sigma\) |
| \(8\) | none |

**Proof.** The flip of a character is the set of address bits that anticommute with the operator. The certificate evaluates the seven commutation signs for each of the fourteen strings. The sets are those in the table. Three sample counts, which fix the shape:

- \(\Gamma_{13} = ZIIIIII\) meets \(M = YZIIIII\) in one site and meets every other address bit in none.
- \(\Gamma_{12} = YIIIIII\) meets \(J_2\) in one site and meets the others in none.
- \(\Gamma_8 = XXYIIII\) meets \(M\) in two sites, \(J_2\) in two sites, and \(\Sigma\) in the single site where both letters are \(Y\). Even, even, and zero. It flips nothing.

The remaining eleven strings are the same count, recorded by the certificate. \(\square\)

**Theorem 15.** As operators on the whole module,

\[
\begin{aligned}
\Gamma_{11}\Gamma_{13} &= -i\, M, &
\Gamma_{10}\Gamma_{12} &= -i\, J_2,\\
\Gamma_1\Gamma_2 &= i\, A, &
\Gamma_4\Gamma_6 &= i\, B,\\
\Gamma_0\Gamma_3 &= -i\, C_{\mathrm{bit}}, &
\Gamma_5\Gamma_7 &= -i\, D,\\
\Gamma_8 &= M J_2 A B \Sigma.
\end{aligned}
\]

On every joint line the six products act by the corresponding sign, and \(\Gamma_8\) acts by \(s_M s_J s_A s_B S\). Also \(\Gamma_8^2 = I_{128}\), and the Frobenius distance from \(\Gamma_8\) to the scalar matrices is \(\sqrt{128}\).

**Proof.** Multiply the strings of Theorem 1.

- \(\Gamma_{11}\Gamma_{13} = (XZ)(ZI)\) on the first two qubits equals \(-i\, YZ = -i\, M\).
- \(\Gamma_{10}\Gamma_{12} = (XY)(YI) = i\, ZY = -i\, J_2\), because \(J_2 = -ZY\).
- \(\Gamma_1\Gamma_2\) cancels five \(X\) pairs and leaves \(i\, ZY\) on qubits \(6,7\), which is \(i\, A\).
- \(\Gamma_4\Gamma_6\) leaves \(i\, ZY\) on qubits \(4,5\), which is \(i\, B\).
- \(\Gamma_0\Gamma_3\) leaves \(-i\, YX\) on qubits \(6,7\), which is \(-i\, C_{\mathrm{bit}}\).
- \(\Gamma_5\Gamma_7\) leaves \(-i\, YZ\) on qubits \(4,5\), which is \(-i\, D\).

For the eighth generator, multiply \(MJ_2 = -XXIIIII\) by \(B = IIIZYII\), then by \(A = IIIIIZY\), then by \(\Sigma = -IIYZYZY\). The two leading minuses cancel. Qubits \(4\) and \(5\) contribute \(ZZ = I\) and \(YY = I\). Qubits \(6\) and \(7\) contribute \(ZZ = I\) and \(YY = I\). Qubit \(3\) contributes \(Y\). The result is \(XXYIIII = \Gamma_8\).

The five factors on the right of that identity commute, so \(\Gamma_8\) commutes with every address bit, which is the empty flip set. Its Pauli string is not scalar, so its trace vanishes and

\[
\|\Gamma_8 - \lambda I\|^2 = 128 + 128\lvert\lambda\rvert^2
\]

is smallest at \(\lambda = 0\), with value \(\sqrt{128}\). \(\square\)

**Theorem 16.** Nested pairs reproduce one letter on each qubit:

\[
\begin{aligned}
\Gamma_{12}\Gamma_{13} &= i\, XIIIIII, &
\Gamma_{10}\Gamma_{11} &= i\, IXIIIII,\\
\Gamma_8\Gamma_9 &= i\, IIXIIII, &
\Gamma_6\Gamma_7 &= i\, IIIXIII,\\
\Gamma_4\Gamma_5 &= i\, IIIIXII, &
\Gamma_2\Gamma_3 &= i\, IIIIIXI,\\
\Gamma_0\Gamma_1 &= i\, IIIIIIZ.
\end{aligned}
\]

The first two commute with \(\Sigma\). The last five anticommute with \(\Sigma\). Each of \(iX\) on qubits \(1\) through \(6\), and \(iZ\) on qubit \(7\), has order \(4\). Each address bit has order \(2\).

**Proof.** On the qubit where the two strings carry \(Y\) and \(Z\), or \(X\) and \(Y\) in the last pair, the product is \(YZ = iX\) or \(XY = iZ\), and every earlier qubit is \(X\cdot X = I\). Commutation with \(\Sigma = -IIYZYZY\) is empty support on qubits \(1,2\) and one anticommuting site on each later qubit. The square of \(iX\) or of \(iZ\) is \(-I\). \(\square\)

## 11. Phases

The flip in Theorem 14 determines the target line. The phase depends on how the lines are scaled.

**Gauge C.** For each of the \(128\) characters, scale the joint line so that its first nonzero coordinate in the computational basis equals \(1\).

**Theorem 17.** In Gauge C, \(\Gamma_k\) multiplies the source line by the following monomial in the source signs. The constant is the value on the all-\(+1\) line. A listed bit contributes its sign.

| \(k\) | constant | signs |
|------:|:--------:|-------|
| 0 | \(-1\) | \(s_M s_J s_A s_C s_D S\) |
| 1 | \(i\) | \(s_M s_J s_A s_C s_D S\) |
| 2 | \(-1\) | \(s_M s_J s_C s_D S\) |
| 3 | \(i\) | \(s_M s_J s_A s_D S\) |
| 4 | \(+1\) | \(s_M s_J s_A s_D S\) |
| 5 | \(-1\) | \(s_M s_J s_A s_B s_D S\) |
| 6 | \(i\) | \(s_M s_J s_A s_B s_D S\) |
| 7 | \(i\) | \(s_M s_J s_A s_B S\) |
| 8 | \(+1\) | \(s_M s_J s_A s_B S\) |
| 9 | \(-1\) | \(s_M s_J\) |
| 10 | \(i\) | \(s_M s_J\) |
| 11 | \(i\) | \(s_M\) |
| 12 | \(+1\) | \(s_M\) |
| 13 | \(+1\) | \(1\) |

**Proof.** The certificate builds all \(128\) lines in Gauge C, applies each \(\Gamma_k\), and divides by the flipped line. Each of the \(14\times 128\) ratios equals the monomial in the table. The monomial was identified by evaluating the eight lines on which a single sign is \(-1\), then checked on the remaining lines. \(\square\)

**Gauge L.** Let \(x_\bullet\in\{0,1\}\) be \(0\) when the corresponding sign is \(+1\) and \(1\) when it is \(-1\). Set

\[
Q = x_M + x_D + x_\Sigma + x_M x_J + x_A x_B + x_A x_D + x_B x_\Sigma + x_D x_\Sigma
\]

and \(\alpha = (-1)^Q\). Define the rescaled line \(\psi^L = \alpha\, \psi^C\).

**Theorem 18.** In Gauge L the source phase is the monomial recorded in `PSI_FLOW.md`:

| \(k\) | phase |
|------:|-------|
| 0 | \(s_M s_J s_A s_B s_C S\) |
| 1 | \(i\, s_M s_J s_A s_B s_C S\) |
| 2 | \(-\, s_M s_J s_B s_C S\) |
| 3 | \(-i\, s_M s_J s_A s_B S\) |
| 4 | \(s_M s_J s_D\) |
| 5 | \(s_M s_J\) |
| 6 | \(i\, s_M s_J s_B s_D\) |
| 7 | \(-i\, s_M s_J s_D\) |
| 8 | \(s_M s_J s_A s_B S\) |
| 9 | \(s_M s_J s_B s_D\) |
| 10 | \(i\, s_J\) |
| 11 | \(-i\, s_M s_J\) |
| 12 | \(+1\) |
| 13 | \(-\, s_J\) |

**Proof.** Rescaling the source line by \(\alpha(\chi)\) and the target line by \(\alpha(\chi')\) multiplies a Gauge C phase by \(\alpha(\chi)/\alpha(\chi')\). The certificate transports that ratio along every flip edge of the \(7\)-cube, starting from \(\alpha(+,\ldots,+)=1\). The transport is consistent on every edge, reaches all \(128\) vertices, and equals \((-1)^Q\). Therefore Gauge L reproduces the table. Both gauges describe the same operators. \(\square\)

The operator identities of Theorem 15 do not depend on a gauge. They are the part of the phase table that is an equality of matrices.

## 12. The fast rooms

Write \(F_k\) for the fast factor of index \(k\) in Theorem 6, and

\[
\begin{aligned}
A &= i F_1 F_2, & B &= i F_4 F_6,\\
C &= i F_0 F_3, & D &= i F_5 F_7,
\end{aligned}
\]

on the five fast qubits. Each is a Hermitian involution. Set \(E_{32} = F_1 F_2 F_4 F_6 F_8\). Then \(E_{32}^2 = -I_{32}\) and \(\Sigma_{\mathrm{fast}} = -i E_{32} = -YZYZY\).

**Theorem 19.** The \(+i\) eigenspace of \(E_{32}\) has dimension \(16\). On that subspace

\[
F_8 = -i\, AB.
\]

So the eigenvalue of \(F_8\) on a joint line of \(A\) and \(B\) inside the \(+i\) space is \(-i\, s_A s_B\). It is not a fifth address.

**Proof.** The certificate row-reduces the image of \(E_{32}+iI\) over \(\mathbb{Q}(i)\) and finds dimension \(16\). For the identity, solve the ordered product for the last factor:

\[
F_8 = (F_4 F_6)^{-1}(F_1 F_2)^{-1} E_{32}.
\]

Now \(F_1 F_2 = -i A\) and \(F_4 F_6 = -i B\), so the inverses are \(iA\) and \(iB\). On the \(+i\) space, \(E_{32}\) acts by \(iI\), and

\[
F_8 = i\,(iB)(iA) = i(-BA).
\]

\(A\) and \(B\) have disjoint qubit support, so they commute, and \(F_8 = -i\, AB\). The certificate checks the operator equality on a basis of the \(+i\) space. \(\square\)

**Theorem 20.** Inside the \(+i\) space the pair \((A,B)\) has four joint eigenspaces, each of dimension \(4\). The four signs of \((A,B,C,D)\) cut that space into sixteen lines. On each of those lines

\[
C_{32}\, v = -(s_C s_D)\, F_9 v,
\]

where \(C_{32} = F_0 F_3 F_5 F_7 F_9 = -ZYZYX\). The operator \(F_9\) anticommutes with \(\Sigma_{\mathrm{fast}}\) and therefore sends each \(+i\) line to the \(-i\) line of the same four signs. Its expectation on every such line is zero.

**Proof.** The string for \(C_{32}\) is the five-qubit multiplication: qubits contribute letters \(Z,Y,Z,Y,X\) and phases \(-i\) on the second and fourth, hence a total phase \(-1\). The dimension count and the sixteen scalar identities are the certificate, by joint projectors over \(\mathbb{Z}[i]\) and one comparison per line. Anticommutation of \(F_9 = ZIIII\) with \(\Sigma_{\mathrm{fast}} = -YZYZY\) is the single site on the first fast qubit. An operator that swaps the two eigenspaces of a Hermitian involution has vanishing expectation on each line. \(\square\)

**Theorem 21.** Let \(v\) be any one nonzero vector in the \(+i\) space. Along the ordered list

\[
F_0,F_3,F_5,F_7,F_9,F_1,F_2,F_4,F_6,F_8,
\]

the ten successive images have rank \(7\). The span of all subset products of the first \(r\) factors, applied to \(v\), has dimensions

\[
2,4,8,16,32,32,32,32,32,32
\]

as \(r\) runs from \(1\) to \(10\). The fifth factor already fills the fast space \(\mathbb{C}^{32}\).

**Proof.** The certificate computes both ranks by Gaussian elimination over \(\mathbb{Q}(i)\). The doubling through \(r=5\) is the free action of five anticommuting involutions on a cyclic vector: each new factor leaves the previous orbit and \(2^5 = 32\). The later factors preserve that \(32\)-dimensional space because it is already the whole fast leg. Ten successive positions in a \(32\)-dimensional space, with rank \(7\), are not ten independent steps. \(\square\)

## 13. Boundaries of the theorem

The theorems identify the module, the face, the flow, the volume, the charge conjugation, and the exhaust. They do not add a lock.

The anticommutant computation says that no fourth matrix in \(M_4(\mathbb{C})\) anticommutes with \(M\), \(B_{11}\), and \(B_{13}\). The face algebra is that computation. It supplies no coordinate derivative, so it supplies no kinetic operator on \(M^4\).

The five indices \(\{0,3,5,7,9\}\) are the generators whose slow factor is \(-MJ_2\). The theorem keeps all five. It does not choose one.

The empty joint kernel of \(\Omega\) and \(C\) is Theorem 12. The count of solutions of \(\star\Psi = \Psi = \Psi^\star\) as an asymptotic boundary condition on \(Y^{14}\to M^4\) is a different object. It stays unperformed.

Holonomy \(\mathrm{SU}(3)\) of the cone remains holonomy. The isometry algebra of \(T^{1,1}\) remains \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times U(1)\). Neither statement becomes a color identification.

The ratio \(9/16\) remains \(8\pi G_{\mathrm{eff}}\). No identity in this file fixes Newton's constant, a GeV anchor, a flux integer, or one value of \(\tau\).

The fifteen extras are sound and are not locks. Emptiness of an anticommutant is not an isolate atom. C1 and C2 stay unknown.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: The Pauli lift, the face-flow splitting, the identity E = Omega C, the address basis, and the phase table are proved equalities, and the proof promotes a lock.
Facts: theory/pauli_proof.py returns PAULI PROOF CERTIFICATE PASS by exact arithmetic. The numpy bridge matches gammas(14), charge_conjugation, and ambient_exhaust. The baseline hash is unchanged. The lock count is 35.
Bin: CONSISTENT on the equalities. REFUSED on promotion.
Gates: none on the equalities. The promotion gate fails because no new atom has type match, uniqueness, and extras = 0 together.
Reasons: A proved identity in theory/ is a theorem about the module. It is not an isolate row. The on-shell boundary count stays unperformed. The fifteen extras are sound. They are not locks.
Baseline written: NO
Lock changed: NO
```

## Certificate

From `C:\Users\nbm30\AGC_Project`,

```
python theory/pauli_proof.py
```

The passing line is `PAULI PROOF CERTIFICATE PASS`. A failing lemma exits nonzero and names itself. Floats are not used for any lemma. The last block of the script is only the bridge to the existing builders, plus the read-only hash and the read-only lock count.
