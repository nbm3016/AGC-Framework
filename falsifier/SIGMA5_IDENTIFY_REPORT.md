# Σ^5 identify

Stored Σ^5 data only. The T^{1,1} diffeotype is not copied. `continuous_knobs = 0`. The probe does not write `complete_baseline.json`.

| id | claim | unique? | live_bin | extras | why |
|----|-------|---------|----------|--------|-----|
| I1 | What exact data are stored for Σ^5? | Yes | FORCED |  | Stored: compact factor Σ^5; dimension 5; odd=true; Euler characteristic 0; note “Odd-dimensional APS wall 5-fold; χ=0.”; Stage 1A survivors (j1,j2,r) = (1/2,0,0), (1,0,0), (3/2,0,0) with lambda-tilde 4.5, 12, 22.5. DIMENSIONAL_SCOPE.md stores that survivor set as not a live 5D mesh. The Sigma5 object has no Betti number, no fundamental group, no spin row, and no contact form. |
| I2 | Does that stored list include a diffeomorphism type? | No | REFUSED |  | The Sigma5 object keys are dim, euler_characteristic, note, odd. The note does not name a diffeomorphism type. TRANSVERSE_BASE records S^2×S^3 and does not name Σ^5. |
| I3 | Does dimension 5 plus χ=0 alone force a unique extras-free diffeomorphism type? | No | UNKNOWN | diffeomorphism type | T11 and Sigma5 are both stored with dimension 5 and Euler characteristic 0. The Sigma5 note records χ=0 for an odd-dimensional APS wall 5-fold. No diffeomorphism type is written from that pair, and no file says the pair classifies one. |
| I4 | Does the Stage 1A survivor set force a unique extras-free diffeomorphism type? | No | UNKNOWN | diffeomorphism type | r0_modes.json stores three modes (j1,j2,r) with lambda-tilde 4.5, 12, 22.5. native_aps_index.json calls the rule a wall-index on j2=0 and says it is not ker D_5 on Ceresole T^{1,1}. The scope file stores the survivor set as not a live 5D mesh. No diffeomorphism type is attached, and no file says the modes classify one. |
| I5 | Do I3 and I4 together force a unique extras-free diffeomorphism type? | No | UNKNOWN | diffeomorphism type | I3 and I4 do not each force an extras-free diffeomorphism type. The files do not decide the pair. |
| I6 | Is Σ^5 the same manifold as T^{1,1}? | No | UNKNOWN | identification Σ^5 with T^{1,1} | The fibre is stored as the product of two named factors. The Σ^5 record does not identify itself with T^{1,1}. The T^{1,1} metric, Betti numbers, spin row, and Reeb quotient are not in the Σ^5 record. No file states that the two factors are diffeomorphic, and no file states that they are not. |
| I7 | Unique extras-free diffeomorphism type for Σ^5 forced? | No | UNKNOWN | diffeomorphism type | Dimension 5, Euler characteristic 0, and the Stage 1A survivor set are stored. They do not carry a diffeomorphism type. The files do not decide one. |

Unique diffeomorphism type forced? Unknown
Baseline byte-stable during probe? Yes

SIGMA5 IDENTIFY PROBE - ZERO KNOBS
