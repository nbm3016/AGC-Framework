"""SHA-256 of a file after carriage returns are removed.

A lock is the text. Windows and Unix checkouts of that text are the same lock.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

WORK_BASELINE_SHA = (
    "6f9324041deb0c48317fbee4e7185a2395f5be4cccb432f8fd0f51326d8cef3f"
)
CORE_BASELINE_SHA = (
    "0b2590e0aeb5c64e527f65d4b0ee1e46fff098b79e22c8ae4ee1fdbf396a6de2"
)


def content_sha256(path: Path | str) -> str:
    data = Path(path).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()
