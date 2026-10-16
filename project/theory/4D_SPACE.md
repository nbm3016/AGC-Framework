# The 4D space inside the 14

This page does not lock. `continuous_knobs = 0`. The container is the ordered Clifford module of `HAND_READING.md`: fourteen generators on \(\mathbb{C}^{128}= \mathbb{C}^4\otimes\mathbb{C}^{32}\), base dimension 4, fibre dimension 10.

## The fibre-blind generators

Write each generator as a slow factor on \(\mathbb{C}^4\) tensor a fast factor on \(\mathbb{C}^{32}\). The fast factor is the identity for exactly four indices, and for no others:

\[
\begin{aligned}
\Gamma_{10} &= (X\otimes Y)\otimes I_{32},\\
\Gamma_{11} &= (X\otimes Z)\otimes I_{32},\\
\Gamma_{12} &= (Y\otimes I)\otimes I_{32},\\
\Gamma_{13} &= (Z\otimes I)\otimes I_{32}.
\end{aligned}
\]

These are the generators that do not see the 32-dimensional fibre. Every earlier generator has a non-trivial fast factor, so it moves the fibre. The set \(\{\Gamma_{10},\Gamma_{11},\Gamma_{12},\Gamma_{13}\}\) is the unique fibre-blind subset of the fourteen.

Each squares to \(I_{128}\). Each pair anticommutes, because every pair of the fourteen does. On the slow factor the four matrices \(XY\), \(XZ\), \(YI\), and \(ZI\) therefore also square to \(I_4\) and anticommute. Four anticommuting involutions generate every \(4\times 4\) matrix.

This does not contradict the empty anticommutant of \(\{M,B_{11},B_{13}\}\). That triple is \(YZ\), \(XZ\), and \(ZI\). The fibre-blind four include \(XZ\) and \(ZI\), and they do not include \(YZ\).

## The flat equation

Let \(x^0,x^1,x^2,x^3\) be coordinates on the base, matched in order to \(\Gamma_{10},\Gamma_{11},\Gamma_{12},\Gamma_{13}\). Define

\[
D_4 = \Gamma_{10}\partial_0 + \Gamma_{11}\partial_1 + \Gamma_{12}\partial_2 + \Gamma_{13}\partial_3.
\]

No coupling and no metric are inserted. Square it. Diagonal terms contribute \(\Gamma_k^2\partial^2=\partial^2\). A cross term carries the anticommutator \(\{\Gamma_a,\Gamma_b\}=0\). Therefore

\[
D_4^2 = \partial_0^2 + \partial_1^2 + \partial_2^2 + \partial_3^2.
\]

The Clifford relation read off from these four generators is

\[
\{\Gamma_a,\Gamma_b\} = 2\delta_{ab}\, I.
\]

The 4D geometry carried by this operator is flat Euclidean space \((\mathbb{R}^4,\delta)\). The field equation for a section constant on the fibre is \(D_4\Psi=0\).

## Why it is not Lorentzian, and why that is the remaining equation

Every one of the fourteen generators squares to \(+I\). The relation above has four plus signs. A Lorentzian generator would square to \(-I\). None does.

Replacing one generator by \(i\) times itself would flip one sign, because \((i\Gamma)^2=-I\). That replacement is a choice of which direction is timelike. The squares do not make that choice. The derived 4-space is Euclidean. The Lorentzian equation is the same \(D_4\) after one stated sign flip, and the sign flip is not a lock.

Curvature is absent for the same reason the generators are constant: \(D_4^2\) has no zeroth-order term. A curved metric would change the coefficients of the derivatives. No such coefficient is present.

The isolate slot `dynamical_4d_eom` stays empty. \(D_4\) and the identification of its volume with \(MJ_2\) are derived operators. They are not copied into the isolate.

## The zero-momentum kernel

Let \(k=(k_0,k_1,k_2,k_3)\) and write \(\Gamma(k)=k_0\Gamma_{10}+k_1\Gamma_{11}+k_2\Gamma_{12}+k_3\Gamma_{13}\). The same square as above, with derivatives replaced by the components of \(k\), gives

\[
\Gamma(k)^2 = |k|^2 I_{128}.
\]

A plane wave \(e^{ik\cdot x}v\) lies in the kernel of \(D_4\) exactly when \(\Gamma(k)v=0\). If \(k\neq 0\), then \(\Gamma(k)\) is invertible, with inverse \(\Gamma(k)/|k|^2\), so \(v=0\). If \(k=0\), then \(\Gamma(k)=0\), and every \(v\in\mathbb{C}^{128}\) survives.

The zero-momentum kernel is therefore the whole spinor space. All \(128\) address lines lie in it. No line is removed, and no line is selected.

The three wall zeros are the labels \((j_1,j_2)=(1/2,0)\), \((1,0)\), and \((3/2,0)\). They are harmonics of the wall rule. They are not vectors in \(\mathbb{C}^{128}\), and no locked atom maps them into the address lines. Their representation dimensions are \(2\), \(3\), and \(4\). Those integers do not partition \(128\), and \(2+3+4=9\) is not the dimension of the slow factor. The kernel result does not say that the wall zeros sit inside a proper subspace of the \(128\) lines. It says that every constant 128-component value is annihilated by \(D_4\).

