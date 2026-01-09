from __future__ import annotations

import csv

from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from pathlib import Path


def write_words_txt(tokens: List[str], out_path: Path) -> None:
    """
    Write one token per line to a text file.

    Args:
        tokens: Tokens to write.
        out_path: Destination path for words.txt.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(tokens) + '\n', encoding='utf-8')


def write_top_words_csv(top_words: List[Tuple[str, int]], out_path: Path) -> None:
    """
    Write top word frequencies to a CSV file.

    Args:
        top_words: List of (word, count) pairs.
        out_path: Destination path for top_words.csv.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['rank', 'word', 'count'])
        for idx, (word, count) in enumerate(top_words, start=1):
            writer.writerow([idx, word, count])
