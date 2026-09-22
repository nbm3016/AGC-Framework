# Absolute Geometric Coherence

AGC is a geometric skeleton with no continuous knobs. The ambient object is a 14-dimensional space \(Y^{14}\), fibered down to four-dimensional spacetime \(M^4\). A self-duality condition, \(\star\Psi = \Psi\), filters the modes on a domain wall. Three modes survive. From those modes the skeleton fixes a shape, a generation count, and a short list of dimensionless numbers. One verifier checks that list.

\(\Sigma^5\) and \(T^{1,1}\) are compact factors inside the fibration. They are not the theory. The cone on \(T^{1,1}\) is the cone on one factor. Its holonomy is \(\mathrm{SU}(3)\). That statement is about holonomy. It is not a color group, and it is not the spacetime metric \(g_{\mu\nu}\).

The numerical source of truth is [`core/complete_baseline.json`](../core/complete_baseline.json). The short form of the boundaries is [`core/CONSTITUTION.md`](../core/CONSTITUTION.md). The geometry in one page is [`WORKING_GEOMETRY.md`](WORKING_GEOMETRY.md).

## The lock

`continuous_knobs = 0`. Nothing in the table below is a fit.

| Quantity | Value | Reading |
|---|---|---|
| \(N_{\mathrm{gen}}\) | 3 | Wall-index count on the self-dual line. Not the kernel dimension of a five-dimensional Dirac operator. |
| \(\tilde\lambda\) | 4.5, 12, 22.5 | The three surviving modes. |
| \(\sigma^*\) | \(\sqrt{3}/2\) | Minimum of the shape potential on \(T^{1,1}\). |
| \(n_\eta\) | 3, 8, 15 | The unique triple tied to those modes. |
| Residual \(r\) | 0.095716 | Higher-resolution residual on the frozen 24-mode slice. The continuum limit \(r \to 0\) is not this number. |
| \(T_{\mathrm{wall}}\) | \(13/2\) | Dimensionless spectral identity. Not a brane tension. |
| \(8\pi G_{\mathrm{eff}}\) | \(9/16\) | A pure number built from \(\sigma^*\) and a Casimir. Not Newton's constant. |

Stage 4 sits downstream of that lock. It reports \(\mu_{\gamma\gamma}\), \(\Omega_\Lambda\), and \(w_0\). Those are checks, not new parameters.

## What is open

The skeleton does not choose among all 14-dimensional fibrations. It does not select \(M^{p,q}\). It does not fix a warp slope \(k\) of dimension length\(^{-1}\), because every locked atom is dimensionless and no compact radius is introduced to convert one. It does not fix \(c_2\) of an SU(3) bundle on \(S^2 \times S^2\). Unique color is not derived. The four-dimensional metric is not derived.

\(\star\Psi = \Psi\) filters modes. It does not delete a topic before it has been tested.

## The eight checks

Do not pass `--regenerate`. That flag rebuilds solver output. The lock is the baseline already in the tree.

```bash
pip install numpy scipy matplotlib
cd core
python AGC_Computational_Framework.py --full
```

| Check | What it asserts |
|---|---|
| 1A | Three self-dual survivors, and \(\tilde\lambda = \{4.5, 12, 22.5\}\). |
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

Zenodo record of the locked core: [10.5281/zenodo.22088037](https://doi.org/10.5281/zenodo.22088037).

## License

MIT. See [`LICENSE`](LICENSE).
