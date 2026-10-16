# Wall uniqueness

WALL UNIQUENESS - THIS SIEVE NOT EVERY 5-FOLD - ZERO KNOBS

This wall is T^{1,1} as first-slice SE with b2=b3=1. It is not proven unique among all 5-manifolds.

| id | claim | unique? | live_bin | extras | why |
|----|-------|---------|----------|--------|-----|
| U1 | locked atoms force T^{1,1} among all 5-manifolds | No | REFUSED | bases_outside_first_slice | controlled_uniqueness.json sets global_landscape_uniqueness false. Uniqueness among all 5-manifolds is not claimed. |
| U2 | locked atoms force T^{1,1} only inside first-slice G_SE | Yes | FORCED | — | The file says lambda-tilde, equivalently sigma*=sqrt(3)/2, isolates T^{1,1} among labeled bases in the first slice. The scope is that slice. |
| U3 | b2=b3=1 kills S^5 and Q^{1,1,1} | Yes | FORCED | — | Locked b2=1, b3=1. S^5 has b2=0. Q^{1,1,1} as the (1,1,1) circle bundle has b2=2. |
| U4 | Iso=SU(2)×SU(2)×U(1) kills M^{p,q} as this wall | Yes | FORCED | — | This wall's isometry has dimension 7 and no SU(3) factor. M^{p,q} is dimension 7 with an SU(3) factor. Not this wall. (p,q) is not selected. |
| U5 | the wall-index sieve exists only on this Iso | No | REFUSED | other_isometry | The sieve is written in the j1, j2 labels of this isometry. The files do not prove that no other group could carry a three-zero count. |
| U6 | some other locked 5-fold also has exactly three zeros under the same rule with extras=0 | No | REFUSED | second_locked_5fold | No second locked 5-fold with that zero count and empty extras is on disk. |
| U7 | Y^{14} / fibration_class is forced this session | No | REFUSED | fibration_class | The same uniqueness file says uniqueness among all 14D fibrations remains open. |

Y^{14} forced? No

Family physics reopened? No
