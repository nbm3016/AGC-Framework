"""Score three structures for Σ^5 against the locks. None is selected."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "probe_sigma5.json"
OUT_MD = ROOT / "PROBE_SIGMA5.md"


def lie_dim_su(n: int) -> int:
    return n * n - 1


def lie_dim_so(n: int) -> int:
    return n * (n - 1) // 2


def main() -> int:
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    yard = json.loads((ROOT / "yardstick_lovelock_euler.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")

    sigma = yard["lovelock_catalog"]["internal_factors"]["Sigma5"]
    allowed = {"dim", "odd", "euler_characteristic", "note"}
    if set(sigma) - allowed:
        raise SystemExit(f"unexpected Σ^5 keys: {sorted(set(sigma) - allowed)}")
    if "b2" in sigma or "b3" in sigma:
        raise SystemExit("Σ^5 record carries Betti numbers")

    by_name = {item["name"]: item for item in locks}
    wall = by_name["wall_zero_count"]
    hol = by_name["CONE_HOLONOMY"]
    iso = by_name["Iso_group"]
    b2 = by_name["b2"]
    b3 = by_name["b3"]
    if wall.get("extras") != 0 or wall.get("value") != 3:
        raise SystemExit("wall_zero_count is not the locked count 3")
    if hol.get("stored_as") != "holonomy" or hol.get("value") != "SU(3)":
        raise SystemExit("cone holonomy lock is not SU(3) stored as holonomy")
    if iso.get("stored_as") != "isometry" or iso.get("dimension") != 7:
        raise SystemExit("isometry lock is not dimension 7")
    if isolate.get("five_fold_is_ambient") is not False:
        raise SystemExit("five_fold_is_ambient is not false")
    if "Σ^5" not in isolate.get("compact_factors_only", []):
        raise SystemExit("Σ^5 is not a stored compact factor")

    su3 = lie_dim_su(3)
    so3 = lie_dim_so(3)
    su2 = lie_dim_su(2)
    so6 = lie_dim_so(6)
    so5 = lie_dim_so(5)
    if (su3, so3, su2, so6, so5) != (8, 3, 3, 15, 10):
        raise SystemExit("Lie dimensions drifted")

    candidates = [
        {
            "id": "C1",
            "name": "SU(3)/SO(3)",
            "dimension": su3 - so3,
            "isometry_algebra": "contains su(3)",
            "isometry_dimension": su3,
            "isometry_dimension_is": "lower bound",
            "su3_acts_on_candidate": True,
            "su3_action": "The left su(3) action is infinitesimally faithful, so an 8-dimensional su(3) acts by isometries of any SU(3)-invariant metric.",
            "holonomy": "not computed",
            "holonomy_note": "The isotropy algebra is so(3). That isotropy is not a holonomy.",
            "bin": "UNKNOWN",
            "why": "Dimension 5 matches the stored factor. No diffeomorphism type is stored, so the coset is not forced. The identification is an extra.",
        },
        {
            "id": "C2",
            "name": "S^5 = SU(3)/SU(2)",
            "dimension": su3 - su2,
            "isometry_algebra": "so(6)",
            "isometry_dimension": so6,
            "isometry_dimension_is": "exact for the round metric",
            "su3_acts_on_candidate": True,
            "su3_action": "su(3) injects into so(6). An 8-dimensional su(3) acts by isometries of the round metric and is not the full isometry algebra.",
            "holonomy": "SO(5)",
            "holonomy_dimension": so5,
            "holonomy_note": "Holonomy of the round metric is SO(5). The isometry algebra is so(6). The isotropy su(2) is not the holonomy.",
            "bin": "UNKNOWN",
            "why": "Dimension 5 matches the stored factor. No diffeomorphism type is stored, so the sphere is not forced. The round metric is an extra.",
        },
        {
            "id": "C3",
            "name": "wall R × M^4",
            "dimension": 1 + 4,
            "isometry_algebra": "not forced",
            "isometry_dimension": None,
            "isometry_dimension_is": "no metric on M^4 is locked",
            "su3_acts_on_candidate": False,
            "su3_action": "No lock puts an 8-dimensional su(3) on this product.",
            "holonomy": "not forced",
            "holonomy_note": "A product holonomy would be the holonomy of M^4. No locked atom selects g_μν.",
            "bin": "REFUSED",
            "why": "Σ^5 is stored as a compact factor. R × M^4 is not compact.",
        },
    ]
    for row in candidates:
        if row["dimension"] != 5:
            raise SystemExit(f"{row['id']} is not 5-dimensional")

    # No candidate group is re-binned onto a lock of a different role.
    matches = []
    for row in candidates:
        for item in locks:
            if item.get("extras") != 0:
                continue
            if item.get("value") == row["isometry_algebra"] and item.get("stored_as") == "isometry":
                matches.append(item["name"])
    moved = matches if len(matches) == 1 else []
    rescored = [
        {
            "name": item["name"],
            "prior": "LOCK",
            "bin": "RESOLVED" if item["name"] in moved else "LOCK",
            "changed": item["name"] in moved,
        }
        for item in locks
    ]

    payload = {
        "continuous_knobs": 0,
        "promoted": False,
        "selected": None,
        "sigma5": {
            "dim": sigma["dim"],
            "odd": sigma["odd"],
            "euler_characteristic": sigma["euler_characteristic"],
            "note": sigma["note"],
            "keys": sorted(sigma),
            "compact_factor": True,
            "five_fold_is_ambient": False,
            "diffeotype": None,
            "betti_copied_from_T11": False,
            "b2_lock_left_on_its_carrier": b2["value"],
            "b3_lock_left_on_its_carrier": b3["value"],
        },
        "wall_zero_count": {
            "value": wall["value"],
            "role": "generation count",
            "is_representation": False,
            "zeros": wall["zeros"],
            "su2_dimensions": wall["su2_dimensions"],
            "reading": wall["reading"],
        },
        "holonomy_lock": {
            "value": hol["value"],
            "dimension": hol["dimension"],
            "stored_as": hol["stored_as"],
            "reading": hol["reading"],
            "is_isometry": False,
        },
        "isometry_lock": {
            "value": iso["value"],
            "dimension": iso["dimension"],
            "stored_as": iso["stored_as"],
            "carrier": "T^{1,1}",
            "copied_onto_sigma5": False,
        },
        "continuous_group_forced": False,
        "three_modes": {
            "count": 3,
            "carry_group_action": False,
            "su3_triplet": False,
            "why": "The count 3 enumerates three harmonics with SU(2) dimensions 2, 3, and 4. No lock forces one group to act on that count.",
        },
        "candidates": candidates,
        "rows_changed": len(moved),
        "moved": moved,
        "rescored": rescored,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Σ^5 structure score",
        "",
        "No coset is selected. The stored Σ^5 record has dimension 5, odd = true, Euler characteristic 0, and the note “Odd-dimensional APS wall 5-fold; χ=0.” Its keys do not include a diffeomorphism type, a metric, or a Betti number. b2 = 1 and b3 = 1 stay on their own carrier and are not copied. The isometry SU(2)×SU(2)×U(1) has dimension 7 and stays on T^{1,1}.",
        "",
        "wall_zero_count = 3 is the generation count of the harmonics 2⊕3⊕4. It is not a representation.",
        "",
        "Hol(g_C) = SU(3) has dimension 8 and is stored as holonomy of the cone. That is not an isometry fact.",
        "",
        "| id | candidate | dim | isometry algebra | isometry dimension | su(3) acts on the candidate | holonomy | bin |",
        "|----|-----------|-----|------------------|--------------------|-----------------------------|----------|-----|",
    ]
    for row in candidates:
        dimension = row["isometry_dimension"]
        if dimension is None:
            dim_text = "none stored"
        elif row["isometry_dimension_is"] == "lower bound":
            dim_text = f"at least {dimension}"
        else:
            dim_text = str(dimension)
        acts = "yes" if row["su3_acts_on_candidate"] else "no"
        lines.append(
            f"| {row['id']} | {row['name']} | {row['dimension']} | {row['isometry_algebra']} | {dim_text} | {acts} | {row['holonomy']} | {row['bin']} |"
        )
    lines += [
        "",
        "C1. Manifold dimension 8 − 3 = 5. An 8-dimensional su(3) acts by isometries of any SU(3)-invariant metric, so the isometry dimension is at least 8. The isotropy algebra so(3) is not recorded as holonomy. The coset is not forced.",
        "",
        "C2. Manifold dimension 8 − 3 = 5. The round isometry algebra is so(6), dimension 15. su(3) injects into so(6), so an 8-dimensional su(3) acts by isometries and is not the full algebra. Holonomy of the round metric is SO(5), dimension 10. The sphere is not forced.",
        "",
        "C3. Manifold dimension 1 + 4 = 5. No metric on M^4 is locked, so no isometry algebra and no holonomy are forced, and su(3) does not act. Σ^5 is a compact factor, so this noncompact product is refused.",
        "",
        "No continuous group on Σ^5 is forced with extras = 0. The three zero modes do not carry a group action. Their SU(2) dimensions are 2, 3, and 4. A count of 3 is not an SU(3) triplet.",
        "",
        "su(3) acts on the locked Σ^5: no.",
        "",
        "Moved: " + (", ".join(moved) if moved else "none") + ".",
        f"Rows changed: {len(moved)}.",
        "No candidate group equals an isometry atom, and no form was introduced.",
        "",
        "SIGMA5 SCORED — NO COSET SELECTED — NOTHING PROMOTED",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
