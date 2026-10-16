# Hop-mass uniqueness

The formula stays the one already written in `MASS_MAP.md`:

\[
m = \frac{\kappa \, n_\eta \, \tau}{3} = \frac{3}{16}\, n_\eta \, \tau,
\]

with \(n_\eta \in \{3, 8, 15\}\) and \(\tau \in \{2 - \sqrt{2},\, 3,\, 2 + \sqrt{2}\}\). The zero branch is \(m = 0\). No new real is introduced. No value is converted to GeV. `continuous_knobs = 0`.

A lock needs three gates together: the type matches, the value is unique from the locked atoms below, and extras \(= 0\).

## Atoms used

Only these locks are scored:

| atom | locked value |
|------|----------------|
| Ambient | \(Y^{14} \to M^4\), dimension 14 |
| Fibre | \(\Sigma^5 \times T^{1,1}\) |
| Filter | \(\star\Psi = \Psi = \Psi^\star\) |
| Barrier | \(\star\Psi = -\Psi\) |
| Clock | \(\mathbb{Z}/24\), \(3 \times 8\), face \(+8\) |
| \(\kappa\) | \(9/16\), with \(4\kappa = 9/4\) and \(4\kappa + 1 = 13/4\) |
| \(N_{\mathrm{gen}}\) | \(3\), wall zeros of dimensions \(2 \oplus 3 \oplus 4\) |
| \(n_\eta\) | \((3, 8, 15)\) |
| \(\sigma^*\) | \(\sqrt{3}/2\), so \(\sigma^{*2} = 3/4\) |
| \(T_{\mathrm{wall}}\) | \(13/2\) |
| Isometry | dimension \(7 = 3 + 3 + 1\), stored as isometry |
| Holonomy | \(\mathrm{Hol}(g_C) = \mathrm{SU}(3)\), dimension 8, stored as holonomy |

## Equality check

A rational \(p/q\) equals \(2 - \sqrt{2}\) only when \(2q^2 = (2q - p)^2\). It equals \(2 + \sqrt{2}\) only when \(2q^2 = (p - 2q)^2\). Both tests fail for every rational carried by the atoms above: \(14\), \(5\), \(9/16\), \(3/16\), \(9/4\), \(13/4\), \(3\), \(8\), \(15\), \(3/4\), \(13/2\), \(7\), \(24\), and \(8\).

\(\sigma^* = \sqrt{3}/2\) squares to \(3/4\). The squares \((2 - \sqrt{2})^2 = 6 - 4\sqrt{2}\) and \((2 + \sqrt{2})^2 = 6 + 4\sqrt{2}\) equal \(3/4\) only if \(512 = 441\). They do not.

The integer \(3\) is the middle element of the \(\tau\) set. It is also the wall-zero count, the number of parts in the filter, the clock index, the first entry of \(n_\eta\), and the dimension of each \(\mathrm{SU}(2)\) factor. Each of those atoms already locks that integer in that role. The hop-mass formula places the wall-zero count in the denominator. The atom \(n_\eta\) is the whole triple \((3, 8, 15)\). The stored number on the holonomy atom is the dimension \(8\). The stored number on the isometry atom is the dimension \(7\).

## Atom ledger

| atom | member of the \(\tau\) set | forces one \(\tau\) | forces the hop case |
|------|----------------------------|---------------------|---------------------|
| \(Y^{14} \to M^4\) | dimension 14 lies outside the set | no | no |
| \(\Sigma^5 \times T^{1,1}\) | both factors have dimension 5 | no | no |
| \(\star\Psi = \Psi = \Psi^\star\) | the equality has three parts | no | no |
| \(\star\Psi = -\Psi\) | the barrier is the minus eigenspace | no | no |
| Clock \(\mathbb{Z}/24\), \(3 \times 8\), face \(+8\) | the line count is 3; order, seats, and face lie outside the set | no | no |
| \(\kappa = 9/16\), \(4\kappa = 9/4\) | \(9/16\), \(3/16\), \(9/4\), and \(13/4\) lie outside the set | no | no |
| \(N_{\mathrm{gen}} = 3\) | the count is 3; the harmonic dimensions are 2, 3, and 4 | no | no |
| \(n_\eta = (3, 8, 15)\) | one entry is 3; the atom is the triple | no | no |
| \(\sigma^* = \sqrt{3}/2\) | \(\sqrt{3}/2\) and \(3/4\) lie outside the set | no | no |
| \(T_{\mathrm{wall}} = 13/2\) | \(13/2\) lies outside the set | no | no |
| Iso dimension 7 | \(7 = 3 + 3 + 1\) lies outside the set as a group dimension | no | no |
| \(\mathrm{Hol}(g_C) = \mathrm{SU}(3)\) as holonomy | the stored number is 8 | no | no |

The fibre names \(T^{1,1}\). The filter keeps the three wall zeros. The barrier keeps the minus eigenspace. None of those statements selects the product branch or the zero branch. Every entry of \(n_\eta\) is nonzero, so each of the nine products is nonzero, and the written zero branch stays a separate case.

## Score

| id | question | unique? | extras | live_bin | why |
|----|----------|---------|--------|----------|-----|
| H1 | Does any locked atom force one unique \(\tau\) from \(\{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}\)? | No | \(\tau \in \{2-\sqrt{2},\, 3,\, 2+\sqrt{2}\}\) | MAP | The set remains three elements. Atoms that carry the integer 3 already lock that integer in their own roles. \(2-\sqrt{2}\) and \(2+\sqrt{2}\) equal none of the listed values. |
| H2 | Does any locked atom force the hop case (must hop versus may not hop)? | No | hop case | MAP | The product branch and the zero branch both remain. No listed atom selects one of them. |
| H3 | After H1 and H2, are the extras for hop-mass empty? | No | \(\tau\), hop case | MAP | H1 leaves the three-element set \(\tau\). H2 leaves the hop case. |
| H4 | Promote hop-mass to LOCK only if the type matches, the value is unique, and extras \(= 0\). | No | \(\tau\), hop case | MAP | The dimensionless type matches. The GeV type does not, and no conversion is written. Uniqueness fails. Extras stay \(\tau\) and the hop case. Status stays MAP. |
| H5 | Occupancy names stay names unless a unique count is forced with extras \(= 0\). | No | name | MAP | \(\dim \mathrm{Hol} = 8\), \(\dim \mathrm{Iso} = 7 = 3+3+1\), and the clock \(\mathbb{Z}/24 = 3 \times 8\) with face \(+8\) stay those locks, extras 0. This pass forces no new count. Names stay names. |

Hop-mass promoted to LOCK? No

Leftover extras: \(\tau\), hop case

HOP-MASS UNIQUENESS - EXTRAS OR LOCK - ZERO KNOBS
