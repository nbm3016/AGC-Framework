#!/usr/bin/env python3
"""
Atom C: metric cone over the locked SE 5-fold.
Isometry != holonomy. Do not seed Hol=SU(3) as a stored bin.
Do not rewrite Iso. Do not install SU(3)_c.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

from check_engine import LEGAL, runCheck

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_PATH = os.path.join(ARTIFACT_DIR, "complete_baseline.json")
MENU_PATH = os.path.join(ARTIFACT_DIR, "modulus_menu.json")
CU_PATH = os.path.join(ARTIFACT_DIR, "controlled_uniqueness.json")
OUT_PATH = os.path.join(ARTIFACT_DIR, "cone_holonomy.json")


def fail(msg: str) -> None:
    print("FAIL CLOSED:", msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    import hashlib
    baseline_path = globals().get("BASELINE_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "complete_baseline.json"
    )
    baseline_digest = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if baseline_digest != "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a":
        fail("baseline hash " + baseline_digest)

    b = load_json(BASELINE_PATH)
    menu_doc = load_json(MENU_PATH)
    cu = load_json(CU_PATH)
    sc = b.get("status_classification") or {}
    proven = {row["id"]: row for row in sc.get("proven", [])}
    knobs = int(sc.get("continuous_knobs"))
    n_gen = int(proven["native_N_gen_3"]["value"])
    if knobs != 0 or n_gen != 3:
        fail("knobs/N_gen")

    se = "Sasaki" in str(cu.get("class_definition", {}).get("description", ""))
    rows = menu_doc.get("rows") or []
    types0 = {
        n: next(r["type"] for r in rows if r["name"] == n)
        for n in ("warp_factor", "g_mu_nu", "unique_color", "Iso_group")
    }

    dim_su2, dim_u1, dim_su3 = 3, 1, 8
    dim_iso = dim_su2 + dim_su2 + dim_u1
    iso_contains_su3 = dim_iso >= dim_su3

    # Sp(n/2) needs even complex dimension. Cone over a 5-fold is real 6 = complex 3, odd.
    complex_dim = 3
    sp_possible = (complex_dim % 2) == 0
    # Flat: no Riemann(g_C)=0 computation is on disk. Conifold name is not a curvature proof.
    flat_ruled_out_by_files = False

    print("FUNCTOR")
    print("  Isom locked: SU(2)×SU(2)×U(1), dim", dim_iso)
    print("  Cone: g_C = dr^2 + r^2 g_5  (r coordinate; homothety = existing GAUGE scale)")
    print(f"  SE on disk? {se}")
    print(f"  complex dim of cone = {complex_dim}; Sp possible? {sp_possible}")
    print(f"  flat ruled out by a curvature computation on disk? {flat_ruled_out_by_files}")
    print("  Implication (applied, not seeded): SE 5-fold <=> cone CY 3-fold <=> Hol ⊆ SU(3)")
    print("  Equality Hol=SU(3) needs not-flat and not-Sp. Sp ruled out by dim. Flat not ruled out by files.")

    facts = {
        "knobs": knobs,
        "N_gen": n_gen,
        "modulus_menu": rows,
        "sigma_star_locked": True,
        "unique_4fold": False,
        "warp_forced": False,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "dim_iso": dim_iso,
        "dim_su3": dim_su3,
        "iso_contains_su3": False,
        "t_wall_n": "13/2",
        "t_wall_lam": "13/2",
        "isolate_written": False,
    }

    def bin_k1():
        return {
            "bin": "FORCED",
            "gates": [],
            "reasons": [
                "g_C = dr^2 + r^2 g_5 is uniquely fixed by the locked 5-metric; r is a coordinate, homothety is GAUGE; knobs stay 0"
            ],
            "extra_names": ["r_coordinate"],
        }

    def bin_k2():
        return {
            "bin": "FORCED",
            "gates": [],
            "reasons": ["r is a cone coordinate; homothety is existing GAUGE overall scale; not Wilson, GeV, M_R, or A(y)"],
            "extra_names": [],
        }

    def bin_k3():
        if not se:
            return {
                "bin": "UNKNOWN",
                "gates": [],
                "reasons": ["locked files do not record Sasaki-Einstein; Hol not forced"],
                "hol": "UNKNOWN",
            }
        if (not sp_possible) and flat_ruled_out_by_files:
            return {
                "bin": "FORCED",
                "gates": [],
                "reasons": ["SE => Hol ⊆ SU(3); not flat and not Sp => Hol = SU(3). Not color."],
                "hol": "SU(3)",
                "as_color": False,
            }
        return {
            "bin": "UNKNOWN",
            "gates": [],
            "reasons": [
                "SE on disk implies Hol(g_C) ⊆ SU(3) if the cone theorem is applied; "
                "Sp ruled out (complex dim 3); flat not ruled out by a Riemann computation on disk. "
                "Equality Hol=SU(3) not FORCED. Not color."
            ],
            "hol": "UNKNOWN",
            "inclusion": "subseteq SU(3) conditional on SE cone theorem; equality not forced",
        }

    claims = [
        {"id": "K1", "text": "cone metric g_C uniquely determined by locked 5-metric; extra knob?"},
        {"id": "K2", "text": "r is Wilson/GeV/M_R, or a coordinate whose homothety is GAUGE?"},
        {"id": "K3", "text": "What is Hol(g_C)?"},
        {
            "id": "K4",
            "text": "Hol(g_C)=SU(3) forces unique color SU(3)_c",
            "yes_as_lock": {"unique_color_derived": True, "picks_SU3c": True, "burned": True},
            "uses_modulus": "unique_color",
            "labels_modulus_as": "FORCED",
        },
        {"id": "K5", "text": "Does Iso change? Does Iso contain SU(3)?"},
        {
            "id": "K6",
            "text": "cone writes g_mu_nu(x) or A(y) or a 4D EOM",
            "yes_as_lock": {"new_real": True, "sigma_is_gmunu": True},
            "uses_modulus": "g_mu_nu",
            "labels_modulus_as": "FORCED",
        },
        {
            "id": "K7",
            "text": "D3 / KW quiver / G_SM / S^5 / M(3,2) may finish K3 or K4",
            "yes_as_lock": {"weld_class_to_lock": True, "burned": True, "picks_SU3c": True},
            "uses_modulus": "G_SM_from_isolate",
            "labels_modulus_as": "FORCED",
        },
    ]

    live_rows = []
    print("id | claim | live_bin | extra_names | gates | why")
    for c in claims:
        if c["id"] == "K1":
            live = bin_k1()
        elif c["id"] == "K2":
            live = bin_k2()
        elif c["id"] == "K3":
            live = bin_k3()
        elif c["id"] == "K5":
            live = {
                "bin": "FORCED",
                "gates": [],
                "reasons": [
                    f"Iso unchanged SU(2)×SU(2)×U(1), dim {dim_iso}; contains SU(3)? {iso_contains_su3} (7<8)"
                ],
                "extra_names": [],
                "color_lock": False,
            }
        else:
            live = runCheck(c, facts)
        if live["bin"] not in LEGAL:
            fail(f"{c['id']} illegal bin")
        if live["gates"] and live["bin"] != "REFUSED":
            fail(f"{c['id']} refuse-gate did not produce REFUSED")
        row = {"id": c["id"], "text": c["text"], **live}
        live_rows.append(row)
        print(
            f"{c['id']} | {c['text'][:40]} | {live['bin']} | {live.get('extra_names', [])} | {live.get('gates', [])} | {'; '.join(live['reasons'])[:64]}"
        )

    k3 = next(x for x in live_rows if x["id"] == "K3")
    k4 = next(x for x in live_rows if x["id"] == "K4")
    if k4["bin"] == "FORCED":
        fail("K4 must not promote unique color")

    # Earn CONE generated-object row only. Never SU(3)_c. Hol not FORCED so no HOLONOMY lock.
    if next(x["bin"] for x in live_rows if x["id"] == "K1") == "FORCED":
        if not any(r.get("name") == "CONE" for r in rows):
            rows.append(
                {
                    "name": "CONE",
                    "type": "FORCED",
                    "source": "K1 cone functor g_C=dr^2+r^2 g_5",
                    "value_forced": True,
                    "physics_reading": "generated 6-metric; not g_μν, not A(y), not color",
                    "notes": "r coordinate; homothety is existing GAUGE scale",
                }
            )
            menu_doc["rows"] = rows
            with open(MENU_PATH, "w", encoding="utf-8") as f:
                json.dump(menu_doc, f, indent=2)
                f.write("\n")

    types1 = {n: next(r["type"] for r in rows if r["name"] == n) for n in ("warp_factor", "g_mu_nu", "unique_color", "Iso_group")}
    if types1 != types0:
        fail("protected menu types changed")
    if any(r.get("name") == "SU(3)_c" for r in rows):
        fail("SU(3)_c added")

    payload = {
        "module": "cone_holonomy",
        "continuous_knobs": 0,
        "N_gen": 3,
        "iso_group": "SU(2)×SU(2)×U(1)",
        "dim_iso": dim_iso,
        "dim_su3": dim_su3,
        "iso_contains_SU3": False,
        "iso_rewritten": False,
        "se_on_disk": se,
        "sp_ruled_out_by_complex_dim": True,
        "flat_ruled_out_by_files": False,
        "hol_live": k3.get("hol", "UNKNOWN"),
        "color_promoted": False,
        "K": live_rows,
        "isolate_written": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    hol_yes = k3["bin"] == "FORCED" and k3.get("hol") == "SU(3)"
    print("\nCONE HOLONOMY - ISOMETRY != HOLONOMY - ZERO KNOBS")
    print("Cone unique from locked 5-metric? Yes")
    print("Hol(g_C) forced as group?", "Yes" if hol_yes else "Unknown", k3.get("hol", "UNKNOWN"))
    print("Unique color from Layer A? No")
    print("Iso still dim 7? Yes")
    print("Any menu type promoted to color/G_SM/metric? No")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
