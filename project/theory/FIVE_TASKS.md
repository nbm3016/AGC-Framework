# Five tasks

This page does not lock. `continuous_knobs = 0`. Each task was run against the atoms in `isolate_updated.json`. A formula is written when the atoms produce it.

## 1. A 4D equation of motion

The fourteen generators \(\Gamma_0,\ldots,\Gamma_{13}\) and the slow face \(M,B_{11},B_{13}\) are constant matrices. A derivative \(\partial/\partial x^\mu\) does not appear in any of them. The fibration sentence \(Y^{14}\to M^4\) names the base and does not supply coordinates or a metric \(g_{\mu\nu}\).

The isolate row `dynamical_4d_eom` has an empty slot, and it records that emptiness is not an isolate atom. No parameter-free differential equation on \(M^4\) is constructed. The slot stays empty. The row stays sound and is not a lock.

## 2. The on-shell joint boundary count

The count is the number of solutions of \(\star\Psi=\Psi=\Psi^\star\) as an asymptotic on-shell boundary condition on \(Y^{14}\to M^4\).

No file exports that differential operator. The Clifford bracket is not that boundary condition. The wall-index count is not \(\dim\ker D_5\). The identity \(\ker\Omega\cap\ker C=\{0\}\) is a fact about two \(128\times 128\) matrices. It is not the solution space of a field operator.

The solution count is not finite, not counted, and not shown empty. The bin stays UNPERFORMED.

## 3. The wall-index rule

On \(j_2=0\) the Module A rule is

\[
\operatorname{index}(j_1)=\max\bigl(0,\ \lfloor 4j_1-6\rfloor\bigr).
\]

Its three zeros, at \(j_1=1/2,1,3/2\), are a theorem of this rule. `native_aps_index.py` states that the rule is not \(\dim\ker D_5\). The APS probe states that closed \(T^{1,1}\) is not a legal APS carrier, and that the Friedrich bound \(|\lambda|\ge 5/2\) leaves the geometric 5-dimensional Dirac kernel empty.

The floor expression is not derived here as that kernel. Main Theorem F stays a theorem of the rule.

## 4. The name of \(\Sigma^5\)

The stored keys are dimension 5, odd, and Euler characteristic 0. Both

\[
C_1=\mathrm{SU}(3)/\mathrm{SO}(3), \qquad C_2=S^5
\]

match those keys, and

\[
H_2(C_1;\mathbb{Z})\cong\mathbb{Z}/2, \qquad H_2(C_2;\mathbb{Z})=0.
\]

The fibration does not produce \(H_2(\Sigma^5)\), a spin structure, or a \(\mathrm{Spin}^h\) structure. The spin structure on disk belongs to \(T^{1,1}\). \(\Sigma^5\) is not required to be spin. No selector is extracted, and no ratio is set. Each identification stays UNKNOWN. The pair stays CLASS.

## 5. The four inputs, the cubic, and the page interface

**The ratio.** The lock stores

\[
\kappa=\frac{3/4}{4/3}=\frac{9}{16},
\]

with \(3/4=\sigma^{*2}\) and \(4/3=C_2(3)\). That division is the identity already on the lock. It is a pure number, \(8\pi G_{\mathrm{eff}}\), and it is not \(G_N\).

**The clock.** The lock stores the order as \(\mathrm{lcm}(8,3,8)\). Since \(\mathrm{lcm}(8,3)=24\) and \(\mathrm{lcm}(24,8)=24\),

\[
\mathbb{Z}/24
\]

is the group of that order. The unique subgroup of order 8 has index 3. The least positive element of order 3 is \(+8\). No new integer is introduced.

**The hop set.** The three numbers satisfy

\[
(x-3)(x^2-4x+2)=0.
\]

The quadratic formula gives \(x=2\pm\sqrt{2}\), and the linear factor gives \(x=3\). So the set \(\{2-\sqrt{2},\,3,\,2+\sqrt{2}\}\) is the root set of that polynomial. The polynomial is the eliminant of the set. It is not derived here from a topological construction that produces the polynomial before the set. No one root is selected.

**The page.** The interface is

\[
\Pi_{s,t}(Y^{14})=0.
\]

The isolate records it as the cut named by the fibration. It is not a lock of \(g_{\mu\nu}\). Under R11 the observer stick stays withdrawn. Coupling \(\Pi_{s,t}\) to a laboratory unit would insert that stick. The knob count is 0, so the stick is not inserted. The 15 sound rows stay translations. They are not physical predictions and they are not locks.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-12
Claim: These five tasks produce a 4D equation, an on-shell solution count, a Dirac derivation of the floor rule, a unique name for Sigma5, and an observer stick that turns the 15 sound rows into measurements, with continuous_knobs still 0.
Facts: dynamical_4d_eom slot empty. JOINT_BOUNDARY.md exports no operator. native_aps_index.py: the floor rule is not ker D_5. Sigma5 stored keys are dim, odd, chi=0. kappa identity (3/4)/(4/3)=9/16. clock order lcm(8,3,8)=24. tau set is the root set of (x-3)(x^2-4x+2). page_interface is the cut, is_lock false. R11 withdraws the observer stick.
Bin: REFUSED for the equation, the Dirac reading, the coset selection, and the observer stick. UNPERFORMED for the boundary count. CONSISTENT for the kappa division, the clock order, and the cubic as the eliminant of the already given tau set.
Gates: R-metric-swap on a hand-inserted metric. R-knob on the observer stick. The APS carrier gate on closed T^{1,1}.
Reasons: The constant matrices contain no derivative. No boundary operator is exported. The floor rule is not a geometric kernel. The fibration does not choose C1 or C2. The cubic and the clock and kappa are identities of atoms already stored. They do not turn a sound row into a measurement.
Baseline written: NO
Lock changed: NO
```

\[
n_{\mathrm{LOCK}}=35, \qquad n_{\mathrm{promoted}}=0, \qquad n_{\mathrm{SOUND}}=15, \qquad \mathrm{continuous\_knobs}=0.
\]
