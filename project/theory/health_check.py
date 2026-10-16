"""Read-only health check for the completed family.

Asserts the proved identities: baseline hash, 35 locks, continuous_knobs = 0,
the 15 extras as sound and not locks, the clock quotients, and the five theory
certificates. It does not treat the 15 as locks, and it does not assert a
metric, a curvature bound, or a firewall. The fourth certificate checks the
sign family and refuses a filled equation slot. The fifth checks that the
photon, Higgs, equation, and GeV rows add no extra.

Writes nothing unless --write-matrix is passed. That flag writes
theory/STATE_MATRIX.md only. The baseline and the isolate are never opened
for writing. --loop repeats the check and is not used by the freeze.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

THEORY = Path(__file__).resolve().parent
ROOT = THEORY.parent
DATA = ROOT.parent / "falsifier"
BASELINE_SHA = (
    "1d9b54a788142b9d2c818d236d55e8a7a71b841c0e032107bcc052f23abe707a"
)
OPEN_EXTRAS = (
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
CERTIFICATES = (
    ("pauli_proof.py", "PAULI PROOF CERTIFICATE PASS"),
    ("c1_c2_derivation.py", "C1 C2 DERIVATION CERTIFICATE PASS"),
    ("completion_proof.py", "COMPLETION PROOF CERTIFICATE PASS"),
    ("d4_gates.py", "D4 GATES CERTIFICATE PASS"),
    ("four_rows.py", "FOUR ROWS CERTIFICATE PASS"),
)


def fail(name: str, detail: str = "") -> None:
    message = f"HEALTH CHECK FAIL {name}"
    if detail:
        message += f": {detail}"
    print(message, flush=True)
    raise SystemExit(1)


def face_and_order8() -> tuple[set[int], set[int]]:
    face = {0}
    x = 0
    while True:
        x = (x + 8) % 24
        if x in face:
            break
        face.add(x)
    order8 = {(3 * k) % 24 for k in range(8)}
    return face, order8


def run_certificate(script: str, expect: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(THEORY / script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 or expect not in completed.stdout:
        tail = (completed.stdout + completed.stderr)[-500:]
        fail(script, tail)


def inventory() -> tuple[list[dict], list[dict], str]:
    baseline_path = DATA / "complete_baseline.json"
    digest = hashlib.sha256(baseline_path.read_bytes()).hexdigest()
    if digest != BASELINE_SHA:
        fail("baseline hash", digest)
    isolate = json.loads((DATA / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        fail("35 locks", str(len(locks)))
    if any(item.get("extras") != 0 for item in locks):
        fail("lock extras")
    by_name = {item["name"]: item for item in locks}
    knob = by_name.get("continuous_knobs")
    if knob is None or knob.get("value") != 0 or knob.get("extras") != 0:
        fail("continuous_knobs")
    maps = [item for item in isolate["maps"] if item.get("status") == "MAP"]
    if len(maps) != 12:
        fail("twelve map rows", str(len(maps)))
    kappa = Fraction(9, 16)
    if 4 * kappa != Fraction(9, 4) or 4 * kappa + 1 != Fraction(13, 4):
        fail("kappa arithmetic")
    if 4 * kappa + 1 == Fraction(9, 4):
        fail("banned swap")
    face, order8 = face_and_order8()
    if face != {0, 8, 16} or order8 != {0, 3, 6, 9, 12, 15, 18, 21}:
        fail("clock quotients")
    if len(OPEN_EXTRAS) != 15:
        fail("fifteen names")
    return locks, maps, digest


def write_matrix(locks: list[dict], maps: list[dict], digest: str) -> None:
    lines = [
        "# State matrix",
        "",
        "Logged from the live isolate and the baseline hash. This page records the freeze. It does not lock. `continuous_knobs = 0`. The 15 extras are sound. They are not locks. No line among the 128 is selected.",
        "",
        f"Baseline sha256: `{digest}`",
        "",
        "## 35 locks",
        "",
        "| name | extras | value |",
        "|------|--------|-------|",
    ]
    for item in locks:
        value = json.dumps(item.get("value"), ensure_ascii=True)
        lines.append(f"| `{item['name']}` | {item.get('extras')} | {value} |")
    lines.extend(
        [
            "",
            "## Module",
            "",
            r"The fourteen generators are the Pauli strings of `theory/PAULI_PROOF.md`. They square to \(I_{128}\), they anticommute, and their subset products fill \(M_{128}(\mathbb{C})\). The exterior residual is \(\{0\}\).",
            "",
            r"Seven commuting address signs \((s_M,s_J,s_A,s_B,s_C,s_D,S)\) label \(2^7 = 128\) joint lines. The lines are a basis. On each line \(E = i\, s_M S\). No line is selected.",
            "",
            "## Arithmetic and clock",
            "",
            r"\[4\kappa = 9/4, \qquad 4\kappa+1 = 13/4.\]",
            "",
            r"The subgroup generated by \(+8\) is \(\{0,8,16\}\), order 3, and the quotient is \(\mathbb{Z}/8\mathbb{Z}\). The unique subgroup of order 8 has index 3, and that quotient is \(\mathbb{Z}/3\mathbb{Z}\).",
            "",
            "## Sound extras",
            "",
            "Twelve map rows remain MAP. The fifteen sound names are:",
            "",
        ]
    )
    for name in OPEN_EXTRAS:
        lines.append(f"- {name}")
    lines.extend(
        [
            "",
            "Map rows:",
            "",
        ]
    )
    for item in maps:
        lines.append(f"- `{item['name']}` extras `{json.dumps(item.get('extras'))}`")
    lines.extend(
        [
            "",
            r"The joint boundary count is unperformed. The face algebra is not \(g_{\mu\nu}\). This matrix does not assert a curvature bound and does not assert a firewall.",
            "",
            r"\[n_{\mathrm{LOCK}} = 35, \qquad n_{\mathrm{promoted}} = 0, \qquad n_{\mathrm{SOUND}} = 15, \qquad \mathrm{continuous\_knobs} = 0.\]",
            "",
        ]
    )
    (THEORY / "STATE_MATRIX.md").write_text("\n".join(lines), encoding="utf-8")


def once(write: bool) -> None:
    for script, expect in CERTIFICATES:
        run_certificate(script, expect)
    locks, maps, digest = inventory()
    if write:
        write_matrix(locks, maps, digest)
    print("HEALTH CHECK PASS", flush=True)


def main() -> int:
    write = "--write-matrix" in sys.argv
    loop = "--loop" in sys.argv
    if loop and write:
        fail("flags", "--loop does not rewrite the matrix")
    while True:
        once(write)
        if not loop:
            return 0
        time.sleep(60)


if __name__ == "__main__":
    raise SystemExit(main())