A nonzero momentum has kernel \(\{0\}\). Propagation on this Euclidean 4-space does not occur.

## The 4D volume is the slow address

The ordered product of the four fibre-blind generators is a multiplication on two qubits. On qubit 1 the letters are \(X,X,Y,Z\), and \(XX=I\), \(YZ=iX\). On qubit 2 the letters are \(Y,Z,I,I\), and \(YZ=iX\). The later qubits are \(I\). The phases are \(i\cdot i=-1\), and the word is \(XX\). So

\[
\Gamma_{10}\Gamma_{11}\Gamma_{12}\Gamma_{13} = -XXIIIII.
\]

The same word is the address product already computed: \(MJ_2=-XXIIIII\). Therefore

\[
\Gamma_{10}\Gamma_{11}\Gamma_{12}\Gamma_{13} = MJ_2.
\]

This operator is Hermitian and squares to \(I_{128}\). On the address line with signs \((s_M,s_J)\) it acts by \(s_M s_J\). The other five signs do not appear.

The zero-momentum kernel therefore splits into two eigenspaces of dimension \(64\), one for each sign of \(s_M s_J\). The fibre signs \(s_A,s_B,s_C,s_D,S\) stay free inside each half. The 4D volume element is the slow address. It does not select a line, and it does not select one of the three wall zeros.

## The rotation algebra

The six planes are the Hermitian operators \(H_{ab}=i\Gamma_a\Gamma_b\), with the labels \(0,1,2,3\) standing for \(\Gamma_{10},\Gamma_{11},\Gamma_{12},\Gamma_{13}\). Each \(H_{ab}\) squares to \(I_{128}\) and acts as the identity on the fibre. The words are

\[
\begin{aligned}
H_{01}&=-IXIIIII, & H_{23}&=-XIIIIII,\\
H_{02}&=-ZYIIIII=J_2, & H_{13}&=YZIIIII=M,\\
H_{03}&=YYIIIII, & H_{12}&=-ZZIIIII.
\end{aligned}
\]

Two copies of \(\mathfrak{su}(2)\) sit inside these six planes. Write

\[
\begin{aligned}
A_1&=\tfrac12(H_{01}+H_{23}), &
A_2&=\tfrac12(H_{02}-H_{13}), &
A_3&=\tfrac12(H_{03}+H_{12}),\\
B_1&=\tfrac12(H_{01}-H_{23}), &
B_2&=\tfrac12(H_{02}+H_{13}), &
B_3&=\tfrac12(H_{03}-H_{12}).
\end{aligned}
\]

They satisfy

\[
[A_i,A_j]=-2i\,\varepsilon_{ijk}A_k, \qquad [B_i,B_j]=+2i\,\varepsilon_{ijk}B_k, \qquad [A_i,B_j]=0.
\]

Both copies commute with the 4D volume \(MJ_2\). Every generator is supported on the first two qubits, so every fibre sign \(s_A,s_B,s_C,s_D,S\) is invariant. The rotation algebra of this Euclidean 4-space is \(\mathfrak{su}(2)\oplus\mathfrak{su}(2)\) acting on the slow factor only.

These two copies are not the isometry \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times U(1)\) of \(T^{1,1}\). That isometry acts on the 5-metric. These matrices act on the base spinor.

The curvature remains absent, because the generators are constant and \(D_4^2\) has no zeroth-order term. The isolate slot stays empty.

## The four sign flips

Every generator squares to \(+I\), so the derived operator is Euclidean. A Lorentzian reading is obtained by multiplying exactly one of the four fibre-blind generators by \(i\). There are four such readings, one for each choice of the timelike slot. No reading is selected.

Take the choice that makes \(\Gamma_{10}\) timelike. The symbol at momentum \(k\) is

\[
S(k)=k_0\,(i\Gamma_{10})+k_1\Gamma_{11}+k_2\Gamma_{12}+k_3\Gamma_{13}.
\]

The cross terms cancel, \((i\Gamma_{10})^2=-I\), and \(\Gamma_{11}^2=\Gamma_{12}^2=\Gamma_{13}^2=I\), so

\[
S(k)^2=(-k_0^2+k_1^2+k_2^2+k_3^2)\,I_{128}.
\]

The symbol is singular exactly on the cone \(k_0^2=k_1^2+k_2^2+k_3^2\). For the null momentum \((1,1,0,0)\), exact elimination gives \(\operatorname{rank} S=64\) and \(\ker S\) of dimension \(64\). The other three choices are the same cone with the timelike coordinate permuted.

The Euclidean member and these four Lorentzian members are the complete sign family of this 4-space. The family is sound. No member is a lock. A curved metric is not among them. The signature, the curvature, and the dynamical equation are checked in `4D_GATES.md`. None of the three is forced, and the slot stays empty.

\[
n_{\mathrm{LOCK}}=35, \qquad n_{\mathrm{promoted}}=0, \qquad n_{\mathrm{SOUND}}=15, \qquad \mathrm{continuous\_knobs}=0.
\]
