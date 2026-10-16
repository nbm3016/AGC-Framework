"""Score whether the locked 10-fold forces a unique triple of 4-real-dimensional faces.

Bins are computed from files already on disk. A row is FORCED only when the
recorded type matches and extras are empty. A row is REFUSED only when those
files contradict the geometric claim. Otherwise the row is UNKNOWN.
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
MENU = ROOT / "modulus_menu.json"
IDENT = ROOT / "identification.json"
YARDSTICK = ROOT / "yardstick_lovelock_euler.json"
SCOPE = PROJECT / "DIMENSIONAL_SCOPE.md"
RESULTS = ROOT / "face_triple_results.json"
REPORT = ROOT / "FACE_TRIPLE_REPORT.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def menu_row(menu: dict, name: str) -> dict:
    for row in menu["rows"]:
        if row["name"] == name:
            return row
    raise KeyError(name)


def transverse_base(inventory: dict) -> dict:
    for item in inventory["new"]:
        if "TRANSVERSE_BASE" in item.get("extra_names", []):
            return item
    raise KeyError("TRANSVERSE_BASE")


def row(rid: str, claim: str, unique: bool, live_bin: str, extras: list, why: str, **extra) -> dict:
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
    menu = load(MENU)
    ident = load(IDENT)
    yard = load(YARDSTICK)
    scope = SCOPE.read_text(encoding="utf-8")

    knobs = [
        isolate["continuous_knobs"],
        inventory["continuous_knobs"],
        menu["continuous_knobs"],
        ident["continuous_knobs"],
    ]
    if any(k != 0 for k in knobs):
        raise SystemExit("continuous_knobs is not 0")

    factors = yard["lovelock_catalog"]["internal_factors"]
    sigma = factors["Sigma5"]
    t11 = factors["T11"]
    product = factors["T11xSigma5_product"]
    base = transverse_base(inventory)
    gmunu = menu_row(menu, "g_mu_nu")
    x4 = menu_row(menu, "leftover_X4_family")
    cp2 = menu_row(menu, "CP2_as_the_4fold")
    k3 = menu_row(menu, "K3_as_the_4fold")
    wall = next(item for item in isolate["locks"] if item["name"] == "wall_zero_count")

    fibre = isolate["compact_fibre"]
    factor_names = isolate["compact_factors_only"]
    dim_match = sigma["dim"] == 5 and t11["dim"] == 5 and product["dim"] == 10
    fibre_named = factor_names == ["Σ^5", "T^{1,1}"] and "Σ^5 × T^{1,1}" in fibre
    f1_ok = (
        dim_match
        and fibre_named
        and isolate["ambient_dimension"] == 14
        and isolate["five_fold_is_ambient"] is False
        and isolate["ambient_statement"] == "Y^{14} → M^4"
    )
    rows = []
    if f1_ok:
        rows.append(
            row(
                "F1",
                "Is Σ^5 × T^{1,1} the locked 10D compact space?",
                True,
                "FORCED",
                [],
                "isolate compact_fibre is X^{10} = Σ^5 × T^{1,1}. "
                "yardstick_lovelock_euler.json records dim 5 and dim 5, product dim 10. "
                "five_fold_is_ambient is false. continuous_knobs is 0. "
                "fibration_class_unique is false and is a different row.",
            )
        )
    else:
        rows.append(
            row(
                "F1",
                "Is Σ^5 × T^{1,1} the locked 10D compact space?",
                False,
                "UNKNOWN",
                ["compact fibre"],
                "The fibre string or the 5+5 dimension record does not match.",
            )
        )

    base_value = base.get("value")
    base_forced = (
        base.get("unique") is True
        and base.get("live_bin") == "FORCED"
        and base_value == "S^2×S^2"
        and base.get("forces_metric") is False
    )
    if base_forced:
        rows.append(
            row(
                "F2",
                "What 4D faces, if any, are forced by T^{1,1}?",
                True,
                "FORCED",
                [],
                "generated_inventory.json TRANSVERSE_BASE is unique and FORCED, value S^2×S^2. "
                "The recorded reason is the free S^1 quotient of the S^3 factor of T^{1,1} ≃ S^2×S^3. "
                "S^2×S^2 is 4-real-dimensional. forces_metric is false.",
                value="S^2×S^2",
                real_dimension=4,
            )
        )
    else:
        rows.append(
            row(
                "F2",
                "What 4D faces, if any, are forced by T^{1,1}?",
                False,
                "UNKNOWN",
                ["transverse base"],
                "TRANSVERSE_BASE is not a unique forced S^2×S^2 in generated_inventory.json.",
            )
        )

    sigma_face_keys = [k for k in sigma.keys() if "face" in k.lower() or "quotient" in k.lower() or "base" in k.lower()]
    scope_says_not_a_mesh = "Σ^5 as a live 5D grid" in scope and "not a live 5D mesh" in scope
    if sigma_face_keys:
        rows.append(
            row(
                "F3",
                "What 4D faces, if any, are forced by Σ^5?",
                False,
                "UNKNOWN",
                sigma_face_keys,
                "Sigma5 in yardstick_lovelock_euler.json carries extra face keys. They are not scored as one extras-free face.",
            )
        )
    else:
        rows.append(
            row(
                "F3",
                "What 4D faces, if any, are forced by Σ^5?",
                False,
                "UNKNOWN",
                ["4D face of Σ^5"],
                "yardstick_lovelock_euler.json records Sigma5 as dim 5 with Euler characteristic 0 and no quotient. "
                "DIMENSIONAL_SCOPE.md says APS on Σ^5 is the Stage 1A survivor set, not a live 5D mesh. "
                "No extras-free 4D face is stored, and no file rules one out.",
                scope_not_a_mesh=scope_says_not_a_mesh,
                sigma_dim=sigma["dim"],
            )
        )

    mode_count = (
        ident["N_gen"] == 3
        and ident["N_gen_meaning"] == "count of wall-index zeros"
        and ident["three_generations_is_A_lock"] is False
        and ident["same_4d_weyl_three_times"] is False
        and wall["value"] == 3
        and wall["su2_dimensions"] == [2, 3, 4]
    )
    if mode_count:
        rows.append(
            row(
                "F4",
                "What does N_gen=3 force as a geometric type?",
                False,
                "REFUSED",
                [],
                "falsifier/identification.json stores N_gen as the count of wall-index zeros. "
                "three_generations_is_A_lock is false. same_4d_weyl_three_times is false. "
                "The zeros are the harmonics of dimensions 2, 3, and 4. That record contradicts a type of three 4-manifolds.",
                forced_as="wall-index zero count",
            )
        )
    else:
        rows.append(
            row(
                "F4",
                "What does N_gen=3 force as a geometric type?",
                False,
                "UNKNOWN",
                ["geometric type of N_gen"],
                "The identification file does not decide the geometric type.",
            )
        )

    filt = isolate["filter"]
    filter_is_mode = (
        filt["role"] == "filter"
        and filt["wall_reading"].startswith("j2 = 0")
        and "face" not in filt
    )
    if filter_is_mode:
        rows.append(
            row(
                "F5",
                "What does ★Ψ=Ψ force as a geometric type?",
                False,
                "REFUSED",
                [],
                "isolate filter.role is filter. wall_reading is j2 = 0, where the defect vanishes. "
                "The stored statement is ★Ψ = Ψ = Ψ★. No 4-manifold is stored on that row. "
                "The record contradicts a geometric face type.",
            )
        )
    else:
        rows.append(
            row(
                "F5",
                "What does ★Ψ=Ψ force as a geometric type?",
                False,
                "UNKNOWN",
                ["geometric type of the filter"],
                "The filter record does not decide a geometric type.",
            )
        )

    third_contradicted = (
        gmunu["type"] == "OPEN-FIELD"
        and gmunu["value_forced"] is False
        and x4["type"] == "CLASS"
        and x4["value_forced"] is False
        and cp2["type"] == "FORBIDDEN"
        and k3["type"] == "FORBIDDEN"
        and isolate["page_interface"]["is_g_mu_nu"] is False
        and isolate["page_interface"]["is_lock"] is False
    )
    if third_contradicted:
        rows.append(
            row(
                "F6",
                "Is a third 4D face forced from the 10-fold with extras=0?",
                False,
                "REFUSED",
                [],
                "modulus_menu.json g_mu_nu is OPEN-FIELD with value_forced false. "
                "leftover_X4_family is CLASS and is not a unique 4-fold. "
                "CP2_as_the_4fold and K3_as_the_4fold are FORBIDDEN. "
                "page_interface is not a lock and is_g_mu_nu is false. "
                "M^4 is the base in the ambient statement, and the 10-fold is the fibre. "
                "Those rows contradict a third 4D face forced from the 10-fold with extras 0.",
            )
        )
    else:
        rows.append(
            row(
                "F6",
                "Is a third 4D face forced from the 10-fold with extras=0?",
                False,
                "UNKNOWN",
                ["third 4D face"],
                "The menu does not both leave g_mu_nu unforced and forbid a unique 4-fold pick.",
            )
        )

    by_id = {item["id"]: item for item in rows}
    legs = [by_id["F2"], by_id["F3"], by_id["F6"]]
    triple_forced = all(
        leg["live_bin"] == "FORCED" and leg["unique"] is True and leg["extras"] == []
        for leg in legs
    )
    if triple_forced:
        rows.append(
            row(
                "F7",
                "Is a unique triple of 4D faces forced?",
                True,
                "FORCED",
                [],
                "F2, F3, and F6 are each unique, type-matched, and extras-free.",
            )
        )
        triple_answer = "Yes"
    elif any(leg["live_bin"] == "REFUSED" for leg in legs):
        rows.append(
            row(
                "F7",
                "Is a unique triple of 4D faces forced?",
                False,
                "REFUSED",
                [],
                "A unique triple needs F2, F3, and F6 each FORCED with extras 0. "
                "At least one of those legs is contradicted by the files.",
            )
        )
        triple_answer = "No"
    else:
        rows.append(
            row(
                "F7",
                "Is a unique triple of 4D faces forced?",
                False,
                "UNKNOWN",
                ["missing 4D face"],
                "The files do not force all three legs, and they do not contradict every leg.",
            )
        )
        triple_answer = "Unknown"

    after = sha256(BASELINE)
    payload = {
        "continuous_knobs": 0,
        "baseline_sha256": before,
        "baseline_byte_stable_during_probe": before == after,
        "unique_triple_forced": triple_answer,
        "face_from_T11": by_id["F2"].get("value"),
        "face_from_Sigma5": None,
        "third_face": None,
        "rows": rows,
    }
    RESULTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 10D face triple",
        "",
        "Bins are read off the locked files. `continuous_knobs = 0`. "
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
    t11_name = payload["face_from_T11"] or ""
    t11_yes = "Yes" if by_id["F2"]["live_bin"] == "FORCED" else "No"
    if t11_name and t11_yes == "Yes":
        t11_yes = f"Yes ({t11_name})"
    sigma_yes = "Yes" if by_id["F3"]["live_bin"] == "FORCED" else (
        "Unknown" if by_id["F3"]["live_bin"] == "UNKNOWN" else "No"
    )
    third_yes = "Yes" if by_id["F6"]["live_bin"] == "FORCED" else (
        "Unknown" if by_id["F6"]["live_bin"] == "UNKNOWN" else "No"
    )
    lines += [
        "",
        f"Unique 4D face from T^{{1,1}}: {t11_yes}",
        f"Unique second face from Σ^5: {sigma_yes}",
        f"Unique third face: {third_yes}",
        f"Unique triple forced? {triple_answer}",
        f"Baseline byte-stable during probe? {'Yes' if before == after else 'No'}",
        "",
        "10D FACE TRIPLE PROBE - ZERO KNOBS",
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
    print("10D FACE TRIPLE PROBE - ZERO KNOBS")
    print(f"Unique triple forced? {triple_answer}")
    print(f"Baseline byte-stable? {'Yes' if before == after else 'No'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
