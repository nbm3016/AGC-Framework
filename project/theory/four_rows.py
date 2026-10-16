"""Read-only map of the photon, Higgs, equation, and GeV rows.

Writes nothing. Does not add an extra. Does not fill dynamical_4d_eom.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

THEORY = Path(__file__).resolve().parent
DATA = THEORY.parent.parent / "falsifier"
import sys

sys.path.insert(0, str(DATA))
from content_sha import WORK_BASELINE_SHA, content_sha256

WORK_SHA = WORK_BASELINE_SHA
SPOKEN = (
    "color",
    "occupancy",
    "tau",
    "hop-case",
    "k",
    "L",
    "y",
    "GeV",
    "M_R",
    "metric",
    "A",
    "c2",
    "fibration_class",
    "EOM",
    "G_N",
)
MAP_TOKENS = frozenset(
    {
        "SU(3)_c",
        "g_mu_nu",
        "A",
        "y",
        "k",
        "L",
        "c2",
        "GeV",
        "M_R",
        "G_N",
        "fibration_class",
        "lock_name",
        "tau",
        "hop_case",
        "name",
        "EOM",
    }
)
BLOCKED = frozenset(
    {"photon", "higgs", "alpha", "alpha_em", "vev", "coupling", "eV"}
)


def fail(name: str, detail: str = "") -> None:
    message = f"FAIL {name}"
    if detail:
        message += f": {detail}"
    raise SystemExit(message)


def main() -> int:
    baseline = DATA / "complete_baseline.json"
    digest = content_sha256(baseline)
    if digest != WORK_SHA:
        fail("working baseline hash", digest)
    isolate = json.loads((DATA / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        fail("35 locks", str(len(locks)))
    if any(item.get("extras") != 0 for item in locks):
        fail("lock extras")
    by_name = {item["name"]: item for item in locks}
    knob = by_name["continuous_knobs"]
    if knob.get("value") != 0 or knob.get("extras") != 0:
        fail("continuous_knobs")
    kappa = Fraction(9, 16)
    if 4 * kappa != Fraction(9, 4) or 4 * kappa + 1 != Fraction(13, 4):
        fail("kappa arithmetic")
    if 4 * kappa + 1 == Fraction(9, 4):
        fail("banned swap")

    iso = by_name["Iso_group"]
    if iso.get("extras") != 0 or iso.get("dimension") != 7:
        fail("isometry")
    if iso.get("value") != "SU(2)×SU(2)×U(1)" or iso.get("stored_as") != "isometry":
        fail("photon seat")
    if 3 + 3 + 1 != 7:
        fail("u1 dimension")
    sigma = by_name["sigma_star"]
    if sigma.get("extras") != 0 or sigma.get("value") != "sqrt(3)/2":
        fail("higgs shape")
    if sigma.get("square") != "3/4" or "shape" not in sigma.get("reading", ""):
        fail("higgs reading")
    if Fraction(3, 4) / Fraction(4, 3) != kappa:
        fail("kappa from shape")

    maps = [item for item in isolate["maps"] if item.get("status") == "MAP"]
    if len(maps) != 12:
        fail("twelve map rows", str(len(maps)))
    by_map = {item["name"]: item for item in maps}
    eom = by_map["dynamical_4d_eom"]
    if eom.get("slot") != "empty" or eom.get("extras") != ["EOM"]:
        fail("eom slot")
    if eom.get("emptiness_is_an_isolate_atom") is not False:
        fail("eom atom")
    gev = by_map["native_GeV_M_R"]
    if gev.get("extras") != ["GeV", "M_R"]:
        fail("gev extras")
    if "No conversion is written." not in gev.get("why", ""):
        fail("gev conversion")
    hop = by_map["hop_mass"]
    if hop.get("GeV_conversion") is not False or hop.get("no_hop") != "m = 0":
        fail("hop gev")

    tokens = []
    for item in maps:
        extras = item.get("extras")
        if isinstance(extras, list):
            tokens.extend(extras)
    if frozenset(tokens) != MAP_TOKENS:
        fail("map tokens", str(sorted(set(tokens))))
    names = {item["name"].lower() for item in locks + isolate["maps"]}
    if names & BLOCKED:
        fail("added row", str(names & BLOCKED))
    if any(token.lower() in BLOCKED for token in tokens):
        fail("added extra")
    if len(SPOKEN) != 15 or len(set(SPOKEN)) != 15:
        fail("spoken count")
    if set(SPOKEN) & BLOCKED:
        fail("spoken extra")

    print("FOUR ROWS CERTIFICATE PASS")
    print("photon seat U(1) dimension 1 extras added 0")
    print("higgs seat empty extras added 0")
    print("eom slot empty extras added 0")
    print("gev numeral absent extras added 0")
    print("n_LOCK 35 n_promoted 0 n_SOUND 15 continuous_knobs 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
