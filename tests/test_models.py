from __future__ import annotations

import dataclasses

import pytest

from latex_wc.models import WordCountResult


def test_word_count_result_is_frozen() -> None:
    result = WordCountResult(
        total_words=3,
        unique_words=2,
        top_words=[('b', 2), ('a', 1)],
        tokens=['a', 'b', 'b'],
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.total_words = 999  # type: ignore[misc]
