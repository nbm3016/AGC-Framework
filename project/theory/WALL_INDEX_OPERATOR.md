# Wall index and the operator that is not here

This page lives in `theory\`. Writing it does not lock. `continuous_knobs = 0`. `n_LOCK = 35`. `n_promoted = 0`. `n_OPEN = 15`.

The stated line is \(j_2 = r = 0\) in the isometry labels of the first-slice \(T^{1,1}\). On that line the number carried by each label \(j\) is

\[
\tilde\lambda(j) = 6\, j(j+1).
\]

That is six times the quadratic Casimir of the spin-\(j\) representation of \(\mathrm{SU}(2)\). It is a Casimir value. It is not a field mode. The three sieve zeros are

\[
\begin{align*}
j &= 1/2, & \tilde\lambda &= 9/2, \\
j &= 1, & \tilde\lambda &= 12, \\
j &= 3/2, & \tilde\lambda &= 45/2.
\end{align*}
\]

The sieve \(\max(0,\lfloor 4j-6\rfloor)\) is 0 at those three labels and 2 at \(j=2\). `wall_index_casimir.py` prints that arithmetic. The repository has no numbered Theorem 4.23. The formula above is the statement the language now follows.

No Dirac operator on a named 5-manifold is exhibited whose analytic index equals this count. `core/wall_index_sieve.py` states that this count is the sieve and that a Dirac index is unperformed. The geometric 5-dimensional Dirac kernel stays empty under the stored bound \(|\lambda|\ge 5/2\). The verdict does not change.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-14
Claim: The wall-index count is the analytic index of a Dirac operator on a stated manifold.
Facts: wall_index_casimir.py. core/wall_index_sieve.py. WORKING_PAGE.md on the empty Dirac kernel.
Bin: UNKNOWN
Gates: none fired
Reasons: The Casimir values are computed. The index of an operator was not.
Baseline written: NO
Lock changed: NO
```
