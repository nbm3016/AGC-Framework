# Four tests

This page does not lock. `continuous_knobs = 0`. Each test is the one named in the request. A test that does not produce the asked object stays at the bin it already had.

## 1. The wall-index rule

The file `native_aps_index.py` states the rule on the self-dual line \(j_2=0\),

\[
\operatorname{index}(j_1)=\max\bigl(0,\ \lfloor 4 j_1-6\rfloor\bigr),
\]

and it states that this rule is not \(\dim\ker D_5\) of the Ceresole geometric Dirac operator. The same file records the Friedrich bound \(|\lambda|\ge 5/2\) on a Sasaki–Einstein 5-fold, so that geometric kernel is empty. The APS probe records that closed \(T^{1,1}\) is not a legal APS carrier, that the named product \(1\) is not an \(\hat A\) integral, and that \(\dim\ker D_{\mathrm{APS}}\) is not computed.

The three zeros of the rule, at \(j_1=1/2,1,3/2\), remain a theorem of the rule. They are not the kernel of a boundary Dirac operator on \(T^{1,1}\). The test does not convert the rule into that kernel. Main Theorem F stays conditional on the rule.

## 2. The on-shell joint boundary count

The count asked for is the number of solutions of \(\star\Psi=\Psi=\Psi^\star\) as an asymptotic on-shell boundary condition on \(Y^{14}\to M^4\).

No file exports that boundary operator. `triality_build.py` records its Clifford bracket as not an on-shell boundary condition. `native_aps_index.py` records its count as not \(\dim\ker D_5\). The empty joint kernel of the matrices \(\Omega\) and \(C\) is a different object. It is not substituted.

The solution count is not a number. It is not finite, not counted, and not shown empty. The bin stays UNPERFORMED.

## 3. A rank-9 walk, by exact arithmetic

On the five fast qubits the exhaust is the word

\[
E_{32}=-i\,YZYZY.
\]

Its \(+i\) eigenspace has dimension \(16\). One vector in a kernel basis of \(E_{32}-i I\), walked in the order

\[
F_0,F_3,F_5,F_7,F_9,F_1,F_2,F_4,F_6,F_8,
\]

has ten images of rank \(7\). That is the special seed already recorded.

The following vector is an exact \(+i\) eigenvector, with entries in \(\mathbb{Z}[i]\). The leftmost qubit is the high bit of the index.

\[
\begin{aligned}
v=\;&-i\,\lvert 00100\rangle
+i\,\lvert 00101\rangle
+i\,\lvert 01111\rangle\\
&+\lvert 10000\rangle
+\lvert 10001\rangle
+\lvert 11010\rangle.
\end{aligned}
\]

In coordinates, the nonzero entries are \(v_4=-i\), \(v_5=i\), \(v_{15}=i\), \(v_{16}=1\), \(v_{17}=1\), \(v_{26}=1\).

Gaussian elimination over \(\mathbb{Q}(i)\) on the ten images \(F_0 v\), \(F_0 F_3 v\), and so on through \(F_8\), has rank \(9\). Each image has six nonzero entries. The same elimination on a single kernel-basis seed has rank \(7\), so the rank depends on the seed. This vector shows that rank \(9\) is attained. It does not say that every seed has rank \(9\).

## 4. The name of \(\Sigma^5\)

The fibration \(Y^{14}\to M^4\) with fibre \(\Sigma^5\times T^{1,1}\) stores \(\Sigma^5\) as dimension \(5\), odd, and Euler characteristic \(0\). It does not store \(H_2\), a spin structure, or a diffeomorphism type. The spin structure on disk belongs to \(T^{1,1}\). The wall rule is not a Dirac operator on \(\Sigma^5\).

\(C_1\) and \(C_2\) remain two non-homeomorphic 5-folds that match the stored numbers. No invariant was derived from the fibration that selects one of them, and no ratio was set. Each identification stays UNKNOWN. The pair stays CLASS.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-12
Claim: The wall-index rule is the kernel of a boundary Dirac operator on T^{1,1}; the on-shell joint boundary count is a number; every fast walk has rank 9; and the fibration selects C1 or C2.
Facts: native_aps_index.py labels the floor rule as not ker D_5. JOINT_BOUNDARY.md exports no operator. The vector v above is an exact +i eigenvector whose ten fast images have rank 9 over Q(i), while a kernel-basis seed has rank 7. Sigma5 is stored with dimension, oddness, and Euler characteristic only.
Bin: REFUSED for the Dirac identification of the wall rule. UNPERFORMED for the joint boundary count. CONSISTENT for one rank-9 walk. UNKNOWN for each coset, CLASS for the pair.
Gates: none fired on the rank-9 vector. The APS carrier gate stays closed on T^{1,1}. No knob was added.
Reasons: The rule's three zeros stay a theorem of the rule. The boundary count has no operator. Rank 9 is attained by v and is not the rank of every seed. The fibration does not name Sigma5.
Baseline written: NO
Lock changed: NO
```

\[
n_{\mathrm{LOCK}}=35, \qquad n_{\mathrm{promoted}}=0, \qquad n_{\mathrm{SOUND}}=15, \qquad \mathrm{continuous\_knobs}=0.
\]
