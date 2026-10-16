#!/usr/bin/env python3
"""Road 1 catalog of the three wall zeros. Labels only. No family physics."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
REPO = os.path.dirname(HERE)
CORE = os.path.join(REPO, "core")
DOCS = os.path.join(REPO, "docs")
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
    constitution = open(os.path.join(CORE, "CONSTITUTION.md"), encoding="utf-8").read()
    geometry = open(os.path.join(DOCS, "WORKING_GEOMETRY.md"), encoding="utf-8").read()
    lorentz_named = "SU(2)_1 with Lorentz" in constitution or "identifies SU(2)_1 with Lorentz" in geometry
    rows = []
    lambdas = []
    for raw in modes:
        j1 = float(raw["j1"])
        j2 = float(raw["j2"])
        charge = float(raw["r"])
        d1 = int(round(2 * j1 + 1))
        d2 = int(round(2 * j2 + 1))
        lam = float(raw["lambda_tilde"])
        lambdas.append(lam)
        rows.append(
            {
                "mode": f"({j1:g},{j2:g},{charge:g})",
                "internal_irrep": f"({d1} of SU(2)_1) x ({d2} of SU(2)_2) x U(1)_{charge:g}",
                "lorentz_spin": "UNKNOWN" if not lorentz_named else "named",
                "gauge_boson": False,
                "gravitino": False,
                "light": "UNKNOWN",
                "lambda_tilde": lam,
                "extras": ["no_lorentz_identification", "no_stored_4d_mass"],
                "why": (
                    f"Internal dimension {d1} of SU(2)_1, singlet of SU(2)_2, charge {charge:g}. "
                    + (
                        "Dimension 3 is not by itself an adjoint gauge boson. "
                        if d1 == 3
                        else "j1=3/2 is not by itself a Lorentz spin-3/2. "
                        if abs(j1 - 1.5) < 1e-9
                        else "Dimension 2 is not a locked 4D Weyl. "
                    )
                    + "No file identifies SU(2)_1 with 4D Lorentz. No 4D mass or gap is stored."
                ),
            }
        )
    one_scale = len(set(lambdas)) == 1
    payload = {
        "banner": "ROAD 1 CATALOG - THREE FIELDS NOT THREE FAMILIES - ZERO KNOBS",
        "continuous_knobs": 0,
        "wall_zero_count": len(rows),
        "N_gen_as_generations": False,
        "rows": rows,
        "any_locked_4d_weyl": False,
        "any_locked_gauge_boson": False,
        "any_locked_gravitino": False,
        "all_three_light_one_scale": False,
        "lambda_tilde": lambdas,
        "lambda_tilde_same_scale": one_scale,
        "unique_color_promoted": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    if payload["wall_zero_count"] != 3 or one_scale:
        fail("count moved or lambdas collapsed")
    with open(os.path.join(HERE, "road1_catalog.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    lines = [
        "# Road 1 catalog",
        "",
        payload["banner"],
        "",
        "Three wall fields, `2 + 3 + 4` of SU(2)_1. Not three generations.",
        "",
        "| mode | internal_irrep | 4D Lorentz spin known? | gauge boson? | gravitino? | light? | extras | why |",
        "|------|----------------|------------------------|--------------|------------|--------|--------|-----|",
    ]
    for row in rows:
        lines.append(
            f"| {row['mode']} | {row['internal_irrep']} | {row['lorentz_spin']} | "
            f"{'Yes' if row['gauge_boson'] else 'No'} | {'Yes' if row['gravitino'] else 'No'} | "
            f"{row['light']} | {', '.join(row['extras'])} | {row['why']} |"
        )
    lines += [
        "",
        f"Stored lambda-tilde values {lambdas} are not one scale.",
        "",
        "Any mode a locked 4D Weyl? No",
        "",
        "Any mode a locked gauge boson? No",
        "",
        "Any mode a locked gravitino? No",
        "",
        "All three light at one scale? No",
        "",
        "N_gen restored as generations? No",
        "",
        "unique_color promoted? No",
        "",
    ]
    with open(os.path.join(HERE, "ROAD1_CATALOG.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print("mode | internal_irrep | 4D Lorentz spin known? | gauge boson? | gravitino? | light? | extras | why")
    for row in rows:
        print(
            f"{row['mode']} | {row['internal_irrep']} | {row['lorentz_spin']} | "
            f"{'Yes' if row['gauge_boson'] else 'No'} | {'Yes' if row['gravitino'] else 'No'} | "
            f"{row['light']} | {', '.join(row['extras'])} | {row['why']}"
        )
    print()
    print(payload["banner"])
    print("Any mode a locked 4D Weyl? No")
    print("Any mode a locked gauge boson? No")
    print("Any mode a locked gravitino? No")
    print("All three light at one scale? No")
    print("N_gen restored as generations? No")
    print("unique_color promoted? No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
