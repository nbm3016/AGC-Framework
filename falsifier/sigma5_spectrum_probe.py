"""Compare the Stage 1A survivor numbers with spectra already stored on disk.

No new spectrum is computed. FORCED requires a numerical match and extras
empty. REFUSED requires the files to contradict the claim. Otherwise UNKNOWN.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE = ROOT / "complete_baseline.json"
ISOLATE = ROOT / "isolate_updated.json"
INVENTORY = ROOT / "generated_inventory.json"
CORE = ROOT / "agc_core_baseline.json"
MODES = ROOT / "r0_modes.json"
APS = ROOT / "native_aps_index.json"
YARD = ROOT / "yardstick_lovelock_euler.json"
RESULTS = ROOT / "sigma5_spectrum_results.json"
REPORT = ROOT / "SIGMA5_SPECTRUM_REPORT.md"

TARGET = (Fraction(9, 2), Fraction(12, 1), Fraction(45, 2))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_fraction(value):
    if isinstance(value, str):
        if "/" in value:
            num, den = value.split("/", 1)
            return Fraction(int(num), int(den))
        return Fraction(value)
    return Fraction(str(value))


def as_tuple(values):
    return tuple(as_fraction(v) for v in values)


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
    core = load(CORE)
    modes = load(MODES)
    aps = load(APS)
    yard = load(YARD)

    knobs = [
        isolate["continuous_knobs"],
        inventory["continuous_knobs"],
        aps["continuous_knobs"],
        yard["continuous_knobs"],
    ]
    if any(k != 0 for k in knobs):
        raise SystemExit("continuous_knobs is not 0")

    lam = next(item for item in isolate["locks"] if item["name"] == "lambda_tilde")
    killing = next(item for item in isolate["locks"] if item["name"] == "D5_LABEL_FORMULA")
    d5 = next(
        item for item in inventory["new"] if "D5_SPECTRUM" in item.get("extra_names", [])
    )
    sigma = yard["lovelock_catalog"]["internal_factors"]["Sigma5"]
    appendix = core["latex_appendix"]
    stage_1a = appendix.split("Stage 1B")[0]
    survivor_modes = as_tuple(m["lambda_tilde"] for m in modes["modes"])
    survivor_aps = as_tuple(m["lambda_tilde_derived"] for m in aps["chiral_modes"])
    survivor_lock = as_tuple(lam["file_decimals"])
    survivor_exact = as_tuple(lam["value"])
    stage_names_sigma = "\\Sigma^5" in stage_1a and "spectral survivors" in stage_1a
    stage_has_target = "4.5" in stage_1a and "12.0" in stage_1a and "22.5" in stage_1a
    not_t11_dirac = "Not ker D_5 on Ceresole T^{1,1}" in aps.get("honest_name", "")
    killing_value = killing.get("value", "")
    killing_is_half = "-5/2" in killing_value and "+5/2" in killing_value
    killing_names_sigma = "Σ^5" in killing_value or "Sigma^5" in killing_value
    sigma_has_spectrum_key = any(
        "eigen" in key.lower() or "lambda" in key.lower() or "spectrum" in key.lower()
        for key in sigma.keys()
    )

    lists = [
        {
            "source": "r0_modes.json modes",
            "values": [str(v) for v in survivor_modes],
            "named_5fold": "Σ^5" if stage_names_sigma and stage_has_target else None,
        },
        {
            "source": "native_aps_index.json chiral_modes",
            "values": [str(v) for v in survivor_aps],
            "named_5fold": None,
            "denied_name": "T^{1,1}" if not_t11_dirac else None,
        },
        {
            "source": "isolate lambda_tilde",
            "values": [str(v) for v in survivor_exact],
            "named_5fold": None,
            "extras": lam.get("extras"),
        },
        {
            "source": "isolate D5_LABEL_FORMULA",
            "values": ["-5/2", "5/2"] if killing_is_half else [killing_value],
            "named_5fold": "Σ^5" if killing_names_sigma else None,
        },
        {
            "source": "generated_inventory D5_SPECTRUM",
            "values": [],
            "named_5fold": None,
            "live_bin": d5.get("live_bin"),
        },
    ]

    same_survivor = (
        survivor_modes == TARGET
        and survivor_aps == TARGET
        and survivor_lock == TARGET
        and survivor_exact == TARGET
        and lam.get("extras") == 0
    )

    rows = []
    if same_survivor and stage_names_sigma and stage_has_target and killing_is_half:
        rows.append(
            row(
                "M1",
                "What eigenvalue lists are stored, and for which named 5-folds?",
                True,
                "FORCED",
                [],
                "Stored lists: r0_modes, native_aps chiral modes, and isolate lambda_tilde "
                "all hold 9/2, 12, 45/2. The Stage 1A appendix heading names Σ^5 spectral survivors "
                "and stores that same set before the T^{1,1} subsection. "
                "D5_LABEL_FORMULA stores Killing eigenvalues -5/2 and +5/2 and does not name Σ^5. "
                "D5_SPECTRUM is stored with no eigenvalue list.",
                lists=lists,
            )
        )
    else:
        rows.append(
            row(
                "M1",
                "What eigenvalue lists are stored, and for which named 5-folds?",
                False,
                "UNKNOWN",
                ["eigenvalue list"],
                "The stored survivor numbers, the Stage 1A heading, and the Killing list do not all read cleanly.",
                lists=lists,
            )
        )

    if same_survivor:
        rows.append(
            row(
                "M2",
                "Is λ̃ = 4.5, 12, 22.5 one of those stored lists?",
                True,
                "FORCED",
                [],
                "9/2, 12, and 45/2 equal the stored survivor lists in r0_modes.json, "
                "native_aps_index.json, and the isolate lambda_tilde lock. That lock has extras 0. "
                "They do not equal the stored Killing pair -5/2, +5/2.",
            )
        )
    elif not same_survivor and (survivor_modes or survivor_aps or survivor_lock):
        rows.append(
            row(
                "M2",
                "Is λ̃ = 4.5, 12, 22.5 one of those stored lists?",
                False,
                "REFUSED",
                [],
                "Stored survivor numbers disagree with 9/2, 12, 45/2 or carry extras.",
            )
        )
    else:
        rows.append(
            row(
                "M2",
                "Is λ̃ = 4.5, 12, 22.5 one of those stored lists?",
                False,
                "UNKNOWN",
                ["eigenvalue list"],
                "No survivor list was stored to compare.",
            )
        )

    m2 = rows[-1]
    if (
        m2["live_bin"] == "FORCED"
        and stage_names_sigma
        and stage_has_target
        and not_t11_dirac
        and not killing_names_sigma
    ):
        rows.append(
            row(
                "M3",
                "If yes, which named 5-fold carries it, and is that name Σ^5?",
                True,
                "FORCED",
                [],
                "The Stage 1A appendix stores the set under the heading Σ^5 spectral survivors. "
                "native_aps_index.json says the rule is not ker D_5 on Ceresole T^{1,1}. "
                "The carrier name on that stored list is Σ^5.",
                named_5fold="Σ^5",
            )
        )
    elif m2["live_bin"] == "FORCED" and not stage_names_sigma:
        rows.append(
            row(
                "M3",
                "If yes, which named 5-fold carries it, and is that name Σ^5?",
                False,
                "UNKNOWN",
                ["named 5-fold"],
                "The numbers are stored, and the Stage 1A heading does not name Σ^5.",
            )
        )
    elif m2["live_bin"] == "REFUSED":
        rows.append(
            row(
                "M3",
                "If yes, which named 5-fold carries it, and is that name Σ^5?",
                False,
                "REFUSED",
                [],
                "M2 is contradicted, so no named 5-fold carries that list.",
            )
        )
    else:
        rows.append(
            row(
                "M3",
                "If yes, which named 5-fold carries it, and is that name Σ^5?",
                False,
                "UNKNOWN",
                ["named 5-fold"],
                "The files do not decide which named 5-fold carries the list.",
            )
        )

    m3 = rows[-1]
    diffeotype = sigma.get("diffeomorphism_type")
    if (
        m3["live_bin"] == "FORCED"
        and m3.get("named_5fold") == "Σ^5"
        and diffeotype
        and not sigma_has_spectrum_key
    ):
        rows.append(
            row(
                "M4",
                "Does the match force a diffeomorphism type with extras = 0?",
                True,
                "FORCED",
                [],
                "The Σ^5 record stores one diffeomorphism type beside the matched list.",
                value=diffeotype,
            )
        )
    elif m3["live_bin"] == "FORCED" and not diffeotype and "diffeomorphism" not in json.dumps(sigma):
        rows.append(
            row(
                "M4",
                "Does the match force a diffeomorphism type with extras = 0?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "The matched list is stored under the name Σ^5. "
                "The Sigma5 record keys do not include a diffeomorphism type. "
                "No file says the eigenvalue match forces one.",
            )
        )
    elif m3["live_bin"] == "REFUSED":
        rows.append(
            row(
                "M4",
                "Does the match force a diffeomorphism type with extras = 0?",
                False,
                "REFUSED",
                [],
                "There is no matched list, so the match does not force a diffeomorphism type.",
            )
        )
    else:
        rows.append(
            row(
                "M4",
                "Does the match force a diffeomorphism type with extras = 0?",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "The files do not decide a diffeomorphism type from the stored lists.",
            )
        )

    m1 = rows[0]
    lists_stored = m1["live_bin"] == "FORCED" and m2["live_bin"] == "FORCED"
    if lists_stored:
        rows.append(
            row(
                "M5",
                "If no list is stored to compare, leave the type unknown.",
                False,
                "REFUSED",
                [],
                "A survivor list is stored and matches 9/2, 12, 45/2. "
                "The premise that no list is stored is contradicted. "
                "The diffeomorphism type stays unknown because the Σ^5 record does not carry one.",
            )
        )
    elif m1["live_bin"] == "UNKNOWN" or m2["live_bin"] == "UNKNOWN":
        rows.append(
            row(
                "M5",
                "If no list is stored to compare, leave the type unknown.",
                False,
                "UNKNOWN",
                ["diffeomorphism type"],
                "No comparable spectrum is stored. The diffeomorphism type stays unknown.",
            )
        )
    else:
        rows.append(
            row(
                "M5",
                "If no list is stored to compare, leave the type unknown.",
                False,
                "UNKNOWN",
                ["eigenvalue list"],
                "The files do not decide whether a comparable list is stored.",
            )
        )

    matched = m2["live_bin"] == "FORCED" and m3["live_bin"] == "FORCED" and m3["extras"] == []
    if matched and m3.get("named_5fold"):
        answer = "Yes"
        named = m3["named_5fold"]
    elif m2["live_bin"] == "REFUSED" or m3["live_bin"] == "REFUSED":
        answer = "No"
        named = None
    else:
        answer = "Unknown"
        named = None

    after = sha256(BASELINE)
    payload = {
        "continuous_knobs": 0,
        "baseline_sha256": before,
        "baseline_byte_stable_during_probe": before == after,
        "stored_spectrum_match": answer,
        "named_5fold": named,
        "target": ["9/2", "12", "45/2"],
        "rows": rows,
    }
    RESULTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Σ^5 spectrum match",
        "",
        "Stored numbers only. No spectrum is computed. "
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
        f"Stored spectrum match? {answer}",
        f"Baseline byte-stable during probe? {'Yes' if before == after else 'No'}",
        "",
        "SIGMA5 SPECTRUM MATCH - ZERO KNOBS",
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
    print("SIGMA5 SPECTRUM MATCH - ZERO KNOBS")
    print(f"Stored spectrum match? {answer}")
    if answer == "Yes" and named:
        print(f"Name: {named}")
    print(f"Baseline byte-stable? {'Yes' if before == after else 'No'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
