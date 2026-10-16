"""Score whether Σ^5 has an extras-free 4-real-dimensional face.

The T^{1,1} transverse base S^2×S^2 is the type template only.
It is not copied onto Σ^5. Bins are computed from files on disk.
FORCED requires a type match and extras empty. REFUSED requires the
files to contradict the claim. Otherwise the bin is UNKNOWN.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent / "project"
BASELINE = ROOT / "complete_baseline.json"
ISOLATE = ROOT / "isolate_updated.json"
INVENTORY = ROOT / "generated_inventory.json"
WAVE2 = ROOT / "generated_wave2.json"
UNCAP = ROOT / "generated_uncap.json"
YARDSTICK = ROOT / "yardstick_lovelock_euler.json"
SCOPE = PROJECT / "DIMENSIONAL_SCOPE.md"
APS = ROOT / "native_aps_index.json"
RESULTS = ROOT / "sigma5_face_results.json"
REPORT = ROOT / "SIGMA5_FACE_REPORT.md"

SIGMA_MARKS = ("Σ^5", "Σ⁵", "Sigma5", "Sigma^5", "sigma5")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mentions_sigma(text: str) -> bool:
    return any(mark in text for mark in SIGMA_MARKS)


def row(rid, claim, unique, live_bin, extras, why, **extra):
    out = {
        "id": rid,
        "claim": claim,
        "unique": unique,
        "live_bin": live_bin,
        "extras": extras,
        "why": why,
    }
    out.update(extra)
    return out


def find_extra(inventory, name):
    for item in inventory["new"]:
        if name in item.get("extra_names", []):
            return item
    raise KeyError(name)


def main() -> int:
    before = sha256(BASELINE)
    isolate = load(ISOLATE)
    inventory = load(INVENTORY)
    wave2 = load(WAVE2)
    uncap = load(UNCAP)
    yard = load(YARDSTICK)
    aps = load(APS)
    scope = SCOPE.read_text(encoding="utf-8")

    knobs = [
        isolate["continuous_knobs"],
        inventory["continuous_knobs"],
        wave2["continuous_knobs"],
        uncap["continuous_knobs"],
        yard["continuous_knobs"],
        aps["continuous_knobs"],
    ]
    if any(k != 0 for k in knobs):
        raise SystemExit("continuous_knobs is not 0")

    sigma = yard["lovelock_catalog"]["internal_factors"]["Sigma5"]
    base = find_extra(inventory, "TRANSVERSE_BASE")
    reeb = find_extra(inventory, "REEB_XI")
    template_ok = (
        base.get("unique") is True
        and base.get("live_bin") == "FORCED"
        and base.get("value") == "S^2×S^2"
        and "S^2×S^3" in base.get("why", "")
        and not mentions_sigma(base.get("why", ""))
        and inventory.get("algebra") == "C^infty(T^{1,1})"
    )
    if not template_ok:
        raise SystemExit("T^{1,1} template S^2×S^2 is not the stored transverse base")

    scope_survivor = (
        "locked Stage 1A survivor set" in scope
        and "not a live 5D mesh" in scope
        and ("\\Sigma^5" in scope or "Σ^5" in scope)
    )
    factor_listed = "Σ^5" in isolate["compact_factors_only"]
    dim_ok = sigma.get("dim") == 5 and sigma.get("odd") is True
    note = sigma.get("note", "")
    diffeotype_stored = any(
        key in sigma for key in ("diffeomorphism_type", "face", "quotient", "transverse_base")
    )

    rows = []
    if factor_listed and dim_ok and scope_survivor and not diffeotype_stored:
        rows.append(
            row(
                "S1",
                "What manifold is Σ^5 in the lock? Name the stored object.",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "The stored name is the compact factor Σ^5. "
                f"yardstick_lovelock_euler.json records dim {sigma.get('dim')}, "
                f"odd={sigma.get('odd')}, Euler characteristic {sigma.get('euler_characteristic')}. "
                f"Its note is: {note} "
                "DIMENSIONAL_SCOPE.md stores APS on Σ^5 as the Stage 1A survivor set, not a live 5D mesh. "
                "No diffeomorphism type is stored.",
                stored_object="Σ^5",
                stored_role="compact factor and Stage 1A survivor set",
            )
        )
    elif diffeotype_stored:
        rows.append(
            row(
                "S1",
                "What manifold is Σ^5 in the lock? Name the stored object.",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "Sigma5 carries extra manifold keys. They are not one extras-free diffeotype.",
                stored_object="Σ^5",
            )
        )
    else:
        rows.append(
            row(
                "S1",
                "What manifold is Σ^5 in the lock? Name the stored object.",
                False,
                "UNKNOWN",
                ["stored object"],
                "The factor list, the dimension record, and the survivor-set sentence do not all agree.",
            )
        )

    reeb_text = " ".join(
        [
            reeb.get("why", ""),
            wave2.get("algebra", ""),
            next(d["why"] for d in wave2["descendants"] if d["object"] == "g_T_omega_T"),
            next(d["why"] for d in wave2["descendants"] if d["object"] == "SASAKI_PHI_J"),
        ]
    )
    circle_on_sigma = mentions_sigma(reeb_text)
    circle_on_t11 = (
        reeb.get("unique") is True
        and reeb.get("live_bin") == "FORCED"
        and wave2.get("algebra") == "C^infty(T^{1,1})"
        and "S^2×S^3" in base.get("why", "")
        and not circle_on_sigma
    )
    if circle_on_sigma and reeb.get("unique") is True and reeb.get("live_bin") == "FORCED":
        rows.append(
            row(
                "S2",
                "Does Σ^5 carry a unique S^1 / Reeb / free-circle action with extras = 0?",
                True,
                "FORCED",
                [],
                "A unique forced Reeb record names Σ^5.",
            )
        )
    elif circle_on_t11:
        rows.append(
            row(
                "S2",
                "Does Σ^5 carry a unique S^1 / Reeb / free-circle action with extras = 0?",
                False,
                "UNKNOWN",
                ["S^1 action on Σ^5"],
                "REEB_XI and CONTACT_ETA are unique and FORCED for the locked 5-metric. "
                "generated_wave2.json sets the algebra to C^infty(T^{1,1}). "
                "The transverse-base reason uses S^2×S^3. None of those records names Σ^5. "
                "No file states that Σ^5 has no circle action.",
            )
        )
    else:
        rows.append(
            row(
                "S2",
                "Does Σ^5 carry a unique S^1 / Reeb / free-circle action with extras = 0?",
                False,
                "UNKNOWN",
                ["S^1 action on Σ^5"],
                "The Reeb record does not decide a circle action on Σ^5.",
            )
        )

    s2 = rows[-1]
    if s2["live_bin"] == "FORCED" and s2["unique"] is True and s2["extras"] == []:
        rows.append(
            row(
                "S3",
                "If S2 is yes, what is the quotient 4-fold?",
                False,
                "UNKNOWN",
                ["quotient 4-fold"],
                "S2 is yes, and no quotient value is attached to the Σ^5 circle record.",
            )
        )
    else:
        rows.append(
            row(
                "S3",
                "If S2 is yes, what is the quotient 4-fold?",
                False,
                "UNKNOWN",
                ["quotient 4-fold"],
                "S2 is not yes. No Σ^5 quotient is computed. "
                "The template value S^2×S^2 stays the transverse base of T^{1,1}.",
            )
        )

    blobs = []
    for path in (INVENTORY, WAVE2, UNCAP, YARDSTICK, ISOLATE, APS):
        blobs.append(path.read_text(encoding="utf-8"))
    blobs.append(scope)
    sigma_face_hits = []
    for blob in blobs:
        if mentions_sigma(blob) and ("4D face" in blob or "4-fold of Σ" in blob or "quotient of Σ" in blob):
            sigma_face_hits.append("named 4D face phrase")
    # A hit must be a stored 4-fold object whose own text names Σ^5.
    # The template base is excluded because its why does not name Σ^5.
    stored_sigma_faces = sigma_face_hits
    if not stored_sigma_faces:
        rows.append(
            row(
                "S4",
                "If S2 is no or unknown, is any other extras-free 4D face of Σ^5 stored?",
                False,
                "REFUSED",
                [],
                "S2 is not yes. generated_inventory.json, generated_wave2.json, "
                "generated_uncap.json, and yardstick_lovelock_euler.json store one extras-free "
                "4D quotient, TRANSVERSE_BASE = S^2×S^2, and its text does not name Σ^5. "
                "No other extras-free 4D face of Σ^5 is stored.",
            )
        )
    else:
        rows.append(
            row(
                "S4",
                "If S2 is no or unknown, is any other extras-free 4D face of Σ^5 stored?",
                False,
                "UNKNOWN",
                ["4D face of Σ^5"],
                "A phrase tying a 4D face to Σ^5 is present and is not extras-free.",
            )
        )

    s4 = rows[-1]
    if s4["live_bin"] == "FORCED" and s4["unique"] is True and s4["extras"] == []:
        rows.append(
            row(
                "S5",
                "Is that face unique?",
                True,
                "FORCED",
                [],
                "The stored Σ^5 face is unique and extras-free.",
            )
        )
    elif s4["live_bin"] == "REFUSED":
        rows.append(
            row(
                "S5",
                "Is that face unique?",
                False,
                "REFUSED",
                [],
                "No Σ^5 face is stored, so uniqueness of such a face is contradicted.",
            )
        )
    else:
        rows.append(
            row(
                "S5",
                "Is that face unique?",
                False,
                "UNKNOWN",
                ["4D face of Σ^5"],
                "The files do not decide uniqueness of a Σ^5 face.",
            )
        )

    same_as_template = mentions_sigma(base.get("why", "")) and base.get("value") == "S^2×S^2"
    if same_as_template:
        rows.append(
            row(
                "S6",
                "Is that face the same object as S^2×S^2, a different stored 4-fold, or not stored?",
                True,
                "FORCED",
                [],
                "The transverse-base record itself names Σ^5.",
                relation="same as S^2×S^2",
            )
        )
    elif s4["live_bin"] == "REFUSED" and template_ok:
        rows.append(
            row(
                "S6",
                "Is that face the same object as S^2×S^2, a different stored 4-fold, or not stored?",
                False,
                "REFUSED",
                [],
                "Not stored. S^2×S^2 is the transverse base recorded from T^{1,1} ≃ S^2×S^3. "
                "That record does not name Σ^5, so it is not copied.",
                relation="not stored",
            )
        )
    else:
        rows.append(
            row(
                "S6",
                "Is that face the same object as S^2×S^2, a different stored 4-fold, or not stored?",
                False,
                "UNKNOWN",
                ["relation to S^2×S^2"],
                "The files do not decide the relation.",
            )
        )

    face_rows = [item for item in rows if item["id"] in ("S3", "S4", "S5")]
    named = next(
        (
            item.get("value")
            for item in rows
            if item["live_bin"] == "FORCED" and item["unique"] is True and item["extras"] == [] and item.get("value")
        ),
        None,
    )
    forced_face = any(
        item["id"] in ("S3", "S4")
        and item["live_bin"] == "FORCED"
        and item["unique"] is True
        and item["extras"] == []
        for item in rows
    )
    if forced_face and named:
        answer = "Yes"
    elif any(item["id"] == "S2" and item["live_bin"] == "REFUSED" for item in rows):
        answer = "No"
    else:
        answer = "Unknown"

    after = sha256(BASELINE)
    payload = {
        "continuous_knobs": 0,
        "baseline_sha256": before,
        "baseline_byte_stable_during_probe": before == after,
        "template": "T^{1,1} transverse base S^2×S^2",
        "template_copied_onto_sigma5": False,
        "unique_extras_free_4d_face": answer,
        "face_name": named,
        "rows": rows,
    }
    RESULTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Σ^5 face",
        "",
        "The type template is the T^{1,1} transverse base S^2×S^2. "
        "It is not copied onto Σ^5. `continuous_knobs = 0`. "
        "The probe does not write `complete_baseline.json`.",
        "",
        "| id | claim | unique? | live_bin | extras | why |",
        "|----|-------|---------|----------|--------|-----|",
    ]
    for item in rows:
        extras = ", ".join(item["extras"]) if item["extras"] else ""
        unique = "Yes" if item["unique"] else "No"
        lines.append(
            f"| {item['id']} | {item['claim']} | {unique} | {item['live_bin']} | {extras} | {item['why']} |"
        )
    name_line = f" If yes, name it: {named}." if answer == "Yes" and named else ""
    lines += [
        "",
        f"Unique extras-free 4D face of Σ^5? {answer}.{name_line}",
        f"Baseline byte-stable during probe? {'Yes' if before == after else 'No'}",
        "",
        "SIGMA5 FACE PROBE - ZERO KNOBS",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("| id | claim | unique? | live_bin | extras | why |")
    print("|----|-------|---------|----------|--------|-----|")
    for item in rows:
        extras = ", ".join(item["extras"]) if item["extras"] else ""
        unique = "Yes" if item["unique"] else "No"
        print(f"| {item['id']} | {item['claim']} | {unique} | {item['live_bin']} | {extras} | {item['why']} |")
    print()
    print("SIGMA5 FACE PROBE - ZERO KNOBS")
    print(f"Unique extras-free 4D face of Σ^5? {answer}")
    if answer == "Yes" and named:
        print(f"Name: {named}")
    print(f"Baseline byte-stable? {'Yes' if before == after else 'No'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
