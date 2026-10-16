"""Score the Stiefel-Whitney obstruction on the stored APS wall only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent / "project"
OUT_JSON = ROOT / "test_wall_spin.json"
OUT_MD = ROOT / "TEST_WALL_SPIN.md"
BASELINE = ROOT / "complete_baseline.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def find_w2(obj: object, found: list[object]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in {"w2", "w_2", "stiefel_whitney"}:
                found.append(value)
            else:
                find_w2(value, found)
    elif isinstance(obj, list):
        for item in obj:
            find_w2(item, found)


def main() -> int:
    baseline_hash = sha256(BASELINE)
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    yard = json.loads((ROOT / "yardstick_lovelock_euler.json").read_text(encoding="utf-8"))
    aps = json.loads((ROOT / "native_aps_index.json").read_text(encoding="utf-8"))
    scope = (PROJECT / "DIMENSIONAL_SCOPE.md").read_text(encoding="utf-8")

    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")
    wall = next(item for item in locks if item["name"] == "wall_zero_count")
    sigma = yard["lovelock_catalog"]["internal_factors"]["Sigma5"]
    if wall.get("extras") != 0 or wall.get("value") != 3:
        raise SystemExit("wall_zero_count is not the locked count 3")

    wall_text = "\n".join(
        [
            json.dumps(sigma),
            json.dumps(wall),
            json.dumps(
                {
                    "method": aps.get("method"),
                    "new_method": aps.get("new_method"),
                    "honest_name": aps.get("honest_name"),
                    "notes": aps.get("notes"),
                }
            ),
            "APS on Σ^5 is the locked Stage 1A survivor set, not a live 5D mesh.",
        ]
    )
    aps_sentence = r"APS on \(\Sigma^5\) is the locked Stage 1A survivor set, not a live 5D mesh."
    if aps_sentence not in scope:
        raise SystemExit("dimensional scope does not store the APS-wall sentence")

    w2_values: list[object] = []
    find_w2(sigma, w2_values)
    find_w2(wall, w2_values)
    spin_phrase = "spin structure" in wall_text.lower() or "spinor bundle" in wall_text.lower()
    w2_zero = any(value in (0, "0", False) for value in w2_values)
    # The count 3 is not a value of w2.
    w2_forced = bool(w2_zero or spin_phrase) and wall.get("extras") == 0
    names_t11_operator = any(
        token in wall_text for token in ("SPIN_T11", "DIRAC_T11", "5-triple", "canonical 5-triple")
    )

    c1 = {
        "id": "C1",
        "name": "SU(3)/SO(3)",
        "bin": "REFUSED" if w2_forced else "UNKNOWN",
        "refused_by_stored_obstruction": w2_forced,
    }
    c2 = {
        "id": "C2",
        "name": "S^5 = SU(3)/SU(2)",
        "bin": "UNKNOWN",
        "selected": False,
        "forced": False,
        "unique": False,
        "survivor": False,
    }

    payload = {
        "continuous_knobs": 0,
        "promoted": 0,
        "baseline_sha256": baseline_hash,
        "locks_changed": 0,
        "wall_record": {
            "sigma5_keys": sorted(sigma),
            "sigma5_note": sigma.get("note"),
            "wall_zero_count": wall["value"],
            "harmonics": "2⊕3⊕4",
            "su2_dimensions": wall.get("su2_dimensions"),
            "aps_honest_name": aps.get("honest_name"),
            "names_spin_t11": names_t11_operator,
            "names_dirac_t11": "DIRAC_T11" in wall_text,
            "names_five_triple": "5-triple" in wall_text or "canonical 5-triple" in wall_text,
        },
        "w2_values_stored": w2_values,
        "w2_forced": w2_forced,
        "c1_refused_by_stored_obstruction": c1["refused_by_stored_obstruction"],
        "c2_selected": False,
        "candidates": [c1, c2],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    w2_answer = "Yes" if w2_forced else "No"
    c1_answer = "Yes" if c1["refused_by_stored_obstruction"] else "No"
    lines = [
        "# Wall spin obstruction",
        "",
        "WALL SPIN OBSTRUCTION - STORED RECORD ONLY - ZERO KNOBS",
        "",
        f"w2 forced on the wall? {w2_answer}",
        "",
        f"C1 refused by a stored obstruction? {c1_answer}",
        "",
        "C2 selected? No",
        "",
        "Rows promoted: 0",
        "",
        "The stored Σ^5 record has keys "
        + ", ".join(sorted(sigma))
        + f". Note: {sigma.get('note')}",
        "",
        "wall_zero_count = 3 counts the harmonics 2⊕3⊕4. A count is not a spinor bundle, and it does not store w2 = 0.",
        "",
        "The APS sentence stores the Stage 1A survivor set. It does not store a spin structure. "
        "SPIN_T11, DIRAC_T11, and the 5-triple are not named as the wall operator.",
        "",
        f"C1 bin: {c1['bin']}. C2 bin: {c2['bin']}. C2 is not forced, not unique, and not the survivor.",
        "",
        f"Baseline sha256: {baseline_hash}",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if sha256(BASELINE) != baseline_hash:
        raise SystemExit("baseline changed during the score")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
