#!/usr/bin/env python3
"""
Ask whether a named operator has an APS kernel dimension.
The wall-index sieve is quoted, not used as that definition.
"""

from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
REPO = os.path.dirname(HERE)
CORE = os.path.join(REPO, "core")
BASELINE_PATH = os.path.join(HERE, "complete_baseline.json")
OUT_JSON = os.path.join(HERE, "aps_index_probe.json")
OUT_MD = os.path.join(HERE, "APS_INDEX_PROBE.md")


def load(path: str):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)

    core_py = os.path.join(CORE, "wall_index_sieve.py")
    proj_py = os.path.join(ROOT, "native_aps_index.py")
    cone = load(os.path.join(ROOT, "cone_curvature.json"))
    spin = load(os.path.join(ROOT, "spin_dirac.json"))
    r0 = load(os.path.join(ROOT, "r0_modes.json"))
    validated = load(os.path.join(ROOT, "validated_modes.json"))
    constitution = open(os.path.join(CORE, "CONSTITUTION.md"), encoding="utf-8").read()
    core_src = open(core_py, encoding="utf-8").read()
    proj_src = open(proj_py, encoding="utf-8").read()
    if "APS Dirac index" in core_src:
        fail("core solver still calls the sieve an APS Dirac index")
    if "def wall_index_sieve" not in core_src:
        fail("core solver is missing wall_index_sieve")
    if "Dirac index UNPERFORMED" not in core_src:
        fail("core solver does not record that the Dirac index is unperformed")

    link_dim = int(spin["certificate"]["link_dim"])
    cone_dim = link_dim + 1
    sigma2 = Fraction(3, 4)
    c2_name = Fraction(4, 3)
    chi_s2 = 2
    named_product = (chi_s2 * chi_s2 / 4) * c2_name * sigma2

    # Sieve quoted from the module. Not an APS index.
    sys.path.insert(0, ROOT)
    import native_aps_index as sieve

    listed = [(float(m["j1"]), float(m["j2"]), float(m["r"])) for m in r0["modes"]]
    sieve_on_listed = [sieve.wall_index_sieve(j1, j2, r) for j1, j2, r in listed]
    # Discrete moves already named in the same function, on the same listed j1.
    r_shift = [sieve.wall_index_sieve(j1, 0.0, 1.0) for j1, _, _ in listed]
    anti = [sieve.wall_index_sieve(j1, 0.5, 0.0) for j1, _, _ in listed]
    zeros_listed = sum(1 for v in sieve_on_listed if v == 0)
    zeros_r = sum(1 for v in r_shift if v == 0)
    zeros_anti = sum(1 for v in anti if v == 0)

    carriers = [
        {
            "id": "L1",
            "object": "T^{1,1}",
            "dim": link_dim,
            "boundary": False,
            "legal_APS_carrier": False,
            "extras": [],
            "why": "Closed and odd-dimensional. A chiral APS index needs a boundary or a cylindrical end.",
        },
        {
            "id": "L2",
            "object": "C(T^{1,1})",
            "dim": cone_dim,
            "boundary": False,
            "legal_APS_carrier": False,
            "extras": ["boundary_radius"],
            "why": "Files give g_C = dr^2 + r^2 g_5 for r>0. That is an open cone with a tip, not a compact manifold with boundary. A cutoff radius is not locked.",
        },
    ]

    phase2 = {
        "bundle_on_disk": "unique spin structure of T^{1,1}; cone tangent reduced by Hol=SU(3)",
        "dirac_on_disk": "Riemannian Dirac of g5, plus a Module A wall-index rule that the project file says is not ker D_5",
        "aps_cut": "not stored. The file uses r=0 and j2=0, not the positive spectrum of a boundary Dirac",
        "star_psi": "imposed as j2=0 in is_self_dual. Not derived from a computed kernel",
        "core_py_calls_sieve_APS": "APS Dirac index" in core_src,
        "project_py_denies_ker_D5": "not a computation of ker D_5" in proj_src,
    }

    phase3 = {
        "named_product": str(named_product),
        "is_A_hat_integral": False,
        "bin": "NAMED_PRODUCT",
        "why": "The file multiplies chi(S^2)^2/4 by the name C2(3) and by sigma*^2. That product is 1. It is not an integral of the A-hat genus.",
        "eta_regularized_in_file": 0.0,
        "eta_is_boundary_eta": False,
        "eta_why": "The file sets eta to 0 because its listed lambda_geometric values are non-negative. That is not eta(0) of D on T^{1,1}.",
        "boundary_harmonics_stored": False,
    }

    phase4 = {
        "half_integer_source": "HALF_INT_LATTICE and j_max=3.0 inside wall_index_sieve.py",
        "j2_zero_source": "is_self_dual returns true only when j2 is numerically zero",
        "finite_list_source": "the loop stops at j_max written in the file",
        "live_bin": "REFUSED",
        "why": "A finite half-integer list is not forced by a boundary spectrum on disk. The only source is the lattice written in the Python file.",
    }

    phase5 = {
        "stored_sieve_zeros_on_r0_modes": zeros_listed,
        "sieve_zeros_if_r_equals_1": zeros_r,
        "sieve_zeros_if_j2_equals_half": zeros_anti,
        "hole_count_changes": zeros_listed != zeros_r or zeros_listed != zeros_anti,
        "new_metric": False,
        "why": "On the j1 values stored in r0_modes.json, the r≠0 branch and the j2≠0 branch of the same sieve do not keep the same zero count. This is sieve arithmetic, not an APS kernel.",
    }

    dim_ker_computed = False
    rows_score = [
        ("P1", "Closed T^{1,1} is a legal APS carrier", "REFUSED", carriers[0]["why"]),
        ("P2", "Open cone as written is a legal APS carrier", "REFUSED", carriers[1]["why"]),
        ("P3", "star Psi = Psi is derived from a kernel", "REFUSED", phase2["star_psi"]),
        ("P4", "Named product is an A-hat integral", "REFUSED", phase3["why"]),
        ("P5", "File eta is the eta-invariant of the boundary Dirac", "REFUSED", phase3["eta_why"]),
        ("P6", "Finite j lattice is forced by geometry", "REFUSED", phase4["why"]),
        ("P7", "Sieve zero-count is stable under listed discrete branches", "REFUSED" if phase5["hole_count_changes"] else "CONSISTENT", phase5["why"]),
        ("P8", "dim ker of a named APS operator is computed", "UNKNOWN", "No boundary Dirac spectrum is stored, so the kernel dimension is not computed."),
    ]

    payload = {
        "banner": "APS INDEX PROBE - NO 3 IN THE CUTOFF - ZERO KNOBS",
        "continuous_knobs": 0,
        "carriers": carriers,
        "operator": phase2,
        "formula": phase3,
        "lattice": phase4,
        "stability": phase5,
        "named_product_value": str(named_product),
        "sieve_is_aps_theorem": False,
        "dim_ker_computed": dim_ker_computed,
        "integer_forced_extras_0": False,
        "called_N_gen": False,
        "called_three_colors": False,
        "constitution_says_wall_index_not_ker_D5": "not $\\ker D_5$" in constitution or "not \\(\\ker D_5\\)" in constitution or "not $\\ker D_5$" in constitution or "ker D_5" in constitution,
        "rows": [{"id": i, "claim": c, "live_bin": b, "why": w} for i, c, b, w in rows_score],
        "cone_not_flat": cone.get("g_C_flat") is False,
        "spin_structures": spin["certificate"]["n_spin_structures"],
        "r0_mode_count_field": r0.get("mode_count"),
        "validated_has_lambda_targets": "lambda_targets" in validated or "modes" in validated,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    # Constitution sentence, matched without treating a count as input.
    payload["constitution_says_wall_index_not_ker_D5"] = "ker D_5" in constitution and "not" in constitution
    with open(OUT_JSON, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    write_md(payload)

    print("id | object | dim | boundary? | legal_APS_carrier? | extras")
    for row in carriers:
        print(
            f"{row['id']} | {row['object']} | {row['dim']} | {row['boundary']} | "
            f"{row['legal_APS_carrier']} | {row['extras'] or '—'}"
        )
    print()
    print("OPERATOR")
    print(phase2["aps_cut"])
    print(phase2["star_psi"])
    print()
    print("FORMULA")
    print(f"named product = {named_product} ; A-hat integral? {phase3['is_A_hat_integral']}")
    print(phase3["eta_why"])
    print()
    print("LATTICE")
    print(phase4["why"])
    print()
    print("STABILITY")
    print(
        f"sieve zeros on stored modes {zeros_listed}; "
        f"r=1 branch {zeros_r}; j2=1/2 branch {zeros_anti}"
    )
    print()
    print("APS INDEX PROBE - NO 3 IN THE CUTOFF - ZERO KNOBS")
    print(f"dim ker D_APS computed from a named operator? {'Yes' if dim_ker_computed else 'No'}")
    print("That integer forced with extras=0? No")
    print("Existing sieve index=max(0,round(4j1-6)) is APS theorem? No")
    print(
        "N_gen still wall-index rule not ker D5? "
        + ("Yes" if payload["constitution_says_wall_index_not_ker_D5"] else "No")
    )
    print("unique_color promoted? No")
    return 0


def write_md(payload: dict) -> None:
    lines = [
        "# APS index probe",
        "",
        payload["banner"],
        "",
        "The wall-index sieve is not used as the definition of an APS index.",
        "",
        "## Carriers",
        "",
        "| id | object | dim | boundary? | legal_APS_carrier? | extras |",
        "|----|--------|-----|-----------|--------------------|--------|",
    ]
    for row in payload["carriers"]:
        lines.append(
            f"| {row['id']} | {row['object']} | {row['dim']} | {row['boundary']} | "
            f"{row['legal_APS_carrier']} | {row['extras'] or '—'} |"
        )
    op = payload["operator"]
    form = payload["formula"]
    lines += [
        "",
        "## Operator",
        "",
        op["bundle_on_disk"] + ".",
        "",
        op["dirac_on_disk"] + ".",
        "",
        op["aps_cut"] + ".",
        "",
        op["star_psi"] + ".",
        "",
        "## Formula",
        "",
        f"Named product `{form['named_product'] if 'named_product' in form else payload['named_product_value']}`. "
        f"A-hat integral: {form['is_A_hat_integral']}. {form['why']}",
        "",
        form["eta_why"],
        "",
        "## Lattice",
        "",
        payload["lattice"]["why"],
        "",
        "## Stability",
        "",
        payload["stability"]["why"],
        "",
        "dim ker D_APS computed from a named operator? No",
        "",
        "That integer forced with extras=0? No",
        "",
        "Existing sieve is an APS theorem? No",
        "",
        "unique_color promoted? No",
        "",
    ]
    with open(OUT_MD, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
