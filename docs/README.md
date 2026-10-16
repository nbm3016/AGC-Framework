# Absolute Geometric Coherence

AGC is a zero-continuous-knob geometric isolate. Compact ambient factors named in the lock; not a separate theory claim. A self-duality condition, \(\star\Psi = \Psi\), keeps three Casimir values on a domain wall. Those values are \(\tilde\lambda = 6j(j+1)\) for \(j\in\{1/2,1,3/2\}\), namely \(9/2\), \(12\), and \(45/2\). They are not field modes. From that line the isolate fixes a shape, a generation count, and a short list of dimensionless numbers. The verifier checks eight assertions, stages 1A through 4.

\(\Sigma^5\) and \(T^{1,1}\) are compact factors named in the lock. They are not a separate theory claim. The cone on \(T^{1,1}\) is the cone on one factor. Its holonomy is \(\mathrm{SU}(3)\). That statement is about holonomy. It is not a color group, and it is not the spacetime metric \(g_{\mu\nu}\).

The numerical source of truth is [`core/complete_baseline.json`](../core/complete_baseline.json). The short form of the boundaries is [`core/CONSTITUTION.md`](../core/CONSTITUTION.md). The geometry in one page is [`WORKING_GEOMETRY.md`](WORKING_GEOMETRY.md).

## The lock

`continuous_knobs = 0`. Nothing in the table below is a fit.

| Quantity | Value | Reading |
|---|---|---|
| \(N_{\mathrm{gen}}\) | 3 | Count of the wall-index zeros \((1/2,0,0)\), \((1,0,0)\), \((3/2,0,0)\). First \(\mathrm{SU}(2)\) dimensions 2, 3, 4: one doublet, one triplet, one quartet. Not three copies of one 4D Weyl spinor. “Three generations” is a name, not an A-lock. Not \(\ker D_5\). Not the APS index theorem. |
| \(\tilde\lambda\) | \(9/2\), \(12\), \(45/2\) | Casimir values \(6j(j+1)\) on the wall-index line. Not field modes. |
| \(\sigma^*\) | \(\sqrt{3}/2\) | Minimum of the shape potential on \(T^{1,1}\). |
| \(n_\eta\) | 3, 8, 15 | The unique triple tied to those Casimir values. |
| Residual \(r\) | 0.095716 | Higher-resolution residual on the frozen 24-mode slice. The continuum limit \(r \to 0\) is not this number. |
| \(T_{\mathrm{wall}}\) | \(13/2\) | Dimensionless spectral identity. Not a brane tension. |
| \(8\pi G_{\mathrm{eff}}\) | \(9/16\) | A pure number built from \(\sigma^*\) and a Casimir. Not Newton's constant. |

Stage 4 is check 4 of the eight. It compares the phenomenology with the locked targets. It is not part of the Zenodo isolate. Official numbers for strangers are the lock table (\(N_{\mathrm{gen}}=3\), \(\sigma^*=\sqrt{3}/2\), residual \(0.095716\), `continuous_knobs=0`, 8/8 PASS).

Two readings share the locked 5-metric. A is its isometry, \(\mathrm{SU}(2)\times\mathrm{SU}(2)\times\mathrm{U}(1)\), dimension 7: the identity of the shape. B is the look through the cone. Holonomy \(\mathrm{SU}(3)\) is dimension 8. Calling that look the eight-gluon observation is a name, not an A-lock of unique color. The number \(9/16\) uses the Casimir name \(C_2(3)=4/3\). It is not \(G_N\). High-scale \(\theta_{13}\) stays \(7.953^\circ\). \(8.54^\circ\) is an observed poster, not this lock.

## What is open

The skeleton does not choose among all 14-dimensional fibrations. It does not select \(M^{p,q}\). It does not fix a warp slope \(k\) of dimension length\(^{-1}\), because every locked atom is dimensionless and no compact radius is introduced to convert one. It does not fix \(c_2\) of an SU(3) bundle on \(S^2 \times S^2\). Unique color is not derived. The four-dimensional metric is not derived.

\(\star\Psi = \Psi\) keeps the three Casimir values on the wall-index line. It does not delete a topic before it has been tested.

## The eight checks

Do not pass `--regenerate`. That flag rebuilds solver output. The lock is the baseline already in the tree.

```bash
pip install numpy scipy matplotlib
cd core
python AGC_Computational_Framework.py --full
```

| Check | What it asserts |
|---|---|
| 1A | Three wall-index zeros, and the Casimir values \(\tilde\lambda = 6j(j+1) \in \{9/2, 12, 45/2\}\). Not field modes. |
| 1B | \(\sigma^* = \sqrt{3}/2\) is stable. |
| 1C | The \(\Delta\eta\) triple is \((3, 8, 15)\). |
| 2A | \(N_{\mathrm{gen}} = 3\). |
| 2B | The beta matrix is in equilibrium on the Laplacian sector. |
| 3 | The master closure has zero continuous knobs. |
| 3B | The sensitivity grid on record is complete. |
| 4 | Phenomenology matches the locked targets. |

Expected result: **8/8 PASS**, residual **0.095716**, `continuous_knobs = 0`. If the zip exporter is not in the tree, `--full` skips it and still runs the eight checks.

## This repository

`core/` is the lock, the verifier, and the constitution. `docs/` is this prose. Both are MIT.

Author: Nicholas Myers ([@ZeroKnobs](https://x.com/ZeroKnobs)).

Zenodo record of the locked isolate: [10.5281/zenodo.22903967](https://doi.org/10.5281/zenodo.22903967). Concept DOI for the lock family: [10.5281/zenodo.22088036](https://doi.org/10.5281/zenodo.22088036).

## License

MIT. See [`LICENSE`](LICENSE).
