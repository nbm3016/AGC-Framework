# Derivation of \(C_1\) and \(C_2\)

This page lives in `theory\`. Writing it does not lock. `continuous_knobs = 0`.

\(C_1\) is the candidate \(\mathrm{SU}(3)/\mathrm{SO}(3)\). \(C_2\) is the candidate \(S^5 = \mathrm{SU}(3)/\mathrm{SU}(2)\). Both are candidates for the compact factor \(\Sigma^5\). The Casimir name \(C_2(3)=4/3\) stays on the locked ratio \(8\pi G_{\mathrm{eff}}=9/16\). The Chern class \(c_2\) stays on its own open row. This page derives the two cosets.

The stored \(\Sigma^5\) record, read from `yardstick_lovelock_euler.json`, has keys `dim`, `odd`, `euler_characteristic`, and `note`. The values are dimension \(5\), odd, Euler characteristic \(0\), and the note “Odd-dimensional APS wall 5-fold; \(\chi=0\).” No diffeomorphism type, metric, or Betti number is stored. \(b_2=1\) and \(b_3=1\) stay on \(T^{1,1}\). \(\mathrm{Hol}(g_C)=\mathrm{SU}(3)\) stays the holonomy of the cone. The isometry \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times U(1)\), dimension \(7\), stays on \(T^{1,1}\).

The certificate is `theory/c1_c2_derivation.py`. It writes nothing. The total knob count stays \(0\).

## 1. Dimension

\[
\dim \mathrm{SU}(n) = n^2-1, \qquad \dim \mathrm{SO}(n) = n(n-1)/2.
\]

So \(\dim \mathrm{SU}(3)=8\), \(\dim \mathrm{SO}(3)=3\), \(\dim \mathrm{SU}(2)=3\), \(\dim \mathrm{SO}(6)=15\), and \(\dim \mathrm{SO}(5)=10\).

\[
\dim C_1 = 8-3 = 5, \qquad \dim C_2 = 8-3 = 5.
\]

Both match the stored dimension. The match is not a selection: two cosets have the same dimension.

## 2. Homotopy of the two cosets

\(S^n\) for \(n\ge 2\) is simply connected: the two hemispheres are contractible, their intersection is \(S^{n-1}\), and the Seifert–van Kampen theorem gives the trivial amalgam. Cellular homology gives \(H_k(S^n;\mathbb{Z})=0\) for \(0<k<n\) and \(H_n(S^n;\mathbb{Z})=\mathbb{Z}\). Hurewicz, applied to a simply connected space, identifies \(\pi_2\) with \(H_2\). Thus \(\pi_2(S^3)=0\). The identity map generates \(\pi_3(S^3)\cong\mathbb{Z}\).

\(\mathrm{SU}(2)\) is diffeomorphic to \(S^3\) by the unit quaternions, so those groups are the groups of \(\mathrm{SU}(2)\).

A map \(S^k\to S^n\) with \(k<n\) is null-homotopic: a cellular approximation lands in the \((n-1)\)-skeleton, and that skeleton of \(S^n\) is a point. Thus \(\pi_k(S^n)=0\) for \(k<n\).

The inclusion of the upper-left \(2\times 2\) block is a fiber bundle \(\mathrm{SU}(2)\to\mathrm{SU}(3)\to S^5\), with base the first column. Its long exact sequence reads

\[
\pi_2(S^5)=0\to \pi_1(\mathrm{SU}(2))=0\to \pi_1(\mathrm{SU}(3))\to \pi_1(S^5)=0,
\]

so \(\pi_1(\mathrm{SU}(3))=0\), and

\[
\pi_2(\mathrm{SU}(2))=0\to \pi_2(\mathrm{SU}(3))\to \pi_2(S^5)=0,
\]

so \(\pi_2(\mathrm{SU}(3))=0\). One step higher,

\[
\pi_4(S^5)=0\to \pi_3(\mathrm{SU}(2))\to \pi_3(\mathrm{SU}(3))\to \pi_3(S^5)=0.
\]

The outer groups vanish because \(3<5\) and \(4<5\), so \(\pi_3(\mathrm{SU}(3))\cong \mathbb{Z}\).

Conjugation by a unit quaternion on the imaginary quaternions \(\mathbb{R}^3\) is a Lie-group homomorphism \(\mathrm{SU}(2)\to\mathrm{SO}(3)\). Its kernel is \(\{\pm 1\}\). The total space is simply connected, so the base has fundamental group equal to the deck group:

\[
\pi_1(\mathrm{SO}(3))\cong \mathbb{Z}/2.
\]

The coset fibrations \(K\to G\to G/K\) have long exact sequences

\[
\pi_2(G)\to \pi_2(G/K)\to \pi_1(K)\to \pi_1(G)\to \pi_1(G/K)\to \pi_0(K).
\]

For \(C_1\), the groups already computed collapse this to

\[
0\to \pi_2(C_1)\to \mathbb{Z}/2\to 0\to \pi_1(C_1)\to 0.
\]

Hence \(\pi_1(C_1)=0\) and \(\pi_2(C_1)\cong\mathbb{Z}/2\). Hurewicz gives \(H_1(C_1;\mathbb{Z})=0\) and

\[
H_2(C_1;\mathbb{Z})\cong \mathbb{Z}/2.
\]

For \(C_2\), the same sequence with \(K=\mathrm{SU}(2)\) collapses to \(\pi_1(C_2)=0\) and \(\pi_2(C_2)=0\), so

\[
H_2(C_2;\mathbb{Z})=0.
\]

Homology is unchanged by a homeomorphism. The two cosets are not homeomorphic.

## 3. Euler characteristic

\(C_2\) is diffeomorphic to \(S^5\), proved in §5. The sphere has one cell in degree \(0\) and one cell in degree \(5\), so

\[
\chi(C_2)=1+(-1)^5=0.
\]

\(C_1\) is a closed manifold: \(\mathrm{SU}(3)\) is compact and \(\mathrm{SO}(3)\) is a closed subgroup. It is orientable because it is simply connected, so its first Stiefel–Whitney class, which is a homomorphism \(\pi_1\to\mathbb{Z}/2\), vanishes. A closed connected orientable manifold has a fundamental class, and cap product with that class is the Poincaré duality isomorphism \(H^k(C_1;\mathbb{Q})\cong H_{5-k}(C_1;\mathbb{Q})\). Rational Betti numbers therefore satisfy \(b_k=b_{5-k}\).

From §2, \(b_1(C_1)=0\) and \(b_2(C_1)=0\). Duality gives \(b_4=b_1=0\), \(b_3=b_2=0\), and \(b_5=b_0=1\). Hence

\[
\chi(C_1)=1-0+0-0+0-1=0.
\]

The same pairing shows that every closed orientable \(5\)-fold has Euler characteristic \(0\). The stored value \(0\) agrees with both cosets and with every other such \(5\)-fold.

## 4. Holonomy of the normal metric on \(C_1\)

Embed \(\mathfrak{so}(3)\) in \(\mathfrak{su}(3)\) as the real skew-symmetric matrices, and let \(\mathfrak{p}\) be \(i\) times the traceless real symmetric matrices. The bracket relations of a symmetric pair hold: \([\mathfrak{k},\mathfrak{k}]\subset\mathfrak{k}\), \([\mathfrak{k},\mathfrak{p}]\subset\mathfrak{p}\), and \([\mathfrak{p},\mathfrak{p}]\subset\mathfrak{k}\). The certificate evaluates the ten brackets of a basis of the symmetric summand and finds that they span \(\mathfrak{so}(3)\). So \([\mathfrak{p},\mathfrak{p}]=\mathfrak{k}\).

The Maurer–Cartan equation on \(\mathrm{SU}(3)\) splits along this decomposition. The \(\mathfrak{k}\)-component says that the curvature form of the canonical connection on the quotient is

\[
\Omega(X,Y)=-[X,Y]\in\mathfrak{k}, \qquad X,Y\in\mathfrak{p}.
\]

That element acts on \(T_oC_1\cong\mathfrak{p}\) by the adjoint representation. The holonomy algebra is the image of \([\mathfrak{p},\mathfrak{p}]=\mathfrak{so}(3)\).

The certificate builds the three adjoint matrices on the \(5\)-plane. They are linearly independent, they are skew-adjoint for the trace metric \(\operatorname{Tr}(ST)\), and their brackets reproduce the brackets of \(\mathfrak{so}(3)\). The Lie-algebra map \(\mathfrak{so}(3)\to\mathfrak{so}(\mathfrak{p})\) is therefore injective. Its image is the holonomy algebra.

The connected Lie group integrating that image is a quotient of \(\mathrm{SO}(3)\) by a discrete normal subgroup. A discrete kernel of a homomorphism from a connected Lie group is central, and the center of \(\mathrm{SO}(3)\) is trivial. The restricted holonomy group is isomorphic to \(\mathrm{SO}(3)\).

The same three matrices, imposed as infinitesimal isometries of a symmetric bilinear form, leave a \(1\)-dimensional space of solutions. The normal metric has a scale and no shape modulus.

\(\mathrm{Hol}(g_C)=\mathrm{SU}(3)\) is the holonomy of the cone over \(T^{1,1}\). It is a different group, of dimension \(8\), on a different carrier. The isometry algebra of any \(\mathrm{SU}(3)\)-invariant metric on \(C_1\) contains \(\mathfrak{su}(3)\) and therefore has dimension at least \(8\). The locked isometry of \(T^{1,1}\) has dimension \(7\) and stays on \(T^{1,1}\).

## 5. The ratio on \(C_2\), and the round point

A matrix of \(\mathrm{SU}(3)\) sends the first standard basis vector of \(\mathbb{C}^3\) to some unit vector, and every unit vector arises. The stabilizer of \(e_1\) consists of the block matrices \(\operatorname{diag}(1,U)\) with \(U\in\mathrm{SU}(2)\). The orbit map is therefore a diffeomorphism

\[
C_2=\mathrm{SU}(3)/\mathrm{SU}(2)\;\cong\; S^5\subset\mathbb{R}^6.
\]

The tangent space at \(e_1\) is \(\operatorname{Re}(v_1)=0\). In coordinates \((y_1,x_2,y_2,x_3,y_3)\), the isotropy algebra fixes the line of \(\partial_{y_1}\) and acts on the complementary \(\mathbb{R}^4\) by the real form of \(\mathrm{SU}(2)\). The certificate solves \(X^{\mathsf T}Q+QX=0\) on the three generators. Every solution is

\[
Q=\operatorname{diag}(p,\,q,\,q,\,q,\,q).
\]

The solution space is two-dimensional. Overall scale is one ray. The shape invariant is the ratio \(p/q\).

The round metric is the point \(p=q\). It lies in the family: each isotropy generator is skew-symmetric, so the Euclidean identity solves the same equation. At that point the metric is the metric induced on the unit sphere of \(\mathbb{R}^6\).

The Gauss equation of the unit sphere, with outward unit normal equal to the position vector, is

\[
R(e_i,e_j)e_k=\delta_{jk}\,e_i-\delta_{ik}\,e_j.
\]

These ten operators are the standard basis of \(\mathfrak{so}(5)\). The certificate row-reduces them and finds rank \(10\), which is \(\dim\mathrm{SO}(5)\). The sphere is simply connected, so the holonomy group equals its restricted holonomy, and that group is \(\mathrm{SO}(5)\).

\(\mathrm{SO}(6)\) preserves the Euclidean metric and the sphere. Its Lie algebra has dimension \(15\). At \(e_0\in\mathbb{R}^6\) the orbit map \(A\mapsto Ae_0\) on skew matrices has rank \(5\), and the kernel has dimension \(15-5=10\). The certificate checks that rank. The action is infinitesimally transitive, and the isometry algebra of the round metric has dimension \(15\).

No stored atom sets \(p/q\). The round holonomy is the holonomy of that one point. It is not \(\mathrm{Hol}(g_C)\).

## 6. What decides the name

The two cosets are known, and they are not homeomorphic. Section 2 gives

\[
H_2(C_1;\mathbb{Z})\cong\mathbb{Z}/2, \qquad H_2(C_2;\mathbb{Z})=0.
\]

That solves the question of which coset is which. It does not solve which coset is the stored \(\Sigma^5\), because the stored keys are only dimension, oddness, and Euler characteristic \(0\).

\(\Sigma^5\) does not have to be spin. The spin structure stored on disk belongs to \(T^{1,1}\). The wall-index rule is not an Atiyah–Patodi–Singer theorem and is not \(\dim\ker D_5\). A classical Dirac operator would need a spin structure. This ledger does not put that operator on \(\Sigma^5\), so the missing spin sentence is not a selector. \(C_1\) stays in the family with \(C_2\). The pair stays CLASS. Each identification stays UNKNOWN.

## 7. Proof of the bins, and of the knob count

The stored keys are `dim`, `odd`, `euler_characteristic`, and `note`. Both cosets are odd-dimensional of dimension \(5\), and both have Euler characteristic \(0\). Sections 2 and 3 show that they are not homeomorphic, and that the invariant which separates them is \(H_2\) torsion. That torsion is not among the stored keys. A record that matches two non-homeomorphic manifolds does not force either diffeomorphism type.

The promotion gate asks for type match, uniqueness, and extras \(=0\) together. Dimension and Euler characteristic match. Uniqueness fails. The diffeomorphism type is an extra, and on \(C_2\) the ratio \(p/q\) is a second extra. Each identification stays UNKNOWN. The pair is CLASS: both cosets are real, and no member is selected.

The locked integer `continuous_knobs` equals \(0\), with extras \(0\). The derivation produces one real ratio, \(p/q\), and assigns it no value. The metric space of \(C_1\) is one scale, so it contributes no shape modulus. Nothing from this page is written into `isolate_updated.json` or `complete_baseline.json`. The locked count remains

\[
\text{continuous\_knobs}=0.
\]

## 8. The bins

| claim | bin | why |
|-------|-----|-----|
| \(\Sigma^5\) is \(C_1\) | UNKNOWN | dimension \(5\) and \(\chi=0\) match; \(H_2\) torsion and the diffeotype are not stored; \(C_2\) matches the same stored numbers |
| \(\Sigma^5\) is \(C_2\) | UNKNOWN | the same stored numbers match; the round ratio \(p/q\) and the diffeotype are extras |
| the pair \(\{C_1,C_2\}\) | CLASS | both cosets are real \(5\)-folds; no member is selected |
| \(C_1\) normal holonomy equals \(\mathrm{SO}(3)\) | CONSISTENT | \([\mathfrak{p},\mathfrak{p}]=\mathfrak{so}(3)\) and the metric has one scale; this is a fact about the candidate |
| the ratio \(p/q\) is fixed | REFUSED | the invariant-metric space is two scales; no lock sets the ratio; R-knob |

The stored rows in `probe_sigma5.json` already say UNKNOWN for both identifications. This derivation computes the holonomy and the metric modulus that those rows left uncomputed. It does not replace the stored bins. \(C_3=\mathbb{R}\times M^4\) stays the refused noncompact product from that file. No coset is selected.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: Derive C1 and C2, and the derivation selects one of them or adds a knob.
Facts: yardstick_lovelock_euler.json stores Sigma5 as dim 5, odd, Euler characteristic 0, with no diffeotype. isolate_updated.json stores continuous_knobs = 0 with extras 0, among 35 locks. theory/c1_c2_derivation.py checks the bracket span so(3), the faithful skew action on the 5-plane, one invariant scale on C1, two invariant scales on C2, curvature rank 10 on the round sphere, and orbit rank 5 for so(6). The long exact sequences in §2 separate H2.
Bin: UNKNOWN for each identification. CLASS for the pair. REFUSED for fixing p/q.
Gates: R-knob on the claim that p/q is fixed. No gate selects a coset.
Reasons: The stored invariants match both cosets and every other closed orientable 5-fold. The torsion that separates C1 from C2 is not a stored atom. The ratio of C2 is a continuous modulus and is left unset, so the locked knob count stays 0.
Baseline written: NO
Lock changed: NO
```

## 9. Knob count

\[
\text{continuous\_knobs} = 0.
\]

\(C_1\) contributes no shape modulus. \(C_2\) has a ratio, and that ratio is not given a value. The total stays the locked integer \(0\).

## Certificate

From `C:\Users\nbm30\AGC_Project`,

```
python theory/c1_c2_derivation.py
```

The passing line is `C1 C2 DERIVATION CERTIFICATE PASS`.
