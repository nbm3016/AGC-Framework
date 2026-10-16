# APS index probe

APS INDEX PROBE - NO 3 IN THE CUTOFF - ZERO KNOBS

The wall-index sieve is not used as the definition of an APS index.

## Carriers

| id | object | dim | boundary? | legal_APS_carrier? | extras |
|----|--------|-----|-----------|--------------------|--------|
| L1 | T^{1,1} | 5 | False | False | — |
| L2 | C(T^{1,1}) | 6 | False | False | ['boundary_radius'] |

## Operator

unique spin structure of T^{1,1}; cone tangent reduced by Hol=SU(3).

Riemannian Dirac of g5, plus a Module A wall-index rule that the project file says is not ker D_5.

not stored. The file uses r=0 and j2=0, not the positive spectrum of a boundary Dirac.

imposed as j2=0 in is_self_dual. Not derived from a computed kernel.

## Formula

Named product `1.0`. A-hat integral: False. The file multiplies chi(S^2)^2/4 by the name C2(3) and by sigma*^2. That product is 1. It is not an integral of the A-hat genus.

The file sets eta to 0 because its listed lambda_geometric values are non-negative. That is not eta(0) of D on T^{1,1}.

## Lattice

A finite half-integer list is not forced by a boundary spectrum on disk. The only source is the lattice written in the Python file.

## Stability

On the j1 values stored in r0_modes.json, the r≠0 branch and the j2≠0 branch of the same sieve do not keep the same zero count. This is sieve arithmetic, not an APS kernel.

dim ker D_APS computed from a named operator? No

That integer forced with extras=0? No

Existing sieve is an APS theorem? No

unique_color promoted? No
