#!/usr/bin/env python3
"""Named projections on the three wall-index zeros. One road only."""

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


def spin_name(j1: float) -> str:
    if abs(j1 - 0.5) < 1e-9:
        return "Weyl"
    if abs(j1 - 1.0) < 1e-9:
        return "vector"
    if abs(j1 - 1.5) < 1e-9:
        return "Rarita-Schwinger"
    return "unlisted"


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)
    r0 = json.load(open(os.path.join(ROOT, "r0_modes.json"), encoding="utf-8"))
    native = json.load(open(os.path.join(ROOT, "native_aps_index.json"), encoding="utf-8"))
    modes = []
    for raw in r0["modes"]:
        j1 = float(raw["j1"])
        dim = int(round(2 * j1 + 1))
        modes.append(
            {
                "j1": j1,
                "j2": float(raw["j2"]),
                "r": float(raw["r"]),
                "dim_su2_1": dim,
                "spin_if_j1_is_spacetime": spin_name(j1),
                "index": int(raw["index"]),
                "aps_neutral": bool(raw["aps_neutral"]),
            }
        )
    chiral = {
        (float(m["j1"]), float(m["j2"]), float(m["r"])): m.get("chirality")
        for m in native.get("chiral_modes", [])
    }
    print("mode | j1 | j2 | r | dim SU(2)_1 = 2j1+1 | 4D spin if j1 is spacetime spin | same_rep?")
    spins = [m["spin_if_j1_is_spacetime"] for m in modes]
    same = len(set(spins)) == 1
    for i, m in enumerate(modes, 1):
        print(
            f"{i} | {m['j1']} | {m['j2']} | {m['r']} | {m['dim_su2_1']} | "
            f"{m['spin_if_j1_is_spacetime']} | {'Yes' if same else 'No'}"
        )

    # Named projections already in the files. No projector that drops j1.
    kept = []
    for m in modes:
        key = (m["j1"], m["j2"], m["r"])
        chir = chiral.get(key)
        star = abs(m["j2"]) < 1e-12
        neutral = m["index"] == 0 and m["aps_neutral"]
        r_zero = abs(m["r"]) < 1e-12
        plus = chir == "+"
        if star and neutral and r_zero and plus:
            kept.append(m)
    leftovers = sorted({m["j1"] for m in kept})
    differ = len(leftovers) > 1
    road = 1 if differ else 2
    catalog = []
    if road == 1:
        for m in kept:
            catalog.append(
                {
                    "j1": m["j1"],
                    "dim_su2_1": m["dim_su2_1"],
                    "four_d_spin": m["spin_if_j1_is_spacetime"],
                    "mass": "UNKNOWN",
                    "flavor": "off",
                }
            )
    payload = {
        "banner": "PROJECTION TEST - ROAD 1 OR ROAD 2 - ZERO KNOBS",
        "continuous_knobs": 0,
        "modes": modes,
        "same_4d_weyl_three_times": same and spins == ["Weyl", "Weyl", "Weyl"],
        "projections": ["j2=0", "index=0", "r=0", "chirality=+"],
        "leftover_j1": leftovers,
        "leftovers_still_differ": differ,
        "road": road,
        "wall_zero_count": len(kept) if road == 1 else None,
        "call_count_N_gen_in_new_locks": False,
        "catalog": catalog,
        "flavor_started": False,
        "unique_color_promoted": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    if road == 1 and payload["wall_zero_count"] != 3:
        fail("wall zero count moved")
    with open(os.path.join(HERE, "projection_test.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    lines = [
        "# Projection test",
        "",
        payload["banner"],
        "",
        "Named projections only: j2=0, index 0, r=0, chiral +.",
        "",
        f"Leftover j1 values: {leftovers}.",
        "",
        f"Road {road}.",
        "",
    ]
    if road == 1:
        lines.append("`wall_zero_count = 3`. New locks do not call that integer N_gen.")
        lines.append("")
        lines.append("| j1 | dim | 4D spin from the label | mass |")
        lines.append("|----|-----|------------------------|------|")
        for row in catalog:
            lines.append(
                f"| {row['j1']} | {row['dim_su2_1']} | {row['four_d_spin']} | {row['mass']} |"
            )
        lines.append("")
        lines.append("Flavor is off.")
    else:
        lines.append("Road 2 is eligible for a later anomalies probe. Anomalies are not started.")
    lines.append("")
    with open(os.path.join(HERE, "PROJECTION_TEST.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print()
    print(payload["banner"])
    print(f"Leftovers still differ? {'Yes' if differ else 'No'}")
    print(f"Road? {road}")
    print(f"Same 4D Weyl three times? {'Yes' if payload['same_4d_weyl_three_times'] else 'No'}")
    print("Call the count N_gen in new locks? No")
    print("Flavor started? No")
    print("unique_color promoted? No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
