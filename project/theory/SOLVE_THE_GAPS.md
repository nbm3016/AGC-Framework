# Solving the six gaps from the locks

This page does not lock. `continuous_knobs = 0`. Each gap is attacked with the atoms already proved. A result is written only when the multiplication or the count produces it.

## 1. The three-factor form of \(E\)

The proved exhaust is the word

\[
E=-i\,YZYZYZY.
\]

Places \(1\) through \(7\) carry the letters \(Y,Z,Y,Z,Y,Z,Y\). Any cut of those places into blocks is a tensor product of the letters in the blocks, with the phase \(-i\) on one block.

The cut used in the hand reading is two blocks:

\[
E=i\,M\otimes\Sigma, \qquad M=YZ, \qquad \Sigma=-YZYZY.
\]

A three-block cut is equally a multiplication. Places \((1,2)\), \((3)\), and \((4,5,6,7)\) give

\[
E=i\,(YZ)\otimes(-Y)\otimes(ZYZY).
\]

Check: \((-Y)\otimes(ZYZY)=-YZYZY=\Sigma\), and \(i\,M\otimes\Sigma=E\). The factors act on spaces of dimension \(4\), \(2\), and \(16\), and \(4\cdot 2\cdot 16=128\).

This is one cut among several. Places \((1)\), \((2)\), and \((3\text{--}7)\) give another,

\[
E=-i\,Y\otimes Z\otimes(YZYZY),
\]

on spaces of dimension \(2\), \(2\), and \(32\). Both products equal \(E\). Neither cut is forced by the fibration sentence \(Y^{14}\to M^4\) with fibre \(\Sigma^5\times T^{1,1}\).

## 2. The four-dimensional object that does exist

The matrices that commute with \(M\), \(B_{11}\), and \(B_{13}\) are

\[
I,\quad J_1=ZX,\quad J_2=-ZY,\quad J_3=-IZ.
\]

That is a \(4\)-dimensional algebra. It is the commutant of the slow face. It is not four coordinates on \(Y^{14}\). The fibration’s fourteen are four of the base plus five plus five. The commutant stays the commutant. The fibre stays \(\Sigma^5\times T^{1,1}\).

The fourteen words \(\Gamma_k\) are constant matrices. They contain no derivative. The face remains the algebra of \(M\), \(B_{11}\), and \(B_{13}\).

## 3. The integer \(3\), solved on the wall rule

On the self-dual line \(j_2=0\) the Module A rule is

\[
\operatorname{index}(j_1)=\max\bigl(0,\ \lfloor 4 j_1-6\rfloor\bigr),
\]

with \(j_1\) a positive half-integer, \(j_1=k/2\) for a positive integer \(k\). The index vanishes when \(4 j_1-6<1\), that is \(j_1<7/4\). Then \(k/2<7/4\), so \(k<3.5\), so \(k\in\{1,2,3\}\).

\[
\begin{aligned}
j_1=\tfrac12 &\colon & 4\cdot\tfrac12-6&=-4, & \lfloor-4\rfloor=-4, & \max(0,-4)&=0,\\
j_1=1 &\colon & 4-6&=-2, & \lfloor-2\rfloor=-2, & \max(0,-2)&=0,\\
j_1=\tfrac32 &\colon & 6-6&=0, & \lfloor 0\rfloor=0, & \max(0,0)&=0,\\
j_1=2 &\colon & 8-6&=2, & \lfloor 2\rfloor=2, & \max(0,2)&=2.
\end{aligned}
\]

Exactly three zeros. The next half-integer is already nonzero. There is no fourth zero of this rule. The dimensions on those three harmonics are \(2\), \(3\), and \(4\).

The outputs that the closure actually returns are pure numbers: \(\kappa=9/16\), \(\mathrm{Vol}(T^{1,1})=16\pi^3/27\), \(\mu_{\gamma\gamma}=1.086571\), \(\Omega_\Lambda=0.679528\), residual \(0.095716\). The conformal quotient does not break rescaling, so none of these is an energy.

The translation \(\rho\cdot u\) still has the unit \(u\) unnamed. No numeral is assigned.

The solve from the atoms is the fibration, the number \(\kappa\), the wall count, and the exhaust \(E=\Omega C\).

\[
n_{\mathrm{LOCK}}=35, \qquad n_{\mathrm{promoted}}=0, \qquad n_{\mathrm{SOUND}}=15, \qquad \mathrm{continuous\_knobs}=0.
\]
