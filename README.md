# Absolute Geometric Coherence

AGC is a zero-continuous-knob geometric isolate. Compact ambient factors named in the lock; not a separate theory claim. A self-duality condition, \(\star\Psi = \Psi\), keeps three Casimir values on a domain wall. Those values are \(\tilde\lambda = 6j(j+1)\) for \(j\in\{1/2,1,3/2\}\), namely \(9/2\), \(12\), and \(45/2\). They are not field modes. From that line the isolate fixes a shape, a generation count, and a short list of dimensionless numbers. The verifier checks eight assertions, stages 1A through 4. This is not a Standard Model replacement.

The framework, the theory ledger, and the falsifier are one tree. The checks do not run if those three are split apart.

| Part | Path | What it is |
|---|---|---|
| Framework | [`core/`](core/) | The seven-check verifier and the constitution. |
| Theory | [`project/theory/`](project/theory/) | The ledger and the certificates. A page here is not a lock. |
| Falsifier | [`falsifier/`](falsifier/) | The isolate, the working baseline, and the probes. |

The pages that carry the public reading are in [`docs/README.md`](docs/README.md).

\(\Sigma^5\) and \(T^{1,1}\) are compact factors named in the lock. They are not a separate theory claim. A is the 7-dimensional isometry of that shape. B is the look through the cone: holonomy \(\mathrm{SU}(3)\) is 8-dimensional, and the eight-gluon count is a name of that look, not an A-lock of unique color. \(T_{\mathrm{wall}} = 13/2\) is not a brane tension. \(8\pi G_{\mathrm{eff}} = 9/16\) is not Newton's constant. Unique color is not derived. The four-dimensional metric is not derived. High-scale \(\theta_{13}\) stays \(7.953^\circ\). \(N_{\mathrm{gen}}=3\) is the count of the wall-index zeros \((1/2,0,0)\), \((1,0,0)\), and \((3/2,0,0)\): one doublet, one triplet, and one quartet. They are not three copies of one 4D Weyl spinor. “Three generations” is a name, not an A-lock. That rule is not \(\ker D_5\) and not the APS index theorem.

## Verify

The joint check reads the falsifier and reruns the theory certificates. It does not rewrite either baseline.

```bash
pip install numpy scipy matplotlib
python project/theory/health_check.py
```

Expected: `HEALTH CHECK PASS`, `continuous_knobs = 0`, 35 locks, 15 sound extras.

The framework check is separate. `--full` rewrites `core/complete_baseline.json`. Do not pass `--regenerate`.

```bash
cd core
python AGC_Computational_Framework.py --full
```

Expected from that command: **8/8 PASS**, residual **0.095716**.

The whole repository is MIT. See [`LICENSE`](LICENSE).

Zenodo record of the locked isolate: [10.5281/zenodo.22903967](https://doi.org/10.5281/zenodo.22903967). Concept DOI for the lock family: [10.5281/zenodo.22088036](https://doi.org/10.5281/zenodo.22088036).

Author: Nicholas Myers ([@ZeroKnobs](https://x.com/ZeroKnobs)).
