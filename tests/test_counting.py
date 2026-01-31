from __future__ import annotations

from latex_wc.counting import build_result, count_words


def test_count_words_basic_no_ties() -> None:
    tokens = ['a', 'b', 'b', 'b', 'c', 'c']
    total, unique, top_words = count_words(tokens, top_n=2)

    assert total == 6
    assert unique == 3
    assert top_words == [('b', 3), ('c', 2)]


def test_count_words_top_n_larger_than_unique() -> None:
    tokens = ['alpha', 'beta', 'beta']
    total, unique, top_words = count_words(tokens, top_n=10)

    assert total == 3
    assert unique == 2
    assert top_words == [('beta', 2), ('alpha', 1)]


def test_build_result_round_trip() -> None:
    tokens = ['x', 'y', 'y']
    result = build_result(tokens, top_n=2)

    assert result.total_words == 3
    assert result.unique_words == 2
    assert result.top_words == [('y', 2), ('x', 1)]
    assert result.tokens is tokens
