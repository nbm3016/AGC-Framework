# Ambient gamma solve

This page lives in `theory\`. Writing it does not lock. A formula here is not an isolate atom. `continuous_knobs = 0`.

AMBIENT GAMMA SOLVE - FIVE INDICES - ZERO KNOBS

Solved list: \(\{0, 3, 5, 7, 9\}\)

Unique generator: No

Promotion candidate: No

Rows promoted: 0

## The identity

The ambient exhaust \(E\) returned by `ambient_exhaust()` is the \(128 \times 128\) matrix

\[
E = \Omega C.
\]

\(\Omega = \Gamma_0 \Gamma_1 \cdots \Gamma_{13}\) is the Hermitian Clifford volume of `triality_build.gammas(14)`. \(C\) is the Pauli-lift charge conjugation from the same file. The checked identities are

\[
\Omega^2 = +I_{128}, \qquad C^2 = +I_{128}, \qquad C \Gamma C^{-1} = \Gamma^{\mathsf T}, \qquad \{\Omega, \Gamma_a\} = 0
\]

for every \(a \in \{0,\ldots,13\}\). The norm \(\lVert E - \Omega C \rVert\) is 0. The same matrix equals \(\tfrac12[\Omega, C]\).

Because \(\Omega\) anticommutes with every generator,

\[
\{E, \Gamma_a\} = 0 \iff [C, \Gamma_a] = 0 \iff \Gamma_a^{\mathsf T} = \Gamma_a,
\]

\[
[E, \Gamma_a] = 0 \iff \{C, \Gamma_a\} = 0 \iff \Gamma_a^{\mathsf T} = -\Gamma_a.
\]

The real-symmetric generators are

\[
\{0, 3, 5, 7, 9, 11, 13\}.
\]

The imaginary-antisymmetric generators are

\[
\{1, 2, 4, 6, 8, 10, 12\}.
\]

These are the sets \(A_{\mathrm{anticommute}}\) and \(A_{\mathrm{commute}}\). Every nonzero bracket with \(E\) has Frobenius norm \(2\sqrt{128}\). Every zero bracket has Frobenius norm 0.

## The five indices

Distinct generators anticommute. \(\Gamma_{11}\) and \(\Gamma_{13}\) are real symmetric, so both lie in \(A_{\mathrm{anticommute}}\). Each squares to \(+I_{128}\), so neither anticommutes with itself. Removing them from the symmetric set leaves

\[
\{0, 3, 5, 7, 9\}.
\]

Each of these five squares to \(+I_{128}\) and anticommutes with both \(\Gamma_{11}\) and \(\Gamma_{13}\). That list is the whole solution of the test. The gate needs one value. Five values fail uniqueness, so the list is not a promotion candidate.

On the \((4, 32, 4, 32)\) decomposition, indices \(0, 3, 5, 7\) move the 32-leg off the diagonal. Index \(9\) preserves each fiber label. Its \(4 \times 4\) block is the exchange matrix on fiber slots \(0\)–\(15\) and the negative of that matrix on slots \(16\)–\(31\). Index \(9\) is not a scalar on the fiber.

## The slow \(4 \times 4\)

\(M\), \(B_{11}\), and \(B_{13}\) are the slow factors rebuilt on the same index. Each squares to \(+I_4\), and the three pairwise anticommutators are 0. The complex linear map

\[
S \mapsto \bigl(\{S, M\},\, \{S, B_{11}\},\, \{S, B_{13}\}\bigr)
\]

on \(M_4(\mathbb{C})\) has smallest singular value 2. Its kernel is \(\{0\}\). No matrix in \(M_4(\mathbb{C})\) anticommutes with all three, so the further demand \(S^2 = -I_4\) has no candidate. The five ambient generators do not supply that matrix.

## What stays

\(M^4\), \(\Sigma^5\), and the cone add to 15. The fiber is \(\Sigma^5 \times T^{1,1}\). C1 and C2 stay UNKNOWN. No coset is selected. The 35 locks stay. `complete_baseline.json` is not rewritten by this page.

Baseline sha256 at the time of the check: `1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a`.
