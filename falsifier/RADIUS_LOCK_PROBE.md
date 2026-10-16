# Radius lock

WALL-INDEX RELABEL + RADIUS LOCK - ZERO KNOBS

No candidate forces a cutoff radius \(r_c\) with empty extras. Phase 3 is not run. Boundary harmonics are not invented.

| id | candidate | type_match_to_radius? | unique? | extras | live_bin | why |
|----|-----------|----------------------|---------|--------|----------|-----|
| R1 | cone coordinate \(r\) | No | No | coordinate value | REFUSED | \(r\) in \(g_C=dr^2+r^2 g_5\) is a coordinate, not one locked radius. |
| R2 | homothety \(r\partial_r\) | No | No | gauge scale | REFUSED | Files already call this homothety gauge. It does not pick one \(r_c\). |
| R3 | \(T_{\mathrm{wall}}=13/2\) | No | No | dimension | REFUSED | Dimensionless. Not wall thickness. |
| R4 | \(\mathrm{Vol}=16\pi^3/27\) | No | No | normalization | REFUSED | Volume of the normalized 5-metric, not a cone cutoff. |
| R5 | \(\sigma^*=\sqrt{3}/2\) | No | No | dimension | REFUSED | Dimensionless shape. |
| R6 | \(8\pi G_{\mathrm{eff}}=9/16\) | No | No | dimension | REFUSED | A pure number. Not \(G_N\) and not a length. |
| R7 | official residual \(r=0.095716\) | No | No | name collision | REFUSED | A beta residual. The letter \(r\) is not a cone radius. |
| R8 | Planck / wall thickness / spectral cutoff | No | No | new name | REFUSED | Not a locked atom. Not introduced. |

\(r_c\) forced? No

True APS index computed? No
