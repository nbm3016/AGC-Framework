"""Open the joint boundary test on Y^14 → M^4.

The test counts solutions of ★Ψ = Ψ = Ψ* as an asymptotic on-shell
boundary condition. If no file exports that operator, the count stays
unperformed. The Clifford bracket is not used as a substitute.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent / "project"
BASELINE = ROOT / "complete_baseline.json"
OUT_JSON = ROOT / "joint_boundary.json"
OUT_MD = ROOT / "JOINT_BOUNDARY.md"
THEORY = PROJECT / "theory" / "JOINT_BOUNDARY.md"

MARKERS = {
    "triality_build.py": "Not an on-shell boundary condition.",
    "native_aps_index.py": "Not dim ker D_5 of Ceresole geometric Dirac.",
    "theory/THEORY_RULES.md": "has not been run as an asymptotic on-shell boundary condition",
}
MARKER_FILES = {
    "triality_build.py": ROOT / "triality_build.py",
    "native_aps_index.py": ROOT / "native_aps_index.py",
    "theory/THEORY_RULES.md": PROJECT / "theory" / "THEORY_RULES.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    baseline_hash = sha256(BASELINE)
    isolate = json.loads((ROOT / "isolate_updated.json").read_text(encoding="utf-8"))
    locks = [item for item in isolate["locks"] if item.get("status") == "LOCK"]
    if len(locks) != 35:
        raise SystemExit(f"expected 35 locks, found {len(locks)}")
    if isolate.get("ambient_statement") != "Y^{14} → M^4":
        raise SystemExit("ambient statement is not Y^14 → M^4")

    missing = []
    for name, marker in MARKERS.items():
        text = MARKER_FILES[name].read_text(encoding="utf-8")
        if marker not in text:
            missing.append(name)
    if missing:
        raise SystemExit(f"expected markers absent: {missing}")

    exported = []
    for path in ROOT.rglob("*.py"):
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "asymptotic on-shell boundary condition" in text and "def " in text:
            # A mention in a scorer is not an exported solver.
            if "def solve" in text or "def asymptotic" in text:
                exported.append(str(path.relative_to(ROOT)))
    operator_exported = len(exported) > 0
    solution_count = None if not operator_exported else "unread"

    lines = [
        "# Joint boundary test",
        "",
        "JOINT BOUNDARY TEST - Y14 TO M4 - ZERO KNOBS",
        "",
        f"Operator exported? {'Yes' if operator_exported else 'No'}",
        "",
        "Solution count: unperformed" if solution_count is None else f"Solution count: {solution_count}",
        "",
        "Rows promoted: 0",
        "",
        "The test is the count of solutions of ★Ψ = Ψ = Ψ* as an asymptotic on-shell boundary condition on Y^14 → M^4.",
        "",
        "No file exports that boundary-value problem. The solution count is not a number. The test stays UNPERFORMED.",
        "",
        "triality_build.py records its Cl(14) bracket as not an on-shell boundary condition. native_aps_index.py counts APS-neutral modes on the j2=0 line and records that this count is not dim ker D_5. Neither object was counted as a boundary solution.",
        "",
        "M^4, Σ^5, and the cone add to 15. The fiber is Σ^5×T^{1,1}.",
        "",
        "C1 and C2 stay UNKNOWN. No coset is selected. The 35 locks stay.",
        "",
        f"Baseline sha256: {baseline_hash}",
        "",
    ]
    payload = {
        "continuous_knobs": 0,
        "promoted": 0,
        "rows_promoted": 0,
        "baseline_sha256": baseline_hash,
        "locks_changed": 0,
        "test": "star Psi = Psi = Psi star as asymptotic on-shell boundary condition on Y^14 → M^4",
        "operator_exported": operator_exported,
        "exported_paths": exported,
        "solution_count": solution_count,
        "bin": "UNPERFORMED",
        "substitute_used": False,
        "C1": "UNKNOWN",
        "C2": "UNKNOWN",
        "coset_selected": None,
        "fiber": "Sigma5 x T^(1,1)",
        "sum_M4_Sigma5_cone": 15,
    }
    text = "\n".join(lines) + "\n"
    OUT_MD.write_text(text, encoding="utf-8")
    THEORY.write_text(text, encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("\n".join(lines[:16]))
    if sha256(BASELINE) != baseline_hash:
        raise SystemExit("baseline changed during the test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
