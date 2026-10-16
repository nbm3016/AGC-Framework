# Mass map

This page lives in `theory\`. Writing it does not lock. The hop-mass formula stays MAP. Leftover extras are \(\tau\) and hop-case.

The nine products below are one CLASS/MAP family. The zero branch \(m = 0\) sits with that family. The family is not one value.

\(\kappa = 9/16\) and \(n_\eta = (3, 8, 15)\) are locked on the isolate. The formula is still written. No value below is a GeV. `continuous_knobs = 0`.

## Formula

\[
m = \frac{\kappa \, n_\eta \, \tau}{3}.
\]

\[
n_\eta \in \{3, 8, 15\}, \qquad \tau \in \{2 - \sqrt{2},\; 3,\; 2 + \sqrt{2}\}.
\]

No hop means massless:

\[
m = 0.
\]

With the locked value \(\kappa = 9/16\),

\[
\frac{\kappa}{3} = \frac{9}{16} \cdot \frac{1}{3} = \frac{3}{16},
\]

so on a hop

\[
m = \frac{3}{16}\, n_\eta \, \tau.
\]

The integer 3 in the denominator is the frozen \(N_{\mathrm{gen}} = 3\). It does not select a pair \((n_\eta, \tau)\).

## Nine-product family

Status of this family: CLASS/MAP. The zero branch is included. Hop-mass stays MAP.

The sets are not zipped. Each locked \(n_\eta\) meets each listed \(\tau\). That meeting is the nine-product family.

| \(n_\eta\) | \(\tau = 2 - \sqrt{2}\) | \(\tau = 3\) | \(\tau = 2 + \sqrt{2}\) |
|---:|---|---:|---|
| 3 | \((9/16)(2 - \sqrt{2})\) | \(27/16\) | \((9/16)(2 + \sqrt{2})\) |
| 8 | \((3/2)(2 - \sqrt{2})\) | \(9/2\) | \((3/2)(2 + \sqrt{2})\) |
| 15 | \((45/16)(2 - \sqrt{2})\) | \(135/16\) | \((45/16)(2 + \sqrt{2})\) |

Zero branch, same family page:

\[
m = 0.
\]

The zero branch is the case with no hop. It sits outside the nine products: none of \(3\), \(8\), \(15\) is zero, and none of the three \(\tau\) values is zero.

## Score

| test | result | reason |
|------|--------|--------|
| Type, dimensionless weight | pass | \(\kappa\), \(n_\eta\), \(\tau\), and \(3\) are dimensionless, so \(m\) is a pure number. |
| Type, native GeV or \(M_R\) | fail | That reading needs a unit. The unit is not applied. |
| Unique from locked atoms | fail | \(n_\eta\) is the locked triple. \(\tau\) remains \(\{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}\). The atom pass in `HOP_MASS_UNIQUENESS.md` finds no listed lock that keeps one element and drops the other two. |
| Extras | \(\tau\), hop case | The uniqueness pass leaves both. \(\tau\) stays the three-element set. The product branch and the zero branch both remain. |
| Nine-product family | CLASS/MAP | Nine products, one family. The zero branch is \(m = 0\). This page does not lock. |
| Hop-mass | MAP | Leftover extras are \(\tau\) and hop-case. Promotion needs type match and uniqueness and extras \(= 0\), together. |

## Uniqueness

`HOP_MASS_UNIQUENESS.md` scores the listed locks one atom at a time. No new real is added. No product is converted to GeV.

| id | question | unique? | extras | live bin |
|----|----------|---------|--------|----------|
| H1 | One \(\tau\) from \(\{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}\) | No | \(\tau \in \{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}\) | MAP |
| H2 | Hop case forced | No | hop case | MAP |
| H3 | Extras empty after H1 and H2 | No | \(\tau\), hop case | MAP |
| H4 | Promote when type matches, the value is unique, and extras \(= 0\) | No | \(\tau\), hop case | MAP |
| H5 | Occupancy names | No | name | MAP |

Hop-mass stays MAP. Leftover extras are \(\tau\) and the hop case. The integer 3 carried by \(N_{\mathrm{gen}}\), by the filter, by the clock index, and by one entry of \(n_\eta\) stays in those roles. The denominator of the formula is that \(N_{\mathrm{gen}}\). \(2-\sqrt{2}\) and \(2+\sqrt{2}\) equal none of the listed values.

Occupancy names stay names. The counts that already have extras 0 are \(\dim \mathrm{Hol} = 8\), \(\dim \mathrm{Iso} = 7 = 3+3+1\), and the clock \(\mathbb{Z}/24 = 3 \times 8\) with face \(+8\).

`continuous_knobs = 0`.

Native GeV and \(M_R\) stay on the open list. Occupancy names are not masses. The counts those names are not allowed to replace are \(\dim \mathrm{Hol} = 8\), \(\dim \mathrm{Iso} = 7 = 3+3+1\), and the clock \(\mathbb{Z}/24 = 3 \times 8\) with face \(+8\).
