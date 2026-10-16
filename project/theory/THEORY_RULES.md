# Theory rules

Writing in this folder does not lock. Write ≠ lock. `continuous_knobs = 0`.

## Lanes

| lane | path | may lock? |
|------|------|-----------|
| isolate | `falsifier\isolate_updated.json` and the working baseline beside it | only by rule |
| theory | `project\theory\` | no |

The checkers read `falsifier\isolate_updated.json` and `falsifier\complete_baseline.json`. The prose note is `project\ISOLATE_UPDATE.md`. The published baseline stays in `core\`.

`project\theory\` holds working pages, maps, and CLASS families. The pages in this folder are `HANDOFF_TODAY.md`, `MASS_MAP.md`, `UPDATED_ISOLATE.md`, `VERIFY_TOE.md`, `PAGE_DERIVATION.md`, `HOP_MASS_UNIQUENESS.md`, `AMBIENT_GAMMA_SOLVE.md`, `JOINT_BOUNDARY.md`, `MASTER_FRAMEWORK_UPDATE.md`, `PSI_FLOW.md`, `OPENS_AFTER_PAULI.md`, `FRAME_EVOLVED.md`, `PAULI_PROOF.md`, `C1_C2_DERIVATION.md`, `QUOTIENT_SYMMETRY.md`, `TRANSLATION.md`, `COMPLETION_PROOF.md`, `STATE_MATRIX.md`, `HAND_READING.md`, `MANUSCRIPT_HAND.md`, `SOLVE_THE_GAPS.md`, `FOUR_TESTS.md`, `FIVE_TASKS.md`, `WORKING_PAGE.md`, `4D_SPACE.md`, `4D_GATES.md`, `QEC_MAP.md`, `WALL_INDEX_OPERATOR.md`, `FOUR_ROWS.md`, and this file. The certificate for `PAULI_PROOF.md` is `pauli_proof.py`. The certificate for `C1_C2_DERIVATION.md` is `c1_c2_derivation.py`. The certificate for `COMPLETION_PROOF.md` is `completion_proof.py`. The certificate for `4D_GATES.md` is `d4_gates.py`. The certificate for `FOUR_ROWS.md` is `four_rows.py`. `health_check.py` reruns those five and the lock inventory. Running any of them writes nothing, except `health_check.py --write-matrix`, which rewrites only `STATE_MATRIX.md`.

A formula in `theory\` is not an isolate atom.

A refused promotion does not forbid the formula. The formula is written. Its bin is MAP or CLASS. The refusal applies to the claim that the formula locks an extra. `QUOTIENT_SYMMETRY.md` is the worked case: \(Q(G)=Y^{14}/G\) is written, \(G\) stays an extra, and the claim that this quotient locks the 15 stays refused.

A translation is a spoken word set beside an engine token. The word is not a second value. `TRANSLATION.md` writes one translation for each of the 15 sound extras. One unnamed unit \(u\) is the only dimensionful place, and it carries no numeral. The swapped \(9/4\) label and the reading "\(9/16\) is \(G_N\)" stay banned inside that column.

Promotion into the isolate requires type match and uniqueness and extras \(= 0\), together.

## Sound without a single winner

Uniqueness is the gate for copying one value into the isolate. It is not the test of whether a structure works.

A family is functional when every member can be computed from locked atoms and the operations stay inside the family. It is structurally sound when the proved relations hold for every member and a fired refuse-gate stays fired. It is leak-proof when `continuous_knobs = 0`, listing the members introduces no new real, and a banned reading is not written as an equation.

These families are already in that state. No member is selected.

| family | members | what is sealed |
|--------|---------|----------------|
| conformal class | \(C_{\mathrm{phys}}=\mathrm{Riem}(Y^{14})/\mathrm{Conf}(Y^{14})\) | no absolute scale is generated |
| address lines | \(128\) joint lines of the seven signs | they form a basis; the exterior residual is \(\{0\}\) |
| slow indices | \(\{0,3,5,7,9\}\) | each slow factor is \(-MJ_2\) |
| hop-mass | nine products, and the branch \(m=0\) | \(m=(3/16)\,n_\eta\tau\) on a hop |
| \(\tau\) labelings | six orderings of \(\{2-\sqrt{2},\,3,\,2+\sqrt{2}\}\) | the set itself |
| \(\Sigma^5\) cosets | \(C_1\) and \(C_2\) | both have dimension \(5\) and Euler characteristic \(0\) |

Picking one member out of any of these rows would be the extra. The family is the sound object. The 15 translations in `TRANSLATION.md` are functional as speech in this same sense. Speech does not copy a row into the isolate.

Zero residual of the Clifford module is the diagnostic that the family is balanced. The phrases "operationally closed" and "dynamic lock" are not bins. They do not move a sound extra onto the isolate. `COMPLETION_PROOF.md` §6 records that refusal. The 15 are sound. They are not locks. Sound means the family is functional, the relations hold for every member, and no new real is introduced. The isolate still stores those rows as MAP, which means they are not among the 35 locks.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-08
Claim: A solution must be unique in order to be functional, structurally sound, and leak-proof.
Facts: The six families in the table above. continuous_knobs = 0. Promotion still needs type match and uniqueness and extras = 0 together.
Bin: REFUSED
Gates: none
Reasons: Each listed family is computed, closed under its operations, and free of a new real. Uniqueness fails inside the family, and that failure is not a leak. Selecting one member would add an extra. The promotion gate is unchanged. The 15 extras are sound. They are not locks.
Baseline written: NO
Lock changed: NO
```

