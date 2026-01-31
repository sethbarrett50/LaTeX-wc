from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class WordCountResult:
    """Result of token counting and ranking."""

    total_words: int
    unique_words: int
    top_words: List[Tuple[str, int]]
    tokens: List[str]
