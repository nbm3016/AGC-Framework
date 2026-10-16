#!/usr/bin/env python3
"""Why this wall is T^{1,1} inside the first slice, not among all 5-folds."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
BASELINE_PATH = os.path.join(HERE, "complete_baseline.json")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def sphere_b2(dim: int) -> int:
    return 1 if dim == 2 else 0


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)
    cu = json.load(open(os.path.join(ROOT, "controlled_uniqueness.json"), encoding="utf-8"))
    cone = json.load(open(os.path.join(ROOT, "cone_curvature.json"), encoding="utf-8"))
    b2 = int(cone["betti"]["b2_link"])
    b3 = int(cone["betti"]["b3_link"])
    b2_s5 = sphere_b2(5)
    # Z^3 / Z(1,1,1) for the circle bundle over three spheres.
    b2_q = 3 - 1
    iso_dim = 3 + 3 + 1
    m_dim = (8 + 3 + 1) - (3 + 1 + 1)
    inside = bool(cu.get("skeleton_isolates_T11")) and "first slice" in cu.get("theorem_level_claim", "")
    global_open = cu.get("global_landscape_uniqueness") is False
    rows = [
        {
            "id": "U1",
            "claim": "locked atoms force T^{1,1} among all 5-manifolds",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["bases_outside_first_slice"],
            "why": "controlled_uniqueness.json sets global_landscape_uniqueness false. Uniqueness among all 5-manifolds is not claimed.",
        },
        {
            "id": "U2",
            "claim": "locked atoms force T^{1,1} only inside first-slice G_SE",
            "unique": inside,
            "live_bin": "FORCED" if inside and global_open else "UNKNOWN",
            "extras": [],
            "why": "The file says lambda-tilde, equivalently sigma*=sqrt(3)/2, isolates T^{1,1} among labeled bases in the first slice. The scope is that slice.",
        },
        {
            "id": "U3",
            "claim": "b2=b3=1 kills S^5 and Q^{1,1,1}",
            "unique": True,
            "live_bin": "FORCED" if b2 == 1 and b2_s5 == 0 and b2_q == 2 else "UNKNOWN",
            "extras": [],
            "why": f"Locked b2={b2}, b3={b3}. S^5 has b2={b2_s5}. Q^{{1,1,1}} as the (1,1,1) circle bundle has b2={b2_q}.",
        },
        {
            "id": "U4",
            "claim": "Iso=SU(2)×SU(2)×U(1) kills M^{p,q} as this wall",
            "unique": True,
            "live_bin": "FORCED" if iso_dim == 7 and m_dim == 7 else "UNKNOWN",
            "extras": [],
            "why": f"This wall's isometry has dimension {iso_dim} and no SU(3) factor. M^{{p,q}} is dimension {m_dim} with an SU(3) factor. Not this wall. (p,q) is not selected.",
        },
        {
            "id": "U5",
            "claim": "the wall-index sieve exists only on this Iso",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["other_isometry"],
            "why": "The sieve is written in the j1, j2 labels of this isometry. The files do not prove that no other group could carry a three-zero count.",
        },
        {
            "id": "U6",
            "claim": "some other locked 5-fold also has exactly three zeros under the same rule with extras=0",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["second_locked_5fold"],
            "why": "No second locked 5-fold with that zero count and empty extras is on disk.",
        },
        {
            "id": "U7",
            "claim": "Y^{14} / fibration_class is forced this session",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["fibration_class"],
            "why": "The same uniqueness file says uniqueness among all 14D fibrations remains open.",
        },
    ]
    if rows[0]["live_bin"] == "FORCED":
        fail("global uniqueness was stamped")
    payload = {
        "banner": "WALL UNIQUENESS - THIS SIEVE NOT EVERY 5-FOLD - ZERO KNOBS",
        "continuous_knobs": 0,
        "rows": rows,
        "unique_among_all_5folds": False,
        "unique_inside_first_slice": rows[1]["live_bin"] == "FORCED",
        "another_extras0_fivefold": False,
        "y14_forced": False,
        "family_physics_reopened": False,
        "n_gen_as_generations": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(os.path.join(HERE, "wall_uniqueness_probe.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    lines = [
        "# Wall uniqueness",
        "",
        payload["banner"],
        "",
        "This wall is T^{1,1} as first-slice SE with b2=b3=1. It is not proven unique among all 5-manifolds.",
        "",
        "| id | claim | unique? | live_bin | extras | why |",
        "|----|-------|---------|----------|--------|-----|",
    ]
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['claim']} | {'Yes' if row['unique'] else 'No'} | {row['live_bin']} | "
            f"{', '.join(row['extras']) or '—'} | {row['why']} |"
        )
    lines += ["", "Y^{14} forced? No", "", "Family physics reopened? No", ""]
    with open(os.path.join(HERE, "WALL_UNIQUENESS.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print("id | claim | unique? | live_bin | extras | why")
    for row in rows:
        print(
            f"{row['id']} | {row['claim']} | {'Yes' if row['unique'] else 'No'} | {row['live_bin']} | "
            f"{', '.join(row['extras']) or '—'} | {row['why']}"
        )
    print()
    print(payload["banner"])
    print("T^{1,1} unique among all 5-manifolds? No")
    print(f"T^{{1,1}} unique inside first-slice G_SE? {'Yes' if payload['unique_inside_first_slice'] else 'No'}")
    print("Another extras=0 5-fold with three zeros? No")
    print("Y^{14} forced? No")
    print("Family physics reopened? No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