The sign family in `4D_GATES.md` is in the same state, and it is not one of the six families named in that verdict. Its members are the unmodified Euclidean operator and the four operators obtained by multiplying one fibre-blind generator by \(i\). Every member is flat. No member is selected. The isolate slot `dynamical_4d_eom` stays empty.

Hop-mass stays MAP. Leftover extras are \(\tau\) and hop-case.

The nine products in `MASS_MAP.md` are a CLASS/MAP family. The zero branch is \(m = 0\).

Occupancy names stay names.

Do not convert a value to GeV.

Do not touch `complete_baseline.json`.

## Banned readings

These two readings are mistakes. They are rules. They are not extras, and they are not locks.

The swapped \(9/4\) label is banned. The live identity is \(4\kappa = 9/4\) and \(4\kappa+1 = 13/4\). Writing \(4\kappa+1 = 9/4\) is the banned swap.

The reading "\(9/16\) is \(G_N\)" is banned. \(\kappa = 9/16\) stays the locked pure number.

Newton's constant, as a constant whose value no locked atom fixes, stays an open physics hole. The banned reading is the identification of that hole with \(9/16\). Review record `G_N`: live_bin FORBIDDEN, extra `G_N`, promoted=false. Open is kept beside FORBIDDEN.

## Review record rows

Addressable is not forced. These citations do not promote a row. CLASS and UNKNOWN are both written where both words are in play. They are not resolved.

| hole | live_bin | extra | promoted |
|------|----------|-------|----------|
| positive_eom | UNKNOWN | empty section | false |
| unique_color | FORBIDDEN | SU(3)_c | false |
| G_N | FORBIDDEN | G_N | false |
| D5_spectrum | UNKNOWN | eigenvalue list | false |
| warp_factor | CONSISTENT | A, y | false |
| g_mu_nu | OPEN-FIELD | g_mu_nu | false |
| fibration_class | CLASS | fibration_class | false |
| c2 | UNKNOWN | c2 | false |

ISOLATE ≠ THEORY - SAFE WORKSPACE - ZERO KNOBS

## Observational core

Triality is fundamental for observation. The observational core is the joint fixed point ★Ψ = Ψ = Ψ*: the mode, its Hodge dual, and its reality involution are one object. This is not a restatement of ★Ψ = Ψ.

★Ψ = Ψ is the scored edge only. It was applied in the T^{1,1} APS self-dual sector and rules out j2 ≠ 0 there. Ψ = Ψ* and ★Ψ = Ψ* are the other two edges. They are declared. They are not that sector score.

Identifying the joint rule with the scored edge is forbidden. The joint rule has not been run as an asymptotic on-shell boundary condition on Y^14 → M^4. That test is unperformed, not a disproof. c2 and Hol(g_C)=SU(3) stay maps and holonomy. Nothing is promoted.
