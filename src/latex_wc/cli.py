from __future__ import annotations

import argparse
import os
import sys

from pathlib import Path
from typing import Optional

from .counting import build_result
from .io_utils import read_text_best_effort
from .latex_tokens import extract_tokens_from_latex
from .writers import write_top_words_csv, write_words_txt


def parse_args() -> argparse.Namespace:
    """
    Parse CLI args for the LaTeX word counter.

    Args:
        argv: CLI arguments excluding the program name.

    Returns:
        argparse.Namespace with parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Count words in a LaTeX document, ignoring LaTeX commands/keywords.')
    parser.add_argument(
        '--document-path',
        default=os.environ.get('DOCUMENT_PATH', './current_doc.tex'),
        help='Path to the LaTeX .tex file (defaults to $DOCUMENT_PATH or ./current_doc.tex).',
    )
    parser.add_argument(
        '--top',
        type=int,
        default=100,
        help='Show top N most frequent words (default: 100).',
    )
    parser.add_argument(
        '--min-len',
        type=int,
        default=1,
        help='Minimum token length to include (default: 1).',
    )
    parser.add_argument(
        '--out-dir',
        default=os.environ.get('LOG_DIR', '') or '',
        help=(
            'Optional output directory for words.txt and top_words.csv '
            '(defaults to $LOG_DIR; if empty, no files are written).'
        ),
    )
    return parser.parse_args()


def main() -> int:
    """
    CLI entrypoint.

    Args:
        argv: CLI arguments excluding the program name.

    Returns:
        Process exit code (0 success, 2 user/validation error).
    """
    args = parse_args()

    doc_path = Path(args.document_path).expanduser().resolve()
    error = _validate_inputs(doc_path=doc_path, top=args.top, min_len=args.min_len)
    if error is not None:
        print(f'Error: {error}', file=sys.stderr)
        return 2

    try:
        tex = read_text_best_effort(doc_path)
    except OSError as exc:
        print(f'Error: failed to read {doc_path}: {exc}', file=sys.stderr)
        return 2

    tokens = extract_tokens_from_latex(tex)
    if args.min_len > 1:
        tokens = [t for t in tokens if len(t) >= args.min_len]

    result = build_result(tokens, top_n=args.top)

    _print_report(doc_path=doc_path, top_n=args.top, result=result)

    out_dir = _resolve_out_dir(args.out_dir)
    if out_dir is not None:
        words_path = out_dir / 'words.txt'
        top_csv_path = out_dir / 'top_words.csv'
        write_words_txt(result.tokens, words_path)
        write_top_words_csv(result.top_words, top_csv_path)
        print('')
        print(f'Wrote: {words_path}')
        print(f'Wrote: {top_csv_path}')

    return 0


def _validate_inputs(doc_path: Path, top: int, min_len: int) -> Optional[str]:
    if not doc_path.exists():
        return f'document not found: {doc_path}'
    if doc_path.suffix.lower() != '.tex':
        return f'expected a .tex file, got: {doc_path.name}'
    if top <= 0:
        return '--top must be > 0'
    if min_len <= 0:
        return '--min-len must be > 0'
    return None


def _resolve_out_dir(out_dir: str) -> Optional[Path]:
    if not out_dir:
        return None
    return Path(out_dir).expanduser().resolve()


def _print_report(doc_path: Path, top_n: int, result) -> None:
    print(f'Document: {doc_path}')
    print(f'Total words: {result.total_words}')
    print(f'Unique words: {result.unique_words}')
    print('')
    print(f'Top {top_n} words:')
    for word, count in result.top_words:
        print(f'{word:>20}  {count}')


if __name__ == '__main__':
    raise SystemExit(main())
