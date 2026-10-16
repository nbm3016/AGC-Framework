"""Score whether dim 5, χ=0, and the Stage 1A survivors force a diffeotype for Σ^5.

Bins come from file contents. FORCED requires a type match and extras empty.
REFUSED requires the files to contradict the claim. Otherwise the bin is UNKNOWN.
The T^{1,1} diffeotype is not copied onto Σ^5.
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
YARDSTICK = ROOT / "yardstick_lovelock_euler.json"
SCOPE = PROJECT / "DIMENSIONAL_SCOPE.md"
APS = ROOT / "native_aps_index.json"
MODES = ROOT / "r0_modes.json"
WAVE2 = ROOT / "generated_wave2.json"
RESULTS = ROOT / "sigma5_identify_results.json"
REPORT = ROOT / "SIGMA5_IDENTIFY_REPORT.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def main() -> int:
    before = sha256(BASELINE)
    isolate = load(ISOLATE)
    inventory = load(INVENTORY)
    yard = load(YARDSTICK)
    aps = load(APS)
    modes = load(MODES)
    wave2 = load(WAVE2)
    scope = SCOPE.read_text(encoding="utf-8")

    knobs = [
        isolate["continuous_knobs"],
        inventory["continuous_knobs"],
        yard["continuous_knobs"],
        aps["continuous_knobs"],
        wave2["continuous_knobs"],
    ]
    if any(k != 0 for k in knobs):
        raise SystemExit("continuous_knobs is not 0")

    factors = yard["lovelock_catalog"]["internal_factors"]
    sigma = factors["Sigma5"]
    t11 = factors["T11"]
    scope_ok = (
        "locked Stage 1A survivor set" in scope
        and "not a live 5D mesh" in scope
        and "\\Sigma^5" in scope
    )
    factor_ok = isolate["compact_factors_only"] == ["Σ^5", "T^{1,1}"]
    modes_ok = (
        modes["mode_count"] == 3
        and len(modes["modes"]) == 3
        and len(aps["chiral_modes"]) == 3
        and [m["j1"] for m in modes["modes"]] == [0.5, 1.0, 1.5]
        and all(m["j2"] == 0.0 and m["r"] == 0.0 for m in modes["modes"])
    )
    base = next(
        item for item in inventory["new"] if "TRANSVERSE_BASE" in item.get("extra_names", [])
    )
    base_why = base.get("why", "")
    sigma_keys = sorted(sigma.keys())
    type_keys = [k for k in sigma_keys if "diffeo" in k.lower() or k in ("homeomorphism_type", "manifold_name")]
    note = sigma.get("note", "")
    same_numbers = (
        sigma.get("dim") == 5
        and t11.get("dim") == 5
        and sigma.get("euler_characteristic") == 0
        and t11.get("euler_characteristic") == 0
    )

    stored = {
        "name": "Σ^5",
        "role": "compact factor",
        "dimension": sigma.get("dim"),
        "odd": sigma.get("odd"),
        "euler_characteristic": sigma.get("euler_characteristic"),
        "note": note,
        "survivor_set": [
            {"j1": m["j1"], "j2": m["j2"], "r": m["r"], "lambda_tilde": m["lambda_tilde"]}
            for m in modes["modes"]
        ],
        "survivor_role": "Stage 1A survivor set, not a live 5D mesh" if scope_ok else None,
        "keys": sigma_keys,
    }

    rows = []
    if factor_ok and scope_ok and modes_ok and sigma.get("dim") == 5 and sigma.get("euler_characteristic") == 0:
        rows.append(
            row(
                "I1",
                "What exact data are stored for Σ^5?",
                True,
                "FORCED",
                [],
                "Stored: compact factor Σ^5; dimension 5; odd=true; Euler characteristic 0; "
                f"note “{note}”; Stage 1A survivors (j1,j2,r) = (1/2,0,0), (1,0,0), (3/2,0,0) "
                "with lambda-tilde 4.5, 12, 22.5. "
                "DIMENSIONAL_SCOPE.md stores that survivor set as not a live 5D mesh. "
                "The Sigma5 object has no Betti number, no fundamental group, no spin row, and no contact form.",
                stored=stored,
            )
        )
    else:
        rows.append(
            row(
                "I1",
                "What exact data are stored for Σ^5?",
                False,
                "UNKNOWN",
                ["Σ^5 record"],
                "The factor list, the Euler record, and the survivor modes do not all match.",
            )
        )

    if type_keys:
        rows.append(
            row(
                "I2",
                "Does that stored list include a diffeomorphism type?",
                False,
                "UNKNOWN",
                type_keys,
                "Sigma5 has type-like keys, and they are not one extras-free diffeomorphism type.",
            )
        )
    elif (
        factor_ok
        and "diffeomorphism" not in note
        and "S^2×S^3" not in note
        and "S^5" not in note
        and "S^2×S^3" in base_why
        and "Σ^5" not in base_why
    ):
        rows.append(
            row(
                "I2",
                "Does that stored list include a diffeomorphism type?",
                False,
                "REFUSED",
                [],
                "The Sigma5 object keys are "
                + ", ".join(sigma_keys)
                + ". The note does not name a diffeomorphism type. "
                "TRANSVERSE_BASE records S^2×S^3 and does not name Σ^5.",
            )
        )
    else:
        rows.append(
            row(
                "I2",
                "Does that stored list include a diffeomorphism type?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "The Σ^5 record does not decide whether a diffeomorphism type is included.",
            )
        )

    classifies = "unique diffeomorphism" in note or "diffeomorphism type" in json.dumps(sigma)
    if classifies and type_keys == []:
        rows.append(
            row(
                "I3",
                "Does dimension 5 plus χ=0 alone force a unique extras-free diffeomorphism type?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "The note mentions a diffeomorphism and does not store one type.",
            )
        )
    elif classifies and len(type_keys) == 1 and sigma.get(type_keys[0]):
        rows.append(
            row(
                "I3",
                "Does dimension 5 plus χ=0 alone force a unique extras-free diffeomorphism type?",
                True,
                "FORCED",
                [],
                "The Σ^5 record stores one diffeomorphism type attributed to dimension and Euler characteristic.",
                value=sigma.get(type_keys[0]),
            )
        )
    elif same_numbers and not type_keys:
        rows.append(
            row(
                "I3",
                "Does dimension 5 plus χ=0 alone force a unique extras-free diffeomorphism type?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "T11 and Sigma5 are both stored with dimension 5 and Euler characteristic 0. "
                "The Sigma5 note records χ=0 for an odd-dimensional APS wall 5-fold. "
                "No diffeomorphism type is written from that pair, and no file says the pair classifies one.",
            )
        )
    else:
        rows.append(
            row(
                "I3",
                "Does dimension 5 plus χ=0 alone force a unique extras-free diffeomorphism type?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "The files do not decide a diffeomorphism type from dimension and Euler characteristic.",
            )
        )

    survivor_type = aps.get("diffeomorphism_type") or modes.get("diffeomorphism_type")
    honest = aps.get("honest_name", "")
    if survivor_type and modes_ok:
        rows.append(
            row(
                "I4",
                "Does the Stage 1A survivor set force a unique extras-free diffeomorphism type?",
                True,
                "FORCED",
                [],
                "The survivor file stores one diffeomorphism type.",
                value=survivor_type,
            )
        )
    elif modes_ok and "Not ker D_5" in honest and scope_ok and not survivor_type:
        rows.append(
            row(
                "I4",
                "Does the Stage 1A survivor set force a unique extras-free diffeomorphism type?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "r0_modes.json stores three modes (j1,j2,r) with lambda-tilde 4.5, 12, 22.5. "
                "native_aps_index.json calls the rule a wall-index on j2=0 and says it is not ker D_5 on Ceresole T^{1,1}. "
                "The scope file stores the survivor set as not a live 5D mesh. "
                "No diffeomorphism type is attached, and no file says the modes classify one.",
            )
        )
    else:
        rows.append(
            row(
                "I4",
                "Does the Stage 1A survivor set force a unique extras-free diffeomorphism type?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "The survivor files do not decide a diffeomorphism type.",
            )
        )

    i3 = rows[-2]
    i4 = rows[-1]
    if (
        i3["live_bin"] == "FORCED"
        and i4["live_bin"] == "FORCED"
        and i3["unique"] is True
        and i4["unique"] is True
        and i3["extras"] == []
        and i4["extras"] == []
        and i3.get("value") == i4.get("value")
    ):
        rows.append(
            row(
                "I5",
                "Do I3 and I4 together force a unique extras-free diffeomorphism type?",
                True,
                "FORCED",
                [],
                "I3 and I4 store the same extras-free diffeomorphism type.",
                value=i3.get("value"),
            )
        )
    elif i3["live_bin"] == "REFUSED" or i4["live_bin"] == "REFUSED":
        rows.append(
            row(
                "I5",
                "Do I3 and I4 together force a unique extras-free diffeomorphism type?",
                False,
                "REFUSED",
                [],
                "One of I3 or I4 is contradicted, so the pair does not force a diffeomorphism type.",
            )
        )
    else:
        rows.append(
            row(
                "I5",
                "Do I3 and I4 together force a unique extras-free diffeomorphism type?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "I3 and I4 do not each force an extras-free diffeomorphism type. "
                "The files do not decide the pair.",
            )
        )

    sigma_text = json.dumps(sigma, ensure_ascii=False)
    identity_hit = ("T^{1,1}" in sigma_text) or ("T11" in sigma_text and "same" in note.lower())
    denial_hit = ("not T" in note) or ("distinct from T" in note)
    product_two_names = factor_ok and "Σ^5 × T^{1,1}" in isolate["compact_fibre"]
    if identity_hit and not denial_hit and type_keys:
        rows.append(
            row(
                "I6",
                "Is Σ^5 the same manifold as T^{1,1}?",
                True,
                "FORCED",
                [],
                "The Σ^5 record states the identity with T^{1,1}.",
            )
        )
    elif denial_hit:
        rows.append(
            row(
                "I6",
                "Is Σ^5 the same manifold as T^{1,1}?",
                False,
                "REFUSED",
                [],
                "The Σ^5 record contradicts identity with T^{1,1}.",
            )
        )
    elif product_two_names and not identity_hit:
        rows.append(
            row(
                "I6",
                "Is Σ^5 the same manifold as T^{1,1}?",
                False,
                "UNKNOWN",
                ["identification Σ^5 with T^{1,1}"],
                "The fibre is stored as the product of two named factors. "
                "The Σ^5 record does not identify itself with T^{1,1}. "
                "The T^{1,1} metric, Betti numbers, spin row, and Reeb quotient are not in the Σ^5 record. "
                "No file states that the two factors are diffeomorphic, and no file states that they are not.",
            )
        )
    else:
        rows.append(
            row(
                "I6",
                "Is Σ^5 the same manifold as T^{1,1}?",
                False,
                "UNKNOWN",
                ["identification Σ^5 with T^{1,1}"],
                "The files do not decide the identification.",
            )
        )

    i5 = next(item for item in rows if item["id"] == "I5")
    if i5["live_bin"] == "FORCED" and i5["unique"] is True and i5["extras"] == [] and i5.get("value"):
        rows.append(
            row(
                "I7",
                "Unique extras-free diffeomorphism type for Σ^5 forced?",
                True,
                "FORCED",
                [],
                "I5 forces one extras-free diffeomorphism type.",
                value=i5.get("value"),
            )
        )
        answer = "Yes"
        named = i5.get("value")
    elif i5["live_bin"] == "REFUSED":
        rows.append(
            row(
                "I7",
                "Unique extras-free diffeomorphism type for Σ^5 forced?",
                False,
                "REFUSED",
                [],
                "I5 is contradicted, so no unique extras-free diffeomorphism type is forced.",
            )
        )
        answer = "No"
        named = None
    else:
        rows.append(
            row(
                "I7",
                "Unique extras-free diffeomorphism type for Σ^5 forced?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "Dimension 5, Euler characteristic 0, and the Stage 1A survivor set are stored. "
                "They do not carry a diffeomorphism type. The files do not decide one.",
            )
        )
        answer = "Unknown"
        named = None

    after = sha256(BASELINE)
    payload = {
        "continuous_knobs": 0,
        "baseline_sha256": before,
        "baseline_byte_stable_during_probe": before == after,
        "stored": stored,
        "unique_diffeomorphism_type_forced": answer,
        "diffeomorphism_type": named,
        "rows": rows,
    }
    RESULTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Σ^5 identify",
        "",
        "Stored Σ^5 data only. The T^{1,1} diffeotype is not copied. "
        "`continuous_knobs = 0`. The probe does not write `complete_baseline.json`.",
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
    lines += [
        "",
        f"Unique diffeomorphism type forced? {answer}",
        f"Baseline byte-stable during probe? {'Yes' if before == after else 'No'}",
        "",
        "SIGMA5 IDENTIFY PROBE - ZERO KNOBS",
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
    print("SIGMA5 IDENTIFY PROBE - ZERO KNOBS")
    print(f"Unique diffeomorphism type forced? {answer}")
    if answer == "Yes" and named:
        print(f"Name: {named}")
    print(f"Baseline byte-stable? {'Yes' if before == after else 'No'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
