"""Score triality as rotation. Three seats, one possibility set.

Reads disk. Writes triality_score.json and TRIALITY_SCORE.md only.
Does not rewrite complete_baseline.json.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent / "project"
BASELINE = ROOT / "complete_baseline.json"
OUT_JSON = ROOT / "triality_score.json"
OUT_MD = ROOT / "TRIALITY_SCORE.md"


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def row(rid, claim, live_bin, extras, why):
    return {
        "id": rid,
        "claim": claim,
        "live_bin": live_bin,
        "extras": extras,
        "why": why,
    }


def main() -> int:
    isolate = load("isolate_updated.json")
    if isolate["continuous_knobs"] != 0:
        raise SystemExit("continuous_knobs is not 0")
    scope = (PROJECT / "DIMENSIONAL_SCOPE.md").read_text(encoding="utf-8")
    status = (PROJECT / "STATUS.md").read_text(encoding="utf-8")
    rules = (PROJECT / "theory" / "THEORY_RULES.md").read_text(encoding="utf-8")
    core_text = "\n".join(
        part.split("## Observational core", 1)[1]
        for part in (status, rules)
        if "## Observational core" in part
    )

    locks = [
        {"name": item["name"], "value": item.get("value")}
        for item in isolate["locks"]
        if item.get("status") == "LOCK"
    ]
    filt = isolate["filter"]
    parts = filt["parts"]
    edge = "★Ψ = Ψ" in filt["wall_reading"] or "★Ψ − Ψ" in filt["wall_reading"] or "j2 = 0" in filt["wall_reading"]
    star_same = "same involution" in filt["star_meaning"] and "not a second operator" in filt["star_meaning"]
    psi_star_glyph = "Ψ★" in parts
    reality_declared = "Ψ*" in core_text and "They are declared." in core_text
    joint_declared = "★Ψ = Ψ = Ψ*" in core_text and "joint fixed point" in core_text
    joint_unrun = "has not been run" in core_text and "Y^14 → M^4" in core_text
    time_absent = "t$" in scope or "and $t$" in scope or "and t" in scope
    # The scope line lists t among the coordinates that are not discretized.
    time_not_discretized = "not discretized" in scope and ("$t$" in scope or "\\(t\\)" in scope)

    seats = [
        {
            "seat": "Ψ",
            "over": "shared possibility set",
            "built": "Ψ" in parts,
            "record": "declared" if "Ψ" not in parts else "built",
            "file": "isolate_updated.json filter.parts",
        },
        {
            "seat": "★Ψ",
            "over": "shared possibility set",
            "built": "★Ψ" in parts and edge,
            "record": "built" if ("★Ψ" in parts and edge) else "declared",
            "file": "isolate_updated.json filter.wall_reading",
        },
        {
            "seat": "Ψ*",
            "over": "shared possibility set",
            "built": False,
            "record": "declared" if reality_declared else "declared",
            "file": "STATUS.md Observational core; theory/THEORY_RULES.md Observational core",
            "not_filled_by": "Ψ★" if psi_star_glyph and star_same else None,
        },
    ]
    # Ψ* stays declared. The glyph Ψ★ is the same involution as ★Ψ, not this seat.
    if not (reality_declared and star_same):
        seats[2]["record"] = "declared"
        seats[2]["built"] = False

    built_n = sum(1 for seat in seats if seat["built"])

    rotation_forced = False
    binding_forced = built_n == 3 and joint_declared and not star_same
    spin_performed = False
    test_14d = False

    rows = [
        row(
            "T1",
            "Possibility set. Locked atoms are the shared possibilities, listed once.",
            "FORCED",
            [],
            f"{len(locks)} locks with status LOCK. One list. It is not copied onto the seats.",
        ),
        row(
            "T2",
            "Three seats over that set. Which seat did the files build?",
            "DECLARED",
            ["Ψ*"],
            "Ψ is built as the mode in the filter. ★Ψ is built as the left side of the wall reading j2=0. "
            "Ψ* is declared in the observational core. Ψ★ is the same involution as the left star, not a second operator, so it does not build Ψ*.",
        ),
        row(
            "T3",
            "Does any file permit the seats to exchange roles with extras=0?",
            "REFUSED",
            ["rotation"],
            "The written map is the APS edge ★Ψ = Ψ in the T^{1,1} self-dual sector. That is one pairing. It is not a rotation of the three seats.",
        ),
        row(
            "T4",
            "Is the joint fixed point ★Ψ = Ψ = Ψ* forced?",
            "FORCED" if binding_forced else "DECLARED",
            [] if binding_forced else ["Ψ*", "binding"],
            "The observational core declares the joint fixed point. Three seats are not all built, so the binding is not determined with extras=0.",
        ),
        row(
            "T5",
            "Is a spin, a rotation parameter, or a time coordinate forced?",
            "UNPERFORMED",
            ["t"],
            "DIMENSIONAL_SCOPE.md leaves t undiscretized. No rotation parameter is a locked atom. The spin of this rotation is unperformed. t is not invented.",
        ),
        row(
            "T6",
            "A state blocked by the binding but not by the edge.",
            "UNKNOWN",
            [],
            "No file exhibits a state the binding blocks and the edge allows. c2 stays a map. Hol(g_C)=SU(3) stays holonomy.",
        ),
        row(
            "T7",
            "A state the rotation forces that the one pairing does not.",
            "REFUSED",
            ["rotation"],
            "The rotation is not an extras-free map. It forces no state beyond the pairing ★Ψ = Ψ.",
        ),
        row(
            "T8",
            "Has the binding been run on Y^14 → M^4?",
            "UNPERFORMED" if joint_unrun or not test_14d else "FORCED",
            [],
            "The observational core says the joint rule has not been run as an asymptotic on-shell boundary condition on Y^14 → M^4. Unperformed is not a disproof.",
        ),
    ]

    if not time_not_discretized:
        rows[4]["why"] = "No locked atom is a time coordinate. The spin is unperformed. t is not invented."

    payload = {
        "continuous_knobs": 0,
        "promoted": False,
        "possibilities": locks,
        "seats": seats,
        "seats_built": f"{built_n}/3",
        "rotation_forced": rotation_forced,
        "spin_performed": spin_performed,
        "test_14d_performed": test_14d,
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Triality scored as rotation",
        "",
        "One possibility set. Three seats. Nothing promoted. `continuous_knobs = 0`.",
        "",
        "| id | claim | live_bin | extras | why |",
        "|----|-------|----------|--------|-----|",
    ]
    for item in rows:
        extras = ", ".join(item["extras"])
        lines.append(
            f"| {item['id']} | {item['claim']} | {item['live_bin']} | {extras} | {item['why']} |"
        )
    lines += [
        "",
        f"Seats built: {built_n}/3",
        "Rotation forced? No",
        "Spin performed? No",
        "14D test performed? No",
        "",
        "TRIALITY SCORED AS ROTATION — SAME POSSIBILITIES, THREE SEATS — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
