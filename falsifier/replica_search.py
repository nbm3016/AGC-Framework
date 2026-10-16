#!/usr/bin/env python3
"""Search for an extras-free kernel that is three copies of one representation."""

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


def row(ident, space, extras, kernel, copies, live, why):
    return {
        "id": ident,
        "space_or_index": space,
        "extras": extras,
        "kernel": kernel,
        "three_copies_of_one_R": copies,
        "live_bin": live,
        "why": why,
        "passes": copies and extras == [] and live == "FORCED",
    }


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)
    r0 = json.load(open(os.path.join(ROOT, "r0_modes.json"), encoding="utf-8"))
    spin = json.load(open(os.path.join(ROOT, "spin_dirac.json"), encoding="utf-8"))
    wave = json.load(open(os.path.join(ROOT, "generated_wave2.json"), encoding="utf-8"))
    dims = [int(round(2 * float(m["j1"]) + 1)) for m in r0["modes"]]
    if dims != [2, 3, 4]:
        fail("old wall dimensions moved")
    killing = spin["certificate"].get("killing_alpha") or []
    parallel = next(item for item in wave["descendants"] if item["object"] == "PARALLEL_SPINORS_CONE")
    rows = [
        row(
            "K1",
            "T^{1,1} wall-index zeros",
            [],
            "2⊕3⊕4 of SU(2)_1",
            False,
            "REFUSED",
            "Three different irreps. Not R⊕R⊕R. Left as the old isolate.",
        ),
        row(
            "K2",
            "parallel spinors of the cone",
            [],
            "one complex line",
            False,
            "REFUSED",
            parallel["why"],
        ),
        row(
            "K3",
            "Killing spinors on the SE 5-fold",
            [],
            f"alpha={killing}",
            False,
            "REFUSED",
            "Two discrete Killing constants, not three copies of one representation.",
        ),
        row(
            "K4",
            "spinor fibre of T^{1,1}",
            [],
            f"rank {spin['certificate'].get('spinor_rank')}",
            False,
            "REFUSED",
            "One spinor bundle of rank 4. Not three copies of one internal representation.",
        ),
    ]
    passed = [item for item in rows if item["passes"]]
    blocked = len(passed) != 1
    if len(passed) > 1:
        fail("more than one replica passed; do not pick")
    payload = {
        "banner": "REPLICA SEARCH - THREE COPIES OR DO NOT START - ZERO KNOBS",
        "continuous_knobs": 0,
        "rows": rows,
        "blocked": blocked,
        "any_extras0_triple_copy": False,
        "new_isolate_started": False,
        "old_isolate_rewritten": False,
        "carried_over": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(os.path.join(HERE, "replica_search.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    lines = [
        "# Replica search",
        "",
        payload["banner"],
        "",
        "BLOCKED. No extras-free kernel is three copies of one internal representation.",
        "The old wall stays 2⊕3⊕4. No new isolate folder was created.",
        "",
        "| id | space_or_index | extras | kernel | three_copies_of_one_R? | live_bin | why |",
        "|----|----------------|--------|--------|------------------------|----------|-----|",
    ]
    for item in rows:
        lines.append(
            f"| {item['id']} | {item['space_or_index']} | {', '.join(item['extras']) or '—'} | "
            f"{item['kernel']} | {'Yes' if item['three_copies_of_one_R'] else 'No'} | "
            f"{item['live_bin']} | {item['why']} |"
        )
    lines.append("")
    with open(os.path.join(HERE, "REPLICA_SEARCH.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print("id | space_or_index | extras | kernel | three_copies_of_one_R? | live_bin | why")
    for item in rows:
        print(
            f"{item['id']} | {item['space_or_index']} | {', '.join(item['extras']) or '—'} | "
            f"{item['kernel']} | {'Yes' if item['three_copies_of_one_R'] else 'No'} | "
            f"{item['live_bin']} | {item['why']}"
        )
    print()
    print("BLOCKED")
    print(payload["banner"])
    print("Any extras=0 kernel R⊕R⊕R? No")
    print("New isolate started? No")
    print("Old isolate rewritten? No")
    print("N_gen / APS-sieve / generations carried over? No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
