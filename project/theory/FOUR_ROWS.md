# Four rows

This page lives in `theory\`. Writing it does not lock. `continuous_knobs = 0`. `n_LOCK = 35`. `n_promoted = 0`. `n_SOUND = 15`.

The four rows are the photon seat, the Higgs seat, the dynamical equation, and the GeV row. Each row is mapped from an atom already on disk. Each map is sound. None of the four adds an extra. The isolate is not edited. The certificate is `four_rows.py`.

A row is sound when the seat can be read from locked atoms, the relations already proved still hold, and the reading introduces no new real. Selecting a coupling, a vacuum number, one signature, or a GeV numeral would be the extra. That selection is not made.

## Photon

The locked isometry is \(\mathrm{Iso}=\mathrm{SU}(2)\times\mathrm{SU}(2)\times\mathrm{U}(1)\), dimension \(7=3+3+1\), extras \(0\), stored as isometry. The photon seat is the \(\mathrm{U}(1)\) factor. Its dimension is \(1\).

The same factor is the phase in two further locks, each with extras \(0\): one complex line of parallel cone spinors, and the transverse form \(\Omega\) of type \((2,0)\). The Euler cup-square \(2\) is the \(\mathrm{U}(1)\) self-pairing. It stays that pairing.

The electromagnetic coupling is not written. A coupling numeral would be a new real, and a coupling name would be a sixteenth sound extra. Neither is added. The seat stays the locked factor.

## Higgs

The Higgs seat is empty. \(\sigma^*=\sqrt{3}/2\) is the lock `sigma_star`, extras \(0\), read as the shape of \(T^{1,1}\). Its square is \(3/4\). That number is the numerator of \(\kappa=(3/4)/(4/3)=9/16\).

The shape is a 5-fold number. It is not copied into a 4-dimensional vacuum slot. No vacuum number is written. An empty seat is not an isolate atom, and it is not a new extra.

## Equation

The isolate row `dynamical_4d_eom` is MAP. The slot is empty. The extra is `EOM`, already one of the fifteen. Emptiness is not an isolate atom.

`4D_GATES.md` keeps five operators: the unmodified Euclidean operator and the four operators obtained by multiplying one fibre-blind generator by \(i\). Every member is flat. No member is selected. The stored verdict of 2026-10-12 refuses the claim that a locked atom selects one signature, forces a curvature onto \(M^4\), or fills the slot. This page does not replace that verdict. It does not write a second extra beside `EOM`.

## GeV

The isolate row `native_GeV_M_R` is MAP. The extras are `GeV` and `M_R`, already two of the fifteen. The row states that the locked atoms are dimensionless and that no conversion is written.

`TRANSLATION.md` speaks a locked ratio \(\rho\) as \(\rho\cdot u\). The unit \(u\) has no numeral. The hop-mass image is a set of pure numbers, including the branch \(m=0\), and its GeV conversion flag is false. No GeV numeral is written on this page. The two extras stay the two already counted.

## Score

| row | read from | sound | extra added | lock-claim |
|-----|-----------|-------|-------------|------------|
| photon | \(\mathrm{U}(1)\) factor, dimension \(1\) | the factor is the existing lock | no | coupling determined: ABSENT |
| Higgs | empty seat; \(\sigma^*=\sqrt{3}/2\) stays the 5-fold shape | no vacuum number | no | a Higgs number is locked: ABSENT |
| equation | `dynamical_4d_eom`, slot empty | five flat members, none selected | no; `EOM` already counted | the slot is an isolate atom: REFUSED, stored 2026-10-12 |
| GeV | `native_GeV_M_R` | pure numbers, unit \(u\) unnamed | no; `GeV` and \(M_R\) already counted | a native GeV is a lock: REFUSED |

Twelve map rows remain. The spoken sound names remain the fifteen in `health_check.py`. Photon and Higgs are seats read off locks. They are not appended to that list.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-15
Claim: The photon seat, the Higgs seat, the 4D equation, and the GeV row are mapped and sound, and that map adds no extra.
Facts: Iso_group is SU(2)×SU(2)×U(1), dimension 7, extras 0. sigma_star is sqrt(3)/2, extras 0, read as the T^{1,1} shape. dynamical_4d_eom is MAP, slot empty, extra EOM. native_GeV_M_R is MAP, extras GeV and M_R, conversion unwritten. The 2026-10-12 verdict refuses a filled equation slot. continuous_knobs = 0. twelve map rows. fifteen sound names.
Bin: CONSISTENT
Gates: promotion, which needs type match and uniqueness and extras = 0 together. The stored EOM refusal. The ban on reading 9/16 as G_N. The ban on writing 4κ+1 = 9/4.
Reasons: Each seat is read from an atom already stored. The coupling, the vacuum number, the chosen signature, and the GeV numeral are not written, so no sixteenth extra appears. The equation slot stays empty. The fifteen stay sound. They are not locks. The lock count stays 35.
Baseline written: NO
Lock changed: NO
```

\[
n_{\mathrm{LOCK}} = 35, \qquad n_{\mathrm{promoted}} = 0, \qquad n_{\mathrm{SOUND}} = 15, \qquad \mathrm{continuous\_knobs} = 0.
\]
