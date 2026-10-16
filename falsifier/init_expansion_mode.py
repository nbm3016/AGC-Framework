#!/usr/bin/env python3
"""
AGC Expansion Mode session initializer.

Prints the active posture, compact 10 rules, and zero-knob checksum reminder.
Writes/updates SESSION_CONTEXT.md with the same content.

Does not modify locked scientific numbers or complete_baseline.json.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_CONTEXT_PATH = os.path.join(ARTIFACT_DIR, "SESSION_CONTEXT.md")

BANNER = "AGC Expansion Mode Active"

POSTURE = (
    "The locked AGC baseline is a core geometric skeleton, not a finished ceiling. "
    "Expand under dimensional and topological discipline; re-lock with continuous_knobs = 0."
)

RULES_COMPACT = [
    "1. Dynamic Skeleton Stance — locks are expandable; do not halt solely for absence from baseline.",
    "2. Scaffolding & Single-Scale Ingestion — one permanent dimensionful yardstick max; else temporary scaffolding.",
    "3. Dimensional Audit — declare [P_s]; reduce dimensionful scaffolding to ratio vs single-scale anchor.",
    "4. Discrete Topological Targeting — absorb only onto discrete invariants (not unstabilized continuous R).",
    "5. Structured Absorption Hypothesis — Parameter → Audit/Ratio → Discrete Anchor → Parameter-Free Lock.",
    "6. Geometric Primacy — universe is topology/shape; if stuck, propose next math/compute step.",
    "7. Scaffolding Provenance — cite PDG/consensus or known proofs for anchors.",
    "8. Advanced Computational Offloading — NPHC/Bertini, TDA, residual tools without free parameters.",
    "9. Active Lemma Generation — after 3 fails: Dimensional / NPHC / TDA → Topological Lemma Spec.",
    "10. Context & Zero-Knob Checksum — start/success language; lock only if continuous_knobs = 0.",
]

SUCCESS_LINE = (
    "Zero continuous free parameters confirmed | continuous_knobs = 0"
)

CHECKSUM_REMINDER = (
    "Zero-knob checksum: after any successful expansion or parameter absorption, "
    f'state "{SUCCESS_LINE}". The session may lock only if this holds.'
)

DOCS = [
    "AGC_Expansion_Mode_Directive_v2.md — full directive (source of truth)",
    "EXPANSION_MODE.md — session posture + 10 rules",
    "EXPANSION_PROTOCOL.md — repeatable checklist",
]


def build_session_context() -> str:
    ts = datetime.now(timezone.utc).isoformat()
    lines = [
        f"# SESSION_CONTEXT — Expansion Mode",
        "",
        f"**Initialized (UTC):** {ts}",
        "",
        f"## {BANNER}",
        "",
        POSTURE,
        "",
        "## Mandatory language",
        "",
        f"- **Start:** {BANNER}",
        f"- **Success:** {SUCCESS_LINE}",
        "",
        "## Posture",
        "",
        POSTURE,
        "",
        "## 10 Expansion Mode Rules (compact)",
        "",
    ]
    lines.extend(f"- {r}" for r in RULES_COMPACT)
    lines.extend(
        [
            "",
            "## Zero-knob checksum reminder",
            "",
            CHECKSUM_REMINDER,
            "",
            "## Governing documents",
            "",
        ]
    )
    lines.extend(f"- `{d}`" for d in DOCS)
    lines.extend(
        [
            "",
            "## Scientific locks (do not casually rewrite)",
            "",
            r"- Native \(N_{\mathrm{gen}}=3\), \(\sigma^*=\sqrt{3}/2\), residual-NLO A4, Stage-4 outputs",
            "- `continuous_knobs = 0` in locked baseline",
            "- See `complete_baseline.json` for authoritative numbers",
            "",
        ]
    )
    return "\n".join(lines)


def print_banner() -> None:
    print("=" * 72)
    print(BANNER)
    print("=" * 72)
    print()
    print("POSTURE")
    print(f"  {POSTURE}")
    print()
    print("10 EXPANSION MODE RULES (compact)")
    for r in RULES_COMPACT:
        print(f"  {r}")
    print()
    print("ZERO-KNOB CHECKSUM REMINDER")
    print(f"  {CHECKSUM_REMINDER}")
    print()
    print("DOCS")
    for d in DOCS:
        print(f"  · {d}")
    print()
    print("=" * 72)


def write_session_context() -> str:
    text = build_session_context()
    with open(SESSION_CONTEXT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    return SESSION_CONTEXT_PATH


def main() -> None:
    print_banner()
    path = write_session_context()
    print(f"Wrote/updated: {path}")


if __name__ == "__main__":
    main()
