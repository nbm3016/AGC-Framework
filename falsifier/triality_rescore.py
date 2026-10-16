"""Apply triality as rotation. Time is exhaust. Mass is data.

Reads the 35 locked atoms. Writes triality_rescore.json and
TRIALITY_RESCORE.md only. Does not rewrite complete_baseline.json.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "triality_rescore.json"
OUT_MD = ROOT / "TRIALITY_RESCORE.md"


def main() -> int:
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    if isolate["continuous_knobs"] != 0:
        raise SystemExit("continuous_knobs is not 0")
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")
    by_name = {item["name"]: item for item in locks}
    filt = isolate["filter"]

    possibilities = [{"name": item["name"], "value": item.get("value")} for item in locks]

    star_same = "same involution" in filt["star_meaning"] and "not a second operator" in filt["star_meaning"]
    wall_zero = "j2 = 0" in filt["wall_reading"] and "vanishes" in filt["wall_reading"]
    dirac = by_name["DIRAC_T11"]["value"]
    reeb_named = "xi" in str(by_name["SASAKI_PHI_J"]["value"]) or "xi" in str(by_name["J_CONE"]["value"])
    kappa = by_name["eight_pi_G_eff_number"]["value"]
    t_wall = by_name["T_wall_identity"]["value"]
    hol = by_name["CONE_HOLONOMY"]

    # Occupied seats carry the wall modes. The count of those modes is the data.
    # N_gen, lambda_tilde, and n_eta label that same triple. They are not three masses.
    mode_count = by_name["wall_zero_count"]["value"]
    if mode_count != 3 or by_name["wall_zero_count"]["extras"] != 0:
        raise SystemExit("wall-zero count is not an extras-free 3")
    mass_candidate = mode_count

    # Hodge on the wall: the defect ||star Psi - Psi||^2 vanishes. Output 0.
    hodge_out = 0 if wall_zero else None
    # Dirac is locked as Dirac(g_5). The wall modes are not stored as its eigenvectors.
    # No extras-free non-zero Dirac generator is among the 35.
    dirac_generator = None
    # Reeb xi is locked. No extras-free Reeb eigenvalue of the wall modes is among the 35.
    reeb_generator = None if reeb_named else None

    extras_free_outputs = [hodge_out]
    nonzero = [value for value in extras_free_outputs if value not in (0, None)]
    if nonzero:
        time_bin = "EMERGENT"
        exhaust = nonzero[0]
    elif extras_free_outputs and all(value == 0 for value in extras_free_outputs):
        time_bin = "TRIVIAL"
        exhaust = 0
    else:
        raise SystemExit("exhaust was neither a non-zero extras-free generator nor identically zero")

    seats = [
        {"seat": "Ψ", "role": "mode", "built": True, "observer": True, "record": "built"},
        {"seat": "★Ψ", "role": "wall reading", "built": True, "observer": True, "record": "built"},
        {
            "seat": "Ψ*",
            "role": "declared",
            "built": False,
            "observer": False,
            "record": "declared",
            "not_filled_by": "Ψ★" if star_same else None,
        },
    ]
    observers = sum(1 for seat in seats if seat["observer"])
    occupied = sum(1 for seat in seats if seat["built"])

    # Zero exhaust resolves no locked row. Bins stay LOCK. Nothing is deleted.
    rescored = []
    changed = 0
    for item in locks:
        rescored.append(
            {
                "name": item["name"],
                "prior": "LOCK",
                "bin": "LOCK",
                "changed": False,
                "why": "The extras-free exhaust is 0. It does not resolve this row.",
            }
        )
    if kappa != "9/16" or t_wall != "13/2" or hol.get("stored_as") != "holonomy":
        raise SystemExit("kappa, T_wall, or holonomy storage moved")

    rows = [
        {
            "id": "R1",
            "object": "possibility set",
            "seat": "shared",
            "data": 35,
            "exhaust": "",
            "bin": "FORCED",
            "why": "35 locks, one list. Ψ is the mode. ★Ψ is the wall reading. Ψ* is declared. Ψ★ is the same involution as the left star, so the left star does not fill Ψ*.",
        },
        {
            "id": "R2",
            "object": "observers",
            "seat": "Ψ, ★Ψ",
            "data": mass_candidate,
            "exhaust": "",
            "bin": "FORCED",
            "why": "The two built seats are observers. The binding ★Ψ = Ψ = Ψ* is not the only observer. Ψ* is not scored as a built observer.",
        },
        {
            "id": "R3",
            "object": "trinodal state",
            "seat": "Ψ, ★Ψ, Ψ*",
            "data": occupied,
            "exhaust": "",
            "bin": "DECLARED",
            "why": "Two built seats are not three. Ψ* stays declared. Ψ is not copied into Ψ*.",
        },
        {
            "id": "R4",
            "object": "mass candidate",
            "seat": "occupied",
            "data": mass_candidate,
            "exhaust": "",
            "bin": "FORCED",
            "why": "The occupied seats carry the three wall modes, extras 0. The count is 3. It is not a kilogram.",
        },
        {
            "id": "R5",
            "object": "time",
            "seat": "two-seat",
            "data": mass_candidate,
            "exhaust": exhaust,
            "bin": time_bin,
            "why": "Hodge on the wall sends the defect to 0. Dirac(g_5) is locked and is not an extras-free eigenvector equation for these modes. The Reeb xi is locked and has no extras-free eigenvalue on them. The extras-free output is identically 0. The two-seat exhaust is partial.",
        },
        {
            "id": "R6",
            "object": "35 rows",
            "seat": "shared",
            "data": 35,
            "exhaust": exhaust,
            "bin": "LOCK",
            "why": "Zero exhaust resolves none of the 35. No row changes. No hypothetical deletion.",
        },
        {
            "id": "R7",
            "object": "c2, holonomy, 9/16, 13/2",
            "seat": "shared",
            "data": mass_candidate,
            "exhaust": exhaust,
            "bin": "LOCK",
            "why": "The exhaust does not force c2. Hol(g_C)=SU(3) stays holonomy. 9/16 stays a number. T_wall stays 13/2.",
        },
        {
            "id": "R8",
            "object": "three-seat exhaust",
            "seat": "Ψ*",
            "data": mass_candidate,
            "exhaust": "partial",
            "bin": "DECLARED",
            "why": "Three-seat exhaust needs Ψ*. That seat is unbuilt. The two-seat exhaust is partial. The 14D run is not determined with extras=0, so it is not computed.",
        },
    ]

    payload = {
        "continuous_knobs": 0,
        "promoted": False,
        "possibilities": possibilities,
        "seats": seats,
        "observers_scored": observers,
        "trinodal_seats_occupied": f"{occupied}/3",
        "mass_candidate": mass_candidate,
        "mass_unit": "data count, not a kilogram",
        "time": time_bin,
        "exhaust": exhaust,
        "two_seat_exhaust": "partial",
        "dirac_operator": dirac,
        "rows_changed": changed,
        "rows": rows,
        "rescored": rescored,
        "held": {
            "c2": "map",
            "Hol_g_C": "holonomy",
            "kappa": kappa,
            "T_wall": t_wall,
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Triality applied",
        "",
        "Time is exhaust. Mass is data. Nothing promoted. `continuous_knobs = 0`.",
        "",
        "| id | object | seat | data | exhaust | bin | why |",
        "|----|--------|------|------|---------|-----|-----|",
    ]
    for item in rows:
        lines.append(
            f"| {item['id']} | {item['object']} | {item['seat']} | {item['data']} | {item['exhaust']} | {item['bin']} | {item['why']} |"
        )
    lines += [
        "",
        f"Observers scored: {observers}",
        f"Trinodal seats occupied: {occupied}/3",
        f"Mass candidate: {mass_candidate}",
        f"Time: {time_bin}",
        f"Rows changed: {changed}",
        "",
        "TRIALITY APPLIED — TIME IS EXHAUST — MASS IS DATA — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
