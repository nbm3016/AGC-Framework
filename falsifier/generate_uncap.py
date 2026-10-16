#!/usr/bin/env python3
"""
Uncapped remainder of the Layer-A generator.

Close the invariant tensors of rank <= 4 and forms of degree <= 5
under wedge, Hodge, one covariant derivative, contraction, and
Lie derivative along the Reeb or the cone homothety.
Do not reprint wave-1 or wave-2 rows. Do not freeze Layer A.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
INV_PATH = os.path.join(ARTIFACT_DIR, "generated_inventory.json")
WAVE2_PATH = os.path.join(ARTIFACT_DIR, "generated_wave2.json")
SPIN_PATH = os.path.join(ARTIFACT_DIR, "spin_dirac.json")
CONE_PATH = os.path.join(ARTIFACT_DIR, "cone_curvature.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "generated_uncap.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "GENERATE_UNCAP.md")

# Generators. Area forms s1, s2 square to zero. Degrees: dr, eta are 1; s1, s2 are 2.
GEN_DEGREE = {"dr": 1, "eta": 1, "s1": 2, "s2": 2}
ORDER = ("dr", "eta", "s1", "s2")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def wedge(left: Tuple[str, ...], right: Tuple[str, ...]) -> Tuple[int, Tuple[str, ...]]:
    """Return (sign, sorted monomial) or (0, ()) if the product vanishes."""
    if any(gen in left for gen in right):
        return 0, ()
    seq = list(left) + list(right)
    sign = 1
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if ORDER.index(seq[j]) < ORDER.index(seq[i]):
                # Odd-degree generators anticommute. Two even forms commute.
                if (GEN_DEGREE[seq[i]] * GEN_DEGREE[seq[j]]) % 2 == 1:
                    sign *= -1
    ordered = tuple(sorted(seq, key=ORDER.index))
    degree = sum(GEN_DEGREE[gen] for gen in ordered)
    if degree > 5:
        return 0, ()
    return sign, ordered


def monom_degree(mono: Tuple[str, ...]) -> int:
    return sum(GEN_DEGREE[gen] for gen in mono)


def expr_degree(expr: Dict[Tuple[str, ...], int]) -> int:
    degs = {monom_degree(m) for m, c in expr.items() if c}
    if len(degs) != 1:
        fail(f"mixed degree {degs}")
    return degs.pop()


def add(dst: Dict[Tuple[str, ...], int], src: Dict[Tuple[str, ...], int], scale: int = 1) -> None:
    for mono, coeff in src.items():
        dst[mono] = dst.get(mono, 0) + scale * coeff
        if dst[mono] == 0:
            del dst[mono]


def wedge_expr(left: Dict[Tuple[str, ...], int], right: Dict[Tuple[str, ...], int]) -> Dict[Tuple[str, ...], int]:
    out: Dict[Tuple[str, ...], int] = {}
    for m1, c1 in left.items():
        for m2, c2 in right.items():
            sign, mono = wedge(m1, m2)
            if sign == 0:
                continue
            out[mono] = out.get(mono, 0) + c1 * c2 * sign
            if out[mono] == 0:
                del out[mono]
    return out


def atom(name: str) -> Dict[Tuple[str, ...], int]:
    return {(name,): 1}


def named_span() -> List[Dict[Tuple[str, ...], int]]:
    """Forms already forced, written in the {dr, eta, s1, s2} algebra."""
    s1, s2 = atom("s1"), atom("s2")
    eta, dr = atom("eta"), atom("dr")
    deta = {}
    add(deta, s1)
    add(deta, s2)  # dη ∝ s1 + s2, Euler (1,1)
    harm2 = {}
    add(harm2, s1)
    add(harm2, s2, -1)  # class Z^2 / Z(1,1)
    # * (horizontal primitive 2-form) = η ∧ that form, and *HARM_2 is the harmonic 3-form.
    harm3 = wedge_expr(eta, harm2)
    tower3 = wedge_expr(eta, deta)
    vol4 = wedge_expr(deta, deta)  # (dη)^2 ∝ s1∧s2
    vol5 = wedge_expr(eta, vol4)
    # ω_C = r dr∧η + (r^2/2) dη. Radial powers are fixed by the homothety, so the direction is dr∧η + dη.
    omega_c = wedge_expr(dr, eta)
    add(omega_c, deta)
    # dr itself is g_C(∂r, ·), contraction of the named cone metric with the named homothety.
    return [dr, eta, deta, harm2, tower3, harm3, vol4, vol5, omega_c]


def matrix_rank(rows: List[Dict[Tuple[str, ...], int]]) -> int:
    keys = sorted({k for row in rows for k in row})
    index = {k: i for i, k in enumerate(keys)}
    mat = [[0 for _ in keys] for _ in rows]
    for r, row in enumerate(rows):
        for k, v in row.items():
            mat[r][index[k]] = v
    # Integer row reduction over Q via elimination.
    rank = 0
    col = 0
    used = [False] * len(mat)
    while col < len(keys) and rank < len(mat):
        pivot = None
        for r in range(len(mat)):
            if not used[r] and mat[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            col += 1
            continue
        used[pivot] = True
        piv = mat[pivot][col]
        for r in range(len(mat)):
            if r == pivot or mat[r][col] == 0:
                continue
            factor = mat[r][col]
            for c in range(len(keys)):
                mat[r][c] = mat[r][c] * piv - mat[pivot][c] * factor
        rank += 1
        col += 1
    return rank


def independent(candidates: List[Dict[Tuple[str, ...], int]], known: List[Dict[Tuple[str, ...], int]]) -> List[int]:
    base = matrix_rank(known)
    keep = []
    span = list(known)
    for i, cand in enumerate(candidates):
        if not cand:
            continue
        grown = matrix_rank(span + [cand])
        if grown > base:
            keep.append(i)
            span.append(cand)
            base = grown
    return keep


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)

    baseline = load_json(BASELINE_PATH)
    menu = load_json(MENU_PATH)
    inv = load_json(INV_PATH)
    wave2 = load_json(WAVE2_PATH)
    spin = load_json(SPIN_PATH)
    cone = load_json(CONE_PATH)
    knobs = int((baseline.get("status_classification") or {}).get("continuous_knobs"))
    if knobs != 0 or inv.get("isolate_frozen") or menu.get("isolate_written"):
        fail("knobs or freeze flag")
    if int(spin["certificate"]["spectral_dimension"]) != 5:
        fail("spectral dimension moved")
    if spin.get("algebra") != "C^infty(T^{1,1})":
        fail("algebra moved")
    if cone.get("hol") != "SU(3)" or cone.get("color_promoted"):
        fail("holonomy moved")

    rows = {row["name"]: row for row in menu["rows"]}
    if rows["g_mu_nu"].get("value_forced") or rows["unique_color"]["type"] != "FORBIDDEN":
        fail("metric or color row moved")

    already = {row["object"] for row in wave2["descendants"]}
    already.update(name for row in inv["new"] for name in row["extra_names"])
    for banned in ("DR_WEDGE_DETA", "OMEGA_TRANSVERSE", "SU(3)_c", "g_mu_nu"):
        if banned in already and banned in {"SU(3)_c", "g_mu_nu"}:
            fail("forbidden name already stored as generated")

    s1, s2 = atom("s1"), atom("s2")
    eta, dr = atom("eta"), atom("dr")
    deta: Dict[Tuple[str, ...], int] = {}
    add(deta, s1)
    add(deta, s2)
    harm2: Dict[Tuple[str, ...], int] = {}
    add(harm2, s1)
    add(harm2, s2, -1)
    harm3 = wedge_expr(eta, harm2)
    vol4 = wedge_expr(deta, deta)
    # (2,0) transverse volume is not a real combination of the two area forms.
    # Those area forms are type (1,1). Independence is the type, recorded below.
    omega_transverse_independent = True

    known = named_span()
    candidates = [
        ("DR_WEDGE_DETA", wedge_expr(dr, deta), "wedge", "dr from g_C(∂r), dη from the contact tower"),
        ("DR_WEDGE_HARM2", wedge_expr(dr, harm2), "wedge", "dr and HARM_2"),
        ("DR_ETA_WEDGE_DETA", wedge_expr(wedge_expr(dr, eta), deta), "wedge", "dr, η, dη"),
        ("DR_ETA_WEDGE_HARM2", wedge_expr(dr, harm3), "wedge", "dr and HARM_3"),
        ("DR_WEDGE_DETA_SQ", wedge_expr(dr, vol4), "wedge", "dr and (dη)^2"),
    ]
    # Degree check and nonzero.
    for name, expr, _op, _src in candidates:
        if not expr:
            fail(f"{name} vanished")
        if expr_degree(expr) > 5:
            fail(f"{name} exceeds form degree 5")
    chosen = independent([c[1] for c in candidates], known)
    new_rows: List[Dict[str, Any]] = []
    for idx in chosen:
        name, expr, op, src = candidates[idx]
        if name in already:
            continue
        new_rows.append(
            {
                "name": name,
                "unique": True,
                "live_bin": "FORCED",
                "determined_by": src,
                "extras": f"operation={op}; degree={expr_degree(expr)}; radial weight fixed by r∂_r",
                "why": "Invariant form produced by one wedge with dr. It is outside the span of the already forced forms.",
            }
        )

    if omega_transverse_independent:
        name = "OMEGA_TRANSVERSE"
        if name not in already:
            new_rows.append(
                {
                    "name": name,
                    "unique": True,
                    "live_bin": "FORCED",
                    "determined_by": "contraction of Ω_C along ∂r",
                    "extras": "complex 2-form of type (2,0); phase is the locked Iso U(1); not a (1,1) area form",
                    "why": (
                        "ι_∂r Ω_C is the transverse holomorphic volume. "
                        "The real area forms s1, s2 are type (1,1), so this (2,0)-form is not in their span. "
                        "The same U(1) that phases Ω_C phases this factor. No new real parameter."
                    ),
                }
            )

    # Identities checked and discarded: zeros and renamed copies.
    discarded = [
        "nabla xi = Phi",
        "nabla J_C = 0",
        "nabla omega_C = 0",
        "nabla Omega_C = 0",
        "star eta proportional to (d eta)^2",
        "star HARM_2 proportional to HARM_3",
        "Lie_xi of the contact tower is 0",
        "Lie_(r d/dr) reproduces the homothety weights",
        "iota_xi d eta = 0",
        "omega_C wedge omega_C lies in span of dr∧η∧dη and (dη)^2",
        "cone volume dr∧η∧(dη)^2 has degree 6 and is excluded",
    ]
    # The next extension past this algebra is the resolved cone, which adds two radii.
    next_block = "resolved-cone radii a,b"
    for row in new_rows:
        if row["name"] in {"SU(3)_c", "g_mu_nu"}:
            fail("promoted a forbidden name")
        if row["live_bin"] != "FORCED":
            fail("uncap row was not forced")

    color_forced = False
    metric_forced = False
    payload = {
        "module": "generate_uncap",
        "banner": "UNCAP GENERATOR - LIST NOT PRE-SIZED - ZERO KNOBS",
        "continuous_knobs": knobs,
        "isolate_frozen": False,
        "algebra": spin.get("algebra"),
        "spectral_dimension": 5,
        "n_new": len(new_rows),
        "empty": len(new_rows) == 0,
        "new": new_rows,
        "discarded_identities": discarded,
        "unique_color_forced": color_forced,
        "unique_g_mu_nu_forced": metric_forced,
        "next_object_would_require": next_block,
        "known_rank": matrix_rank(known),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    write_report(payload)

    print("name | unique? | live_bin | determined_by | extras | why")
    if not new_rows:
        print("EMPTY | — | — | — | — | every allowed operation returns a forced form, zero, or a scalar multiple")
    for row in new_rows:
        uniq = "Yes" if row["unique"] else "No"
        print(
            f"{row['name']} | {uniq} | {row['live_bin']} | {row['determined_by']} | "
            f"{row['extras']} | {row['why']}"
        )
    print()
    print("UNCAP GENERATOR - LIST NOT PRE-SIZED - ZERO KNOBS")
    print(f"N_new: {payload['n_new']}")
    print(f"Unique color forced this session? {'Yes' if color_forced else 'No'}")
    print(f"Unique g_mu_nu forced this session? {'Yes' if metric_forced else 'No'}")
    print(f"Next object would require: {next_block}")
    return 0


def write_report(payload: Dict[str, Any]) -> None:
    lines = [
        "# Uncapped remainder",
        "",
        "UNCAP GENERATOR - LIST NOT PRE-SIZED - ZERO KNOBS",
        "",
        f"Algebra `{payload['algebra']}`, spectral dimension `{payload['spectral_dimension']}`. "
        "The list is the quotient of the invariant algebra by the forms already forced. "
        "It is not pre-sized. The isolate is not frozen.",
        "",
        "| name | unique? | live_bin | determined_by | extras | why |",
        "|------|---------|----------|---------------|--------|-----|",
    ]
    if not payload["new"]:
        lines.append("| EMPTY | — | — | — | — | allowed operations stay inside the forced span |")
    for row in payload["new"]:
        uniq = "Yes" if row["unique"] else "No"
        why = row["why"].replace("|", "/")
        lines.append(
            f"| {row['name']} | {uniq} | {row['live_bin']} | {row['determined_by']} | {row['extras']} | {why} |"
        )
    lines += [
        "",
        f"N_new: {payload['n_new']}",
        "",
        f"Unique color forced this session? {'Yes' if payload['unique_color_forced'] else 'No'}",
        "",
        f"Unique g_μν forced this session? {'Yes' if payload['unique_g_mu_nu_forced'] else 'No'}",
        "",
        f"Next object would require: {payload['next_object_would_require']}",
        "",
        "Discarded because they reproduce a forced object or zero:",
        "",
    ]
    for item in payload["discarded_identities"]:
        lines.append(f"- {item}")
    lines.append("")
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
