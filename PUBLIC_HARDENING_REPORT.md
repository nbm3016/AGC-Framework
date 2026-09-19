# Public hardening report

Stranger-clone audit of `nbm3016/AGC-Framework`. Locked numbers not rewritten. No share pack added.

| bug | fix | still broken? |
|-----|-----|----------------|
| `--full` crashed: `No module named 'export_agc_package'` | `export_package` / `export_submission` skip on `ImportError` | no |
| `--full` overwrote public README with trust-demo / zip commands | `write_readme` preserves README that already has the public skeleton voice | no |
| README Verify documented `--full` but CLI crashed | skip missing export; README notes the skip | no |
| `TECHNICAL_BRIEFING.md` linked `EXPANSION_MODE.md`, `EXPANSION_PROTOCOL.md`, `init_expansion_mode.py` (not in tree) | point at `STATUS.md` / `EXPANSION_SYNTHESIS.md`; skip missing session files | no |
| `final_paper_draft.md` told reviewers to `cd AGC_Package` and run `export_submission_package.py` | `--full` only; zip optional | no |
| Generated README advertised `agc_trust_demo.py` and submission zip | stripped from fallback template | no |
| Volume treated as open dynamical defect | STATUS / briefing already conversion-closed; no change to Open table | no |
| CKM / U(2)/S3 / “replaces SM” | public README already denies SM replacement; graph lock is LOCK vs MAP vs struck; CKM stays Open | no |
| Appendix `\includegraphics` figures | png files present in this tree | no |
| Terminal printed “Trust Wrapper finalization” | replaced with skip-zip verify line | no |

`--regenerate` remains an optional extra. It is not the documented stranger path.

Open stays open: \(r\to 0\), anomalies beyond index, landscape uniqueness, \(\theta_{13}\) bridge, HD Wilson, CKM.
