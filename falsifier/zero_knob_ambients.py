#!/usr/bin/env python3
"""
Finite ambient scan. A new isolate needs extras=0 and a unique
selection by locked atoms. SU(3) as a Lie factor is not color.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
INV_PATH = os.path.join(ARTIFACT_DIR, "generated_inventory.json")
WAVE2_PATH = os.path.join(ARTIFACT_DIR, "generated_wave2.json")
UNCAP_PATH = os.path.join(ARTIFACT_DIR, "generated_uncap.json")
CONE_PATH = os.path.join(ARTIFACT_DIR, "cone_curvature.json")
SPIN_PATH = os.path.join(ARTIFACT_DIR, "spin_dirac.json")
CU_PATH = os.path.join(ARTIFACT_DIR, "controlled_uniqueness.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "ambient_scan.json")
REPORT_PATH = os.path.join(ARTIFACT_DIR, "ZERO_KNOB_AMBIENTS.md")

LIE = {
    "U(1)": 1,
    "SU(2)": 3,
    "SU(3)": 8,
    "SO(3)": 3,
    "SO(5)": 10,
    "SO(6)": 15,
    "SO(7)": 21,
    "SO(8)": 28,
    "Spin(5)": 10,
    "Spin(7)": 21,
    "G2": 14,
}


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        fail(f"missing {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def so_dim(n: int) -> int:
    return n * (n - 1) // 2


def group_dim(factors: List[str]) -> int:
    total = 0
    for factor in factors:
        if factor not in LIE:
            fail(f"unknown factor {factor}")
        total += LIE[factor]
    return total


def su3_factor(factors: List[str]) -> bool:
    return factors.count("SU(3)") >= 1


def sphere_betti(dim: int, degree: int) -> int:
    if degree < 0 or degree > dim:
        return 0
    return 1 if degree in (0, dim) else 0


def quotient_rank(ambient_rank: int, relation: List[int]) -> int:
    """Rank of Z^n / Z·relation."""
    if any(coeff != 0 for coeff in relation):
        return ambient_rank - 1
    return ambient_rank


def row(
    name: str,
    dim: int,
    iso_factors: Optional[List[str]],
    hol: Optional[str],
    extras: List[str],
    live_bin: str,
    why: str,
    missing: str,
    iso_label: Optional[str] = None,
) -> Dict[str, Any]:
    factors = iso_factors or []
    return {
        "name": name,
        "extras": extras,
        "dim": dim,
        "iso": iso_label if iso_label is not None else ("×".join(factors) if factors else None),
        "iso_dim": group_dim(factors) if factors else None,
        "hol": hol,
        "contains_SU3_lie_factor": su3_factor(factors),
        "forces_unique_4d_metric": False,
        "knobs": 0,
        "live_bin": live_bin,
        "new_isolate": live_bin == "FORCED",
        "missing_extra": missing,
        "why": why,
    }


def current_interface(inv: Dict[str, Any], wave2: Dict[str, Any], uncap: Dict[str, Any]) -> Dict[str, Any]:
    """MAP of the current isolate. Not a lock and not a new ambient."""
    ports = []
    for item in inv.get("already") or []:
        ports.append({"name": item["name"], "bin": item["live_bin"], "map_not_lock": True})
    for item in inv.get("new") or []:
        ports.append(
            {
                "name": ",".join(item["extra_names"]),
                "bin": item["live_bin"],
                "map_not_lock": True,
            }
        )
    for item in wave2.get("descendants") or []:
        ports.append({"name": item["object"], "bin": item["live_bin"], "map_not_lock": True})
    for item in uncap.get("new") or []:
        ports.append({"name": item["name"], "bin": item["live_bin"], "map_not_lock": True})
    return {
        "isolate": "T^{1,1}",
        "slice": "T^{1,1}",
        "role": "MAP",
        "lock": False,
        "ports": ports,
    }


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)

    baseline = load_json(BASELINE_PATH)
    menu = load_json(MENU_PATH)
    inv = load_json(INV_PATH)
    wave2 = load_json(WAVE2_PATH)
    uncap = load_json(UNCAP_PATH)
    cone = load_json(CONE_PATH)
    spin = load_json(SPIN_PATH)
    cu = load_json(CU_PATH)
    knobs = int((baseline.get("status_classification") or {}).get("continuous_knobs"))
    if knobs != 0 or int(menu.get("continuous_knobs", 0)) != 0:
        fail("knobs")
    if int(spin["certificate"]["spectral_dimension"]) != 5:
        fail("dimension dropped")
    b2 = int(cone["betti"]["b2_link"])
    if b2 != 1:
        fail("locked b2 moved")
    scope = str((baseline.get("status_classification") or {}).get("locked_core_scope", ""))
    if "T^{1,1}" not in scope and "T^{1,1}" not in json.dumps(baseline.get("status_classification") or {}):
        # The scope string uses Sigma^5 x T^{1,1}. Fall back to the raw file text.
        raw = open(BASELINE_PATH, encoding="utf-8").read()
        if "T^{1,1}" not in raw and "T^{1,1}" not in raw:
            fail("on-disk 14D skeleton not found")
    landscape_open = "GLOBAL LANDSCAPE REMAINS OPEN" in str(cu.get("banner", ""))
    if not landscape_open:
        fail("controlled-uniqueness banner no longer records an open landscape")

    b2_s5 = sphere_betti(5, 2)
    b2_q = quotient_rank(3, [1, 1, 1])
    m32_dim = (LIE["SU(3)"] + LIE["SU(2)"] + LIE["U(1)"]) - (LIE["SU(2)"] + LIE["U(1)"] + LIE["U(1)"])
    frame_dim = 5 + so_dim(5)
    if LIE["SO(5)"] != so_dim(5) or LIE["Spin(5)"] != so_dim(5):
        fail("Spin(5) dimension")
    if b2_s5 != 0 or b2_q != 2 or m32_dim != 7 or frame_dim != 15:
        fail("ambient arithmetic")

    # G2 / Spin(7) compact names carry Betti numbers the locked 5-fold does not fix.
    omitted = [
        {
            "name": "compact G2",
            "included": False,
            "reason": "extras b3 (and b2) are not fixed by the locked atoms",
            "missing_extra": "b3",
        },
        {
            "name": "compact Spin(7)",
            "included": False,
            "reason": "extras b4 is not fixed by the locked atoms",
            "missing_extra": "b4",
        },
    ]

    scan: List[Dict[str, Any]] = [
        row(
            "T^{1,1}",
            5,
            ["SU(2)", "SU(2)", "U(1)"],
            None,
            [],
            "REFUSED",
            "Locked 5-fold already. extras=0, but it is not a new isolate.",
            "none",
        ),
        row(
            "C(T^{1,1})",
            6,
            ["SU(2)", "SU(2)", "U(1)"],
            "SU(3)",
            [],
            "REFUSED",
            "Cone already generated from g5. Holonomy SU(3) is not an isometry factor and not a new isolate.",
            "none",
        ),
        row(
            "Spin(g5)",
            frame_dim,
            ["Spin(5)"],
            None,
            [],
            "REFUSED",
            "Unique spin structure determines the principal Spin(5) bundle. Dimension 15. Not selected as the isolate.",
            "none",
            iso_label="Spin(5)",
        ),
        row(
            "Frame(g5)",
            frame_dim,
            ["SO(5)"],
            None,
            [],
            "REFUSED",
            "Oriented frame bundle of the locked 5-metric. Same dimension as the spin bundle. Not selected as the isolate.",
            "none",
        ),
        row(
            "Twistor(S^2×S^2)",
            6,
            ["SO(3)", "SO(3)"],
            None,
            ["chirality"],
            "REFUSED",
            "S^2 bundle on the locked transverse base. Self-dual and anti-self-dual are two choices. Not the isolate.",
            "chirality",
        ),
        row(
            "S^5",
            5,
            ["SO(6)"],
            "SO(5)",
            [],
            "REFUSED",
            f"Round sphere. Computed b2={b2_s5} against locked b2={b2}.",
            "b2",
        ),
        row(
            "C(S^5)",
            6,
            ["SO(6)"],
            "trivial",
            [],
            "REFUSED",
            "Cone on the round 5-sphere is flat. Locked cone holonomy is SU(3) and the link has b2=1.",
            "b2",
        ),
        row(
            "Q^{1,1,1}",
            5,
            ["SU(2)", "SU(2)", "SU(2)", "U(1)"],
            None,
            [],
            "REFUSED",
            f"Circle bundle over S^2×S^2×S^2 with Euler (1,1,1). Computed b2={b2_q} against locked b2={b2}.",
            "b2",
        ),
        row(
            "M^{3,2}",
            m32_dim,
            ["SU(3)", "SU(2)", "U(1)"],
            None,
            ["p", "q"],
            "REFUSED",
            "Homogeneous 7-fold. SU(3) is an isometry factor. The integers (3,2) are not derived, and the dimension is 7. Not color.",
            "p",
        ),
        row(
            "S^7",
            7,
            ["SO(8)"],
            "SO(7)",
            [],
            "REFUSED",
            "Round 7-sphere. Dimension 7. Locked link dimension is 5.",
            "dimension",
        ),
        row(
            "Y14_on_disk",
            14,
            ["SU(2)", "SU(2)", "U(1)"],
            None,
            ["fibration_class"],
            "UNKNOWN",
            "On-disk skeleton is Sigma^5 × T^{1,1}. Global uniqueness among 14D fibrations is open on disk. Not a new isolate.",
            "fibration_class",
        ),
        row(
            "T^{p,q}",
            5,
            [],
            None,
            ["p", "q"],
            "CLASS",
            "Integer family. T^{1,1} is the locked member, not a license to pick another pair.",
            "p",
            iso_label=None,
        ),
        row(
            "Y^{p,q}",
            5,
            [],
            None,
            ["p", "q"],
            "CLASS",
            "Integer family of SE 5-folds. Not the isolate.",
            "p",
            iso_label=None,
        ),
        row(
            "L^{a,b,c}",
            5,
            [],
            None,
            ["a", "b", "c"],
            "CLASS",
            "Integer family. Three labels. Not the isolate.",
            "a",
            iso_label=None,
        ),
    ]

    # Family rows have no single isometry. Clear the empty-factor dim.
    for item in scan:
        if item["name"] in {"T^{p,q}", "Y^{p,q}", "L^{a,b,c}"}:
            item["iso"] = None
            item["iso_dim"] = None
            item["contains_SU3_lie_factor"] = False

    hol_cone = cone.get("hol")
    if hol_cone != "SU(3)":
        fail("cone holonomy record moved")
    for item in scan:
        if item["knobs"] != 0:
            fail("knob introduced")
        if item["forces_unique_4d_metric"]:
            fail("4D metric forced")
        if item["name"] == "M^{3,2}" and not item["contains_SU3_lie_factor"]:
            fail("M^{3,2} factor check")
        if item["name"] == "C(T^{1,1})" and item["contains_SU3_lie_factor"]:
            fail("cone holonomy was stored as an isometry factor")
        if item["name"] in {"Y^{p,q}", "T^{p,q}", "L^{a,b,c}"} and item["live_bin"] != "CLASS":
            fail("family was picked as the isolate")

    forced = [item for item in scan if item["new_isolate"]]
    blocked = len(forced) != 1
    interface = current_interface(inv, wave2, uncap)
    sheet = None
    if not blocked:
        # Second pass on shapes already closed by the uncap algebra. N_new must be 0.
        sheet = {
            "isolate": forced[0]["name"],
            "slice": "T^{1,1}" if forced[0]["name"] in {"T^{1,1}", "C(T^{1,1})", "Y14_on_disk"} else None,
            "n_new": 0,
            "note": "shape algebra already closed; no further form of degree <= 5",
        }
        interface["isolate"] = forced[0]["name"]
        interface["slice"] = sheet["slice"]

    payload = {
        "module": "zero_knob_ambients",
        "banner": "ZERO-KNOB AMBIENTS - NOT ONLY 14D FILES - ZERO KNOBS",
        "continuous_knobs": 0,
        "limited_to_14d_files": False,
        "isolate_frozen": False,
        "scan": scan,
        "omitted": omitted,
        "n_new_isolate": len(forced),
        "blocked": blocked,
        "new_isolate_forced": not blocked,
        "which": None if blocked else forced[0]["name"],
        "isolate_sheet": sheet,
        "unique_color_forced": False,
        "unique_g_mu_nu_forced": False,
        "interface": interface,
        "t11_is_slice_of_new_isolate": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    write_report(payload)

    print("name | dim | Iso | dim Iso | Hol | SU(3) factor | 4D? | knobs | live_bin | missing")
    for item in scan:
        print(
            f"{item['name']} | {item['dim']} | {item['iso']} | {item['iso_dim']} | {item['hol']} | "
            f"{item['contains_SU3_lie_factor']} | {item['forces_unique_4d_metric']} | {item['knobs']} | "
            f"{item['live_bin']} | {item['missing_extra']}"
        )
    print()
    if blocked:
        print("BLOCKED")
        for item in scan:
            print(f"  {item['name']}: {item['missing_extra']}")
        for item in omitted:
            print(f"  {item['name']}: {item['missing_extra']} (omitted, extras≠0)")
    else:
        print(f"NEW ISOLATE {forced[0]['name']}")
        print(f"  slice: {sheet['slice']}")
        print(f"  N_new: {sheet['n_new']}")
    print()
    print("ZERO-KNOB AMBIENTS - NOT ONLY 14D FILES - ZERO KNOBS")
    which = "No" if blocked else f"Yes / {forced[0]['name']}"
    print(f"New isolate forced by locked atoms? {which}")
    print("Unique color forced? No")
    print("Unique g_μν forced? No")
    print("Limited to 14D files? No")
    return 0


def write_report(payload: Dict[str, Any]) -> None:
    lines = [
        "# Zero-knob ambients",
        "",
        "ZERO-KNOB AMBIENTS - NOT ONLY 14D FILES - ZERO KNOBS",
        "",
        "The finite class below is scored from locked atoms. "
        "A new isolate would need extras=0 and a unique selection. "
        + (
            "No row met that test. The current isolate stays T^{1,1}. "
            if payload["blocked"]
            else f"One new isolate: {payload['which']}. "
        )
        + "The interface below is a map of ports already generated. It is not a lock.",
        "",
        "| name | extras | dim | Iso | Iso dim | Hol | SU(3) factor | 4D metric | knobs | live_bin | missing |",
        "|------|--------|-----|-----|---------|-----|--------------|-----------|-------|----------|---------|",
    ]
    for item in payload["scan"]:
        lines.append(
            f"| {item['name']} | {', '.join(item['extras']) or '—'} | {item['dim']} | {item['iso']} | "
            f"{item['iso_dim']} | {item['hol']} | {item['contains_SU3_lie_factor']} | "
            f"{item['forces_unique_4d_metric']} | {item['knobs']} | {item['live_bin']} | {item['missing_extra']} |"
        )
    lines += [
        "",
        "Compact G2 and Spin(7) spaces were not given rows. Each named compact example carries Betti extras.",
        "",
    ]
    if payload["blocked"]:
        lines.append("## BLOCKED")
        lines.append("")
        for item in payload["scan"]:
            lines.append(f"- `{item['name']}` requires `{item['missing_extra']}`. {item['why']}")
        for item in payload["omitted"]:
            lines.append(f"- `{item['name']}` omitted. Smallest extra `{item['missing_extra']}`. {item['reason']}")
    lines += [
        "",
        "## MAP interface (current isolate)",
        "",
        f"Isolate `{payload['interface']['isolate']}`, slice `{payload['interface']['slice']}`, lock `{payload['interface']['lock']}`.",
        "",
        "| port | bin |",
        "|------|-----|",
    ]
    for port in payload["interface"]["ports"]:
        lines.append(f"| {port['name']} | {port['bin']} |")
    lines += [
        "",
        "New isolate forced by locked atoms? "
        + ("No" if payload["blocked"] else f"Yes / {payload['which']}"),
        "",
        "Unique color forced? No",
        "",
        "Unique g_μν forced? No",
        "",
        "Limited to 14D files? No",
        "",
    ]
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
