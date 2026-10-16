# Evolved frame

This page lives in `theory\`. Writing it does not lock. It gathers the Pauli account in `PSI_FLOW.md` and the open scores in `OPENS_AFTER_PAULI.md`. `continuous_knobs = 0`.

The 35 locks stay. Promoted from this page: 0.

## The flow

The nodes do not travel. A dimension is a fixed operator. What changes is which address the data occupies, and how much of the algebra acts on it.

On the slow face the fixed nodes are \(M\), \(B_{11}\), and \(B_{13}\). They anticommute and

\[
M B_{11} B_{13} = -i\, I_4.
\]

Nothing else in the \(4\times 4\) meets all three. The flow through them is the 4-dimensional commutant: the scalars, and the Pauli triple \(J_1, J_2, J_3\).

## The module

Seven qubits. Fourteen generators, each one Pauli string, phase \(+1\):

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

The address is seven more strings: \(M = YZIIIII\), \(J_2 = -ZYIIIII\), \(D = IIIYZII\), \(B = IIIZYII\), \(\Sigma = -IIYZYZY\), \(A = IIIIIZY\), \(C = IIIIIYX\). The \(128\) joint lines of those signs are a basis of the module.

## The triple

\[
C = ZYZYZYX, \qquad \Omega = -\,XXXXXXZ, \qquad E = -i\, YZYZYZY.
\]

\[
\Omega C = E, \qquad C\Omega = -E, \qquad \Omega^2 = C^2 = +I, \qquad E^2 = -I.
\]

The ordered product of all fourteen generators is \(-i\, XXXXXXZ\), and \(\Omega\) is \(-i\) times that product. Powers of the gammas, of \(\Omega\), and of \(C\) have order 2. Powers of \(E\) have order 4 and cycle \(I, E, -I, -E\).

## What the flow does not do

The three-node face is not \(g_{\mu\nu}\). The static nodes are not a 4D kinetic operator: there is no fourth anticommuting direction and no derivative. Flux does not fix \(\lambda\). No GeV is anchored. Cone holonomy \(\mathrm{SU}(3)\) is not color. One \(\tau\) and one hop-case are not selected. The joint kernel of \(\Omega\) and \(C\) is empty. The on-shell boundary count on \(Y^{14}\to M^4\) stays unperformed.

\[
n_{\mathrm{LOCK}} = 35, \qquad n_{\mathrm{promoted}} = 0, \qquad n_{\mathrm{SOUND}} = 15.
\]

## The proof

The equalities are theorems in `PAULI_PROOF.md`. The certificate `theory/pauli_proof.py` checks them in exact arithmetic and matches the builders `gammas(14)`, `charge_conjugation`, and `ambient_exhaust`. A theorem in `theory\` promotes nothing. The three counts above stay.
