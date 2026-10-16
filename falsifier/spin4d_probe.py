#!/usr/bin/env python3
"""4D spin of the three wall zeros. Internal charge is not Lorentz."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
REPO = os.path.dirname(HERE)
CORE = os.path.join(REPO, "core")
BASELINE_PATH = os.path.join(HERE, "complete_baseline.json")


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
    modes = json.load(open(os.path.join(ROOT, "r0_modes.json"), encoding="utf-8"))["modes"]
    spin = json.load(open(os.path.join(ROOT, "spin_dirac.json"), encoding="utf-8"))
    native = open(os.path.join(ROOT, "native_aps_index.py"), encoding="utf-8").read()
    constitution = open(os.path.join(CORE, "CONSTITUTION.md"), encoding="utf-8").read()
    labels = [(float(m["j1"]), float(m["j2"]), float(m["r"]), float(m["lambda_tilde"])) for m in modes]
    if [round(j, 1) for j, _, _, _ in labels] != [0.5, 1.0, 1.5]:
        fail("mode labels moved")
    lorentz_id = "identifies SU(2)_1 with 4D Lorentz" in constitution
    field_named = any(word in native for word in ("5D scalar field", "5D Dirac field", "5D vector field"))
    denies_ker = "not a computation of ker D_5" in native
    five_triple_is_4d = bool(spin.get("algebra_is_M4"))
    masses = [m.get("mass_4d") for m in modes]
    common_mass = len(set(m[3] for m in labels)) == 1 and all(masses)
    rows = [
        {
            "id": "S1",
            "claim": "SU(2)_1 is 4D Lorentz",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["lorentz_identification"],
            "why": "No file identifies SU(2)_1 with 4D Lorentz. The Road 1 catalog already records that absence.",
        },
        {
            "id": "S2",
            "claim": "the three labels are harmonics of D5 spinors",
            "unique": False,
            "live_bin": "REFUSED" if denies_ker else "UNKNOWN",
            "extras": ["field_type"],
            "why": "native_aps_index.py says the wall-index rule is not ker D_5. spin_dirac.json names Dirac(g5) on T^{1,1} and does not list these three labels as its harmonics.",
        },
        {
            "id": "S3",
            "claim": "the three labels are scalar harmonics",
            "unique": False,
            "live_bin": "UNKNOWN",
            "extras": ["field_type"],
            "why": "No file names the 5D field type of r0_modes as scalar.",
        },
        {
            "id": "S4",
            "claim": "each descends as a 4D Weyl",
            "unique": False,
            "live_bin": "UNKNOWN",
            "extras": ["lorentz_identification"],
            "why": "4D spin stays UNKNOWN. The 5-triple is not three 4D Weyls.",
        },
        {
            "id": "S5",
            "claim": "each descends as a 4D scalar",
            "unique": False,
            "live_bin": "UNKNOWN",
            "extras": ["lorentz_identification"],
            "why": "No descent to a 4D scalar is stored.",
        },
        {
            "id": "S6",
            "claim": "each descends as a 4D vector",
            "unique": False,
            "live_bin": "UNKNOWN",
            "extras": ["lorentz_identification"],
            "why": "No descent to a 4D vector is stored.",
        },
        {
            "id": "S7",
            "claim": "mixed: 1/2 Weyl, 1 vector, 3/2 RS",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["lorentz_identification"],
            "why": "That mix treats j1 as spacetime spin. No file makes that identification.",
        },
        {
            "id": "S8",
            "claim": "a common 4D mass scale is stored",
            "unique": False,
            "live_bin": "REFUSED",
            "extras": ["mass"],
            "why": f"Stored lambda-tilde values are {[m[3] for m in labels]}. They are not one scale, and no 4D mass is stored.",
        },
    ]
    if lorentz_id or field_named or five_triple_is_4d or common_mass:
        fail("a forbidden identification became true")
    if any(row["live_bin"] == "FORCED" for row in rows):
        fail("4D spin was forced")
    payload = {
        "banner": "4D SPIN PROBE - INTERNAL CHARGE != LORENTZ - ZERO KNOBS",
        "continuous_knobs": 0,
        "modes": [[a, b, c] for a, b, c, _ in labels],
        "rows": rows,
        "spin_4d_forced": False,
        "common_mass_forced": False,
        "su2_1_is_lorentz": False,
        "family_physics_reopened": False,
        "unique_color_promoted": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(os.path.join(HERE, "spin4d_probe.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    lines = [
        "# 4D spin probe",
        "",
        payload["banner"],
        "",
        "Internal SU(2)_1 charge is not 4D Lorentz spin.",
        "",
        "| id | claim | unique? | live_bin | extras | why |",
        "|----|-------|---------|----------|--------|-----|",
    ]
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['claim']} | {'Yes' if row['unique'] else 'No'} | {row['live_bin']} | "
            f"{', '.join(row['extras'])} | {row['why']} |"
        )
    lines += [
        "",
        "4D spin forced? No",
        "",
        "Common mass forced? No",
        "",
        "SU(2)_1 identified with Lorentz? No",
        "",
        "Family physics reopened? No",
        "",
        "unique_color promoted? No",
        "",
    ]
    with open(os.path.join(HERE, "SPIN4D_PROBE.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print("id | claim | unique? | live_bin | extras | why")
    for row in rows:
        print(
            f"{row['id']} | {row['claim']} | {'Yes' if row['unique'] else 'No'} | {row['live_bin']} | "
            f"{', '.join(row['extras'])} | {row['why']}"
        )
    print()
    print(payload["banner"])
    print("4D spin forced? No")
    print("Common mass forced? No")
    print("SU(2)_1 identified with Lorentz? No")
    print("Family physics reopened? No")
    print("unique_color promoted? No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
