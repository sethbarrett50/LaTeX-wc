from __future__ import annotations

import csv

from latex_wc.writers import write_top_words_csv, write_words_txt


def test_write_words_txt_creates_parent_and_writes_newline(tmp_path) -> None:
    out_path = tmp_path / 'logs' / 'words.txt'
    tokens = ['hello', 'world']

    write_words_txt(tokens, out_path)

    assert out_path.exists()
    assert out_path.read_text(encoding='utf-8') == 'hello\nworld\n'


def test_write_top_words_csv_has_header_and_ranked_rows(tmp_path) -> None:
    out_path = tmp_path / 'logs' / 'top_words.csv'
    top_words = [('alpha', 5), ('beta', 3)]

    write_top_words_csv(top_words, out_path)

    assert out_path.exists()
    with out_path.open('r', encoding='utf-8', newline='') as handle:
        rows = list(csv.reader(handle))

    assert rows[0] == ['rank', 'word', 'count']
    assert rows[1] == ['1', 'alpha', '5']
    assert rows[2] == ['2', 'beta', '3']
