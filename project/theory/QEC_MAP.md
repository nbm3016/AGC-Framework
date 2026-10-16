# QEC map

This page lives in `theory\`. Writing it does not lock. It does not promote a row. `continuous_knobs = 0`. `n_LOCK = 35`. `n_promoted = 0`. `n_OPEN = 15`. The slot `dynamical_4d_eom` stays empty.

## The map

The module is seven qubits. A vector sits on one of the 128 address lines. The address is the sign tuple `(s_M, s_J, s_D, s_B, s_A, s_c, s_Sigma)`, read by the operators in `qec\address.py`: `M = YZIIIII`, `J_2`, `D`, `B`, `A`, `C_bit`, and `Sigma`.

That address is the data register. The state being protected is the line the vector occupies.

A check is one of the seven extractors in `qec\syndrome.py`. Six are the twin products of the gamma generators. The seventh is `Gamma_8`. Each extractor is a fixed Pauli on the same seven qubits. It is not a new operator on the slow face.

A syndrome bit is the `F_2` commutation of a fault Pauli with one extractor. The seven bits are the record of which address signs the fault flipped. Recovery, when the catalog has one phase-corrected Pauli for that record, puts the vector back on its line.

## What stays put

The slow face remains `M`, `B_11`, and `B_13` on the `4\times4`. They anticommute. Their product is `-i I_4`. No fourth matrix shares that face. The syndrome is a classical record of commutation. It is not a fourth face node, and the face is not the spacetime metric.

`M`, `B_11`, and `B_13` are not renamed data, check, and syndrome. The data register is the seven-qubit address. The checks are the extractors. The syndrome is the commutation record.

Weight-1 lookup does not give a unique correction on every record. A missing syndrome returns no Pauli. Aliases are degenerate. This page does not claim a unique decoder, and it does not claim `B[2] = 32/75`.

```
FALSIFIER VERDICT
-----------------
Date: 2026-10-14
Claim: The seven-qubit address is the data register, the seven extractors are the checks, and the syndrome is the F_2 commutation record of a fault against those extractors.
Facts: address.py and syndrome.py in qec\. Face product M B_11 B_13 = -i I_4. Anticommutant of the face inside 4×4 is {0}.
Bin: CONSISTENT
Gates: R-metric-swap not fired. R-knob not fired. No fourth face node.
Reasons: The map uses operators the module already has. It does not select a unique code and it does not add a lock.
Baseline written: NO
Lock changed: NO
```
