# Absolute Geometric Coherence (AGC)

Parameter-free computational skeleton. An alternative to knob-tuning frameworks, not a Standard Model replacement claim.

Author: Nicholas Myers (`@ZeroKnobs`)

## Ambient

The theory is 14-dimensional: \(Y^{14} \to M^4\). \(\Sigma^5\) and \(T^{1,1}\) are compact factors, not the ambient theory. \(\star\Psi = \Psi\) is a filter. See `WORKING_GEOMETRY.md` and `../core/CONSTITUTION.md`.

## Verify

From `core/`:

```bash
pip install numpy scipy matplotlib
python AGC_Computational_Framework.py --full
```

Do not pass `--regenerate`. Expected: PASS 8/8, residual 0.095716, `continuous_knobs = 0`. If the export package is missing, `--full` skips the zip and still verifies.

## What this public tree is

`core/` holds the lock, the verifier, and the constitution. `docs/` holds this prose. Both are MIT.

Private packages are not in this repository.

## License

MIT. See `LICENSE`.
