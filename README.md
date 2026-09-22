# Absolute Geometric Coherence

AGC is a geometric skeleton with no continuous knobs. The ambient object is a 14-dimensional space \(Y^{14}\), fibered down to four-dimensional spacetime \(M^4\). A self-duality condition, \(\star\Psi = \Psi\), keeps three modes on a domain wall. From those modes the skeleton fixes a shape, a generation count, and a short list of dimensionless numbers. One verifier checks that list.

The pages that carry this are in [`docs/README.md`](docs/README.md). The lock, the verifier, and the constitution are in [`core/`](core/).

\(\Sigma^5\) and \(T^{1,1}\) are compact factors. They are not the theory. Cone holonomy \(\mathrm{SU}(3)\) is holonomy of the cone on \(T^{1,1}\). It is not color, and it is not \(g_{\mu\nu}\). \(T_{\mathrm{wall}} = 13/2\) is not a brane tension. \(8\pi G_{\mathrm{eff}} = 9/16\) is not Newton's constant. Unique color is not derived. The four-dimensional metric is not derived.

## Verify

```bash
pip install numpy scipy matplotlib
cd core
python AGC_Computational_Framework.py --full
```

Expected: **8/8 PASS**, residual **0.095716**, `continuous_knobs = 0`.

`core/` and `docs/` are MIT. See [`docs/LICENSE`](docs/LICENSE).

Author: Nicholas Myers ([@ZeroKnobs](https://x.com/ZeroKnobs)).
