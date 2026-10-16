# Σ^5 spectrum match

Stored numbers only. No spectrum is computed. `continuous_knobs = 0`. The probe does not write `complete_baseline.json`.

| id | claim | unique? | live_bin | extras | why |
|----|-------|---------|----------|--------|-----|
| M1 | What eigenvalue lists are stored, and for which named 5-folds? | Yes | FORCED |  | Stored lists: r0_modes, native_aps chiral modes, and isolate lambda_tilde all hold 9/2, 12, 45/2. The Stage 1A appendix heading names Σ^5 spectral survivors and stores that same set before the T^{1,1} subsection. D5_LABEL_FORMULA stores Killing eigenvalues -5/2 and +5/2 and does not name Σ^5. D5_SPECTRUM is stored with no eigenvalue list. |
| M2 | Is λ̃ = 4.5, 12, 22.5 one of those stored lists? | Yes | FORCED |  | 9/2, 12, and 45/2 equal the stored survivor lists in r0_modes.json, native_aps_index.json, and the isolate lambda_tilde lock. That lock has extras 0. They do not equal the stored Killing pair -5/2, +5/2. |
| M3 | If yes, which named 5-fold carries it, and is that name Σ^5? | Yes | FORCED |  | The Stage 1A appendix stores the set under the heading Σ^5 spectral survivors. native_aps_index.json says the rule is not ker D_5 on Ceresole T^{1,1}. The carrier name on that stored list is Σ^5. |
| M4 | Does the match force a diffeomorphism type with extras = 0? | No | UNKNOWN | diffeomorphism type | The matched list is stored under the name Σ^5. The Sigma5 record keys do not include a diffeomorphism type. No file says the eigenvalue match forces one. |
| M5 | If no list is stored to compare, leave the type unknown. | No | REFUSED |  | A survivor list is stored and matches 9/2, 12, 45/2. The premise that no list is stored is contradicted. The diffeomorphism type stays unknown because the Σ^5 record does not carry one. |

Stored spectrum match? Yes
Baseline byte-stable during probe? Yes

SIGMA5 SPECTRUM MATCH - ZERO KNOBS
