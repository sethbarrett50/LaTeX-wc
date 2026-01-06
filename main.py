from __future__ import annotations

import argparse
import csv
import os
import re
import sys

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class WordCountResult:
    total_words: int
    unique_words: int
    top_words: List[tuple[str, int]]
    tokens: List[str]


_LATEX_COMMENT_RE = re.compile(r'(?<!\\)%.*$')
_LATEX_COMMAND_RE = re.compile(
    r"""
    \\                                  
    [a-zA-Z@]+[*]?                       
    (?:\s*\[[^\]]*\])?                  
    """,
    re.VERBOSE,
)

_DROP_COMMANDS = (
    'cite',
    'citet',
    'citep',
    'citeauthor',
    'citeyear',
    'ref',
    'eqref',
    'pageref',
    'autoref',
    'cref',
    'Cref',
    'label',
    'url',
    'href',
    'footnote',
)

_DROP_COMMANDS_RE = re.compile(
    r'\\(?:' + '|'.join(re.escape(cmd) for cmd in _DROP_COMMANDS) + r')\*?(?:\s*\[[^\]]*\])?\s*\{[^}]*\}',
    re.DOTALL,
)

_INLINE_DOLLAR_MATH_RE = re.compile(r'\$(?:\\.|[^$\\])*\$')
_DISPLAY_DOLLAR_MATH_RE = re.compile(r'\$\$(?:\\.|[^$\\])*\$\$', re.DOTALL)
_PAREN_MATH_RE = re.compile(r'\\\((?:\\.|[^\\])*\s*\\\)', re.DOTALL)
_BRACKET_MATH_RE = re.compile(r'\\\[(?:\\.|[^\\])*\s*\\\]', re.DOTALL)
_MATH_ENV_RE = re.compile(
    r'\\begin\{(?:equation|align|align\*|equation\*|gather|gather\*|multline|multline\*)\}'
    r'.*?'
    r'\\end\{(?:equation|align|align\*|equation\*|gather|gather\*|multline|multline\*)\}',
    re.DOTALL,
)

_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

_BEGIN_END_TAG_RE = re.compile(r'\\(?:begin|end)\{[^}]+\}')


def _strip_comments(tex: str) -> str:
    lines = []
    for line in tex.splitlines():
        lines.append(_LATEX_COMMENT_RE.sub('', line))
    return '\n'.join(lines)


def _remove_math(tex: str) -> str:
    tex = _MATH_ENV_RE.sub(' ', tex)
    tex = _DISPLAY_DOLLAR_MATH_RE.sub(' ', tex)
    tex = _INLINE_DOLLAR_MATH_RE.sub(' ', tex)
    tex = _PAREN_MATH_RE.sub(' ', tex)
    tex = _BRACKET_MATH_RE.sub(' ', tex)
    return tex


def _remove_drop_commands(tex: str) -> str:
    return _DROP_COMMANDS_RE.sub(' ', tex)


def _remove_begin_end_tags(tex: str) -> str:
    return _BEGIN_END_TAG_RE.sub(' ', tex)


def _remove_commands_keep_text(tex: str) -> str:
    """
    Remove LaTeX command names while keeping any following brace content.

    Example:
      \\section{Intro}  -> {Intro}
      \textbf{Hello}   -> {Hello}
      \\LaTeX           -> (removed)
    """
    return _LATEX_COMMAND_RE.sub(' ', tex)


def _cleanup_braces_and_controls(tex: str) -> str:
    tex = tex.replace('{', ' ').replace('}', ' ')
    tex = tex.replace('~', ' ')
    tex = tex.replace('\\', ' ')
    return tex


def extract_tokens_from_latex(tex: str) -> List[str]:
    tex = _strip_comments(tex)
    tex = _remove_math(tex)
    tex = _remove_drop_commands(tex)
    tex = _remove_begin_end_tags(tex)
    tex = _remove_commands_keep_text(tex)
    tex = _cleanup_braces_and_controls(tex)

    tokens = [t.lower() for t in _TOKEN_RE.findall(tex)]
    return tokens


def count_words(tokens: Iterable[str], top_n: int) -> tuple[int, int, List[tuple[str, int]]]:
    counter = Counter(tokens)
    total = sum(counter.values())
    unique = len(counter)
    top_words = counter.most_common(top_n)
    return total, unique, top_words


def write_words_txt(tokens: List[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(tokens) + '\n', encoding='utf-8')


def write_top_words_csv(top_words: List[tuple[str, int]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['rank', 'word', 'count'])
        for idx, (word, count) in enumerate(top_words, start=1):
            writer.writerow([idx, word, count])


def parse_args(argv: List[str]) -> argparse.Namespace:
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
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    doc_path = Path(args.document_path).expanduser().resolve()
    if not doc_path.exists():
        print(f'Error: document not found: {doc_path}', file=sys.stderr)
        return 2
    if doc_path.suffix.lower() != '.tex':
        print(f'Error: expected a .tex file, got: {doc_path.name}', file=sys.stderr)
        return 2
    if args.top <= 0:
        print('Error: --top must be > 0', file=sys.stderr)
        return 2
    if args.min_len <= 0:
        print('Error: --min-len must be > 0', file=sys.stderr)
        return 2

    try:
        tex = doc_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        tex = doc_path.read_text(encoding='latin-1')

    tokens = extract_tokens_from_latex(tex)
    if args.min_len > 1:
        tokens = [t for t in tokens if len(t) >= args.min_len]

    total, unique, top_words = count_words(tokens, top_n=args.top)

    print(f'Document: {doc_path}')
    print(f'Total words: {total}')
    print(f'Unique words: {unique}')
    print('')
    print(f'Top {args.top} words:')
    for word, count in top_words:
        print(f'{word:>20}  {count}')

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else None
    if out_dir is not None:
        words_path = out_dir / 'words.txt'
        top_csv_path = out_dir / 'top_words.csv'
        write_words_txt(tokens, words_path)
        write_top_words_csv(top_words, top_csv_path)
        print('')
        print(f'Wrote: {words_path}')
        print(f'Wrote: {top_csv_path}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
