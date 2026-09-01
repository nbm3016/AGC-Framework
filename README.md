# Absolute Geometric Coherence (AGC)

Parameter-free computational skeleton on \(\Sigma^5\times T^{1,1}\). This tree is the scientific core only.

## Locked results

| Quantity | Value |
|----------|-------|
| Native APS \(N_{\mathrm{gen}}\) | 3 |
| \(\sigma^*\) | \(\sqrt{3}/2\) |
| Official \(\beta\) residual \(r\) | 0.095716 |
| \(T_{\mathrm{wall}}\) | \(13/2\) |
| Residual-NLO A4 \(\theta_{13}\) | \(7.953^\circ\) |
| `continuous_knobs` | 0 |
| Core verification | 8/8 PASS |

Classification of Proven / Partial / Open: [`STATUS.md`](STATUS.md). Numerical source of truth: [`complete_baseline.json`](complete_baseline.json).

## Reproduce

```bash
pip install numpy scipy matplotlib
python AGC_Computational_Framework.py --full
```

Expected: **PASS 8/8**, official residual **0.095716**, `continuous_knobs = 0`.

## Layout

- `AGC_Computational_Framework.py` — 8-stage verification
- `stage*.py` — stage modules and probes
- JSON baselines and ledgers
- `final_paper_draft.md`, `paper_appendix.tex`

This export is not a full Standard Model fermion spectrum and does not contain a derived \(Y^{14}\to M^4\) Einstein–Hilbert reduction. See `M4_BRIDGE.md` and `REVIEWER_REPRODUCTION.md`.

## License

MIT. See `LICENSE`.
