# 10D face triple

Bins are read off the locked files. `continuous_knobs = 0`. The probe does not write `complete_baseline.json`.

| id | claim | unique? | live_bin | extras | why |
|----|-------|---------|----------|--------|-----|
| F1 | Is Σ^5 × T^{1,1} the locked 10D compact space? | Yes | FORCED |  | isolate compact_fibre is X^{10} = Σ^5 × T^{1,1}. yardstick_lovelock_euler.json records dim 5 and dim 5, product dim 10. five_fold_is_ambient is false. continuous_knobs is 0. fibration_class_unique is false and is a different row. |
| F2 | What 4D faces, if any, are forced by T^{1,1}? | Yes | FORCED |  | generated_inventory.json TRANSVERSE_BASE is unique and FORCED, value S^2×S^2. The recorded reason is the free S^1 quotient of the S^3 factor of T^{1,1} ≃ S^2×S^3. S^2×S^2 is 4-real-dimensional. forces_metric is false. |
| F3 | What 4D faces, if any, are forced by Σ^5? | No | UNKNOWN | 4D face of Σ^5 | yardstick_lovelock_euler.json records Sigma5 as dim 5 with Euler characteristic 0 and no quotient. DIMENSIONAL_SCOPE.md says APS on Σ^5 is the Stage 1A survivor set, not a live 5D mesh. No extras-free 4D face is stored, and no file rules one out. |
| F4 | What does N_gen=3 force as a geometric type? | No | REFUSED |  | falsifier/identification.json stores N_gen as the count of wall-index zeros. three_generations_is_A_lock is false. same_4d_weyl_three_times is false. The zeros are the harmonics of dimensions 2, 3, and 4. That record contradicts a type of three 4-manifolds. |
| F5 | What does ★Ψ=Ψ force as a geometric type? | No | REFUSED |  | isolate filter.role is filter. wall_reading is j2 = 0, where the defect vanishes. The stored statement is ★Ψ = Ψ = Ψ★. No 4-manifold is stored on that row. The record contradicts a geometric face type. |
| F6 | Is a third 4D face forced from the 10-fold with extras=0? | No | REFUSED |  | modulus_menu.json g_mu_nu is OPEN-FIELD with value_forced false. leftover_X4_family is CLASS and is not a unique 4-fold. CP2_as_the_4fold and K3_as_the_4fold are FORBIDDEN. page_interface is not a lock and is_g_mu_nu is false. M^4 is the base in the ambient statement, and the 10-fold is the fibre. Those rows contradict a third 4D face forced from the 10-fold with extras 0. |
| F7 | Is a unique triple of 4D faces forced? | No | REFUSED |  | A unique triple needs F2, F3, and F6 each FORCED with extras 0. At least one of those legs is contradicted by the files. |

Unique 4D face from T^{1,1}: Yes (S^2×S^2)
Unique second face from Σ^5: Unknown
Unique third face: No
Unique triple forced? No
Baseline byte-stable during probe? Yes

10D FACE TRIPLE PROBE - ZERO KNOBS
