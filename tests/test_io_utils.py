from __future__ import annotations

import pytest

from latex_wc.io_utils import read_text_best_effort


def test_read_text_best_effort_reads_utf8(tmp_path) -> None:
    p = tmp_path / 'doc.tex'
    p.write_text('Hello — café ☕', encoding='utf-8')

    assert read_text_best_effort(p) == 'Hello — café ☕'


def test_read_text_best_effort_falls_back_to_latin1(tmp_path) -> None:
    p = tmp_path / 'latin1.tex'
    p.write_bytes('café'.encode('latin-1'))

    assert read_text_best_effort(p) == 'café'


def test_read_text_best_effort_raises_for_missing_file(tmp_path) -> None:
    p = tmp_path / 'missing.tex'
    with pytest.raises(OSError):
        _ = read_text_best_effort(p)
