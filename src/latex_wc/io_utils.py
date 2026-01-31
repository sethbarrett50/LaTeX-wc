from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def read_text_best_effort(path: Path) -> str:
    """
    Read text with a sensible encoding fallback.

    Attempts UTF-8 first, then falls back to Latin-1 to avoid crashing
    on older or mixed-encoding documents.

    Args:
        path: File path to read.

    Returns:
        File contents as a string.

    Raises:
        OSError: If the file cannot be read.
    """
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return path.read_text(encoding='latin-1')
