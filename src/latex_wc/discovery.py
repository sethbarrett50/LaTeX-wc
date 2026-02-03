from __future__ import annotations

import os

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

DEFAULT_EXCLUDE_DIRS: tuple[str, ...] = (
    '.git',
    '.venv',
    'venv',
    '__pycache__',
    '.mypy_cache',
    '.ruff_cache',
    '.pytest_cache',
    'build',
    'dist',
)


@dataclass(frozen=True)
class DiscoveryResult:
    files: tuple[Path, ...]


def discover_tex_files(
    root: Path,
    *,
    exclude_dirs: Sequence[str] = DEFAULT_EXCLUDE_DIRS,
) -> DiscoveryResult:
    """
    Recursively discover *.tex files under a root directory.

    - Prunes common build/venv/cache directories for speed.
    - Returns paths in deterministic sorted order.

    Raises:
        NotADirectoryError: if root is not a directory.
    """
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(str(root))

    exclude_set = set(exclude_dirs)
    found: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_set and not d.startswith('.')]

        for name in filenames:
            if name.lower().endswith('.tex'):
                found.append((Path(dirpath) / name).resolve())

    found_sorted = tuple(sorted(set(found)))
    return DiscoveryResult(files=found_sorted)
