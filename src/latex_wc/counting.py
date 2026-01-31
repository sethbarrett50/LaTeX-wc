from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Tuple

from .models import WordCountResult


def count_words(tokens: Iterable[str], top_n: int) -> Tuple[int, int, List[Tuple[str, int]]]:
    """
    Count total words, unique words, and compute top-N frequencies.

    Args:
        tokens: Iterable of normalized tokens (usually lowercase).
        top_n: Number of top words to return (must be > 0).

    Returns:
        (total_words, unique_words, top_words)
    """
    counter = Counter(tokens)
    total = sum(counter.values())
    unique = len(counter)
    top_words = counter.most_common(top_n)
    return total, unique, top_words


def build_result(tokens: List[str], top_n: int) -> WordCountResult:
    """
    Convenience wrapper that returns a WordCountResult.

    Args:
        tokens: List of tokens.
        top_n: Number of top words.

    Returns:
        WordCountResult containing totals, top words, and the tokens list.
    """
    total, unique, top_words = count_words(tokens, top_n=top_n)
    return WordCountResult(total_words=total, unique_words=unique, top_words=top_words, tokens=tokens)
