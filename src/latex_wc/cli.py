from __future__ import annotations

import argparse
import logging
import os
import sys

from pathlib import Path
from typing import Optional, Sequence

from .counting import build_result
from .discovery import discover_tex_files
from .io_utils import read_text_best_effort
from .latex_tokens import extract_tokens_from_latex
from .writers import write_top_words_csv, write_words_txt

LOGGER_NAME = 'latex_wc'


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """
    Parse CLI args for the LaTeX word counter.

    PATH (positional) may be:
      - a .tex file
      - a directory (recursively searches for *.tex)
      - omitted (use $DOCUMENT_PATH if set, else search cwd)
    """
    parser = argparse.ArgumentParser(description='Count words in LaTeX .tex file(s), ignoring LaTeX commands/keywords.')

    parser.add_argument(
        'path',
        nargs='?',
        default=None,
        help=('Optional path to a .tex file or a directory. If omitted, uses $DOCUMENT_PATH or searches cwd.'),
    )

    parser.add_argument(
        '--document-path',
        default=None,
        help='Path to a LaTeX .tex file (optional; overridden by positional PATH if provided).',
    )

    parser.add_argument('--top', type=int, default=100, help='Show top N most frequent words (default: 100).')
    parser.add_argument('--min-len', type=int, default=1, help='Minimum token length to include (default: 1).')

    parser.add_argument(
        '--out-dir',
        default=os.environ.get('LOG_DIR', '') or '',
        help=(
            'Optional output directory for words.txt and top_words.csv '
            '(defaults to $LOG_DIR; if empty, no files are written).'
        ),
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable verbose debug logging.',
    )

    return parser.parse_args(argv)


def _configure_logging(debug: bool) -> logging.Logger:
    """
    Configure logging for CLI execution.

    - INFO by default, DEBUG with --debug
    - Logs to stderr (so stdout remains the report output)
    """
    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        return logger

    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
    return logger


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    CLI entrypoint.

    Returns:
        Process exit code (0 success, 2 user/validation error).
    """
    args = parse_args(argv)
    logger = _configure_logging(debug=args.debug)

    logger.debug('Args parsed: %s', args)

    error = _validate_common_inputs(top=args.top, min_len=args.min_len)
    if error is not None:
        logger.error(error)
        print(f'Error: {error}', file=sys.stderr)
        return 2

    try:
        input_path = _resolve_input_path(args.path, args.document_path)
    except ValueError as exc:
        logger.error('Failed to resolve input path: %s', exc)
        print(f'Error: {exc}', file=sys.stderr)
        return 2

    logger.info('Input: %s', input_path)

    try:
        tex_files = _resolve_tex_files(input_path, logger=logger)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        logger.error('%s', exc)
        print(f'Error: {exc}', file=sys.stderr)
        return 2

    logger.info('Tex files: %d', len(tex_files))
    logger.debug('Tex file list:\n%s', '\n'.join(str(p) for p in tex_files))

    tokens: list[str] = []
    read_failures: list[str] = []

    for idx, p in enumerate(tex_files, start=1):
        logger.debug('Reading file %d/%d: %s', idx, len(tex_files), p)

        try:
            tex = read_text_best_effort(p)
        except OSError as exc:
            msg = f'{p}: {exc}'
            read_failures.append(msg)
            logger.warning('Failed to read: %s', msg)
            if args.debug:
                logger.exception('Read exception for %s', p)
            continue

        file_tokens = extract_tokens_from_latex(tex)
        logger.debug('Extracted %d raw tokens from %s', len(file_tokens), p.name)

        if args.min_len > 1:
            before = len(file_tokens)
            file_tokens = [t for t in file_tokens if len(t) >= args.min_len]
            logger.debug(
                'Applied min-len=%d to %s: %d -> %d tokens',
                args.min_len,
                p.name,
                before,
                len(file_tokens),
            )

        tokens.extend(file_tokens)

    if read_failures:
        logger.warning('Read failures: %d', len(read_failures))
        for msg in read_failures:
            print(f'Warning: failed to read {msg}', file=sys.stderr)

    if not tokens:
        logger.error('No tokens extracted from any readable .tex file.')
        print('Error: no tokens extracted (no readable .tex files found?)', file=sys.stderr)
        return 2

    logger.info('Total tokens (combined): %d', len(tokens))

    result = build_result(tokens, top_n=args.top)
    logger.debug(
        'Result built: total_words=%d unique_words=%d top_n=%d',
        result.total_words,
        result.unique_words,
        args.top,
    )

    _print_report(input_path=input_path, tex_files=tex_files, top_n=args.top, result=result)

    out_dir = _resolve_out_dir(args.out_dir)
    if out_dir is not None:
        logger.info('Writing outputs to: %s', out_dir)
        words_path = out_dir / 'words.txt'
        top_csv_path = out_dir / 'top_words.csv'

        try:
            write_words_txt(result.tokens, words_path)
            write_top_words_csv(result.top_words, top_csv_path)
        except OSError as exc:
            logger.error('Failed writing outputs: %s', exc)
            if args.debug:
                logger.exception('Output write exception')
            print(f'Error: failed writing outputs: {exc}', file=sys.stderr)
            return 2

        print('')
        print(f'Wrote: {words_path}')
        print(f'Wrote: {top_csv_path}')

    return 0


def _validate_common_inputs(top: int, min_len: int) -> Optional[str]:
    if top <= 0:
        return '--top must be > 0'
    if min_len <= 0:
        return '--min-len must be > 0'
    return None


def _resolve_input_path(positional: Optional[str], document_path: Optional[str]) -> Path:
    """
    Precedence:
      1) positional PATH
      2) --document-path
      3) $DOCUMENT_PATH
      4) cwd (directory)
    """
    if positional:
        return Path(positional).expanduser().resolve()

    if document_path:
        return Path(document_path).expanduser().resolve()

    env_doc = os.environ.get('DOCUMENT_PATH')
    if env_doc:
        return Path(env_doc).expanduser().resolve()

    return Path.cwd().resolve()


def _resolve_tex_files(input_path: Path, logger: logging.Logger) -> tuple[Path, ...]:
    """
    If input_path is a file, it must be a .tex file.
    If it is a directory, discover all *.tex recursively.
    """
    if not input_path.exists():
        raise FileNotFoundError(f'path not found: {input_path}')

    if input_path.is_file():
        if input_path.suffix.lower() != '.tex':
            raise ValueError(f'expected a .tex file, got: {input_path.name}')
        logger.debug('Single file mode: %s', input_path)
        return (input_path,)

    logger.debug('Directory mode discovery: %s', input_path)
    discovery = discover_tex_files(input_path)
    if not discovery.files:
        raise ValueError(f'no .tex files found under: {input_path}')

    logger.debug('Discovery returned %d files', len(discovery.files))
    return discovery.files


def _resolve_out_dir(out_dir: str) -> Optional[Path]:
    if not out_dir:
        return None
    return Path(out_dir).expanduser().resolve()


def _print_report(input_path: Path, tex_files: Sequence[Path], top_n: int, result) -> None:
    if input_path.is_dir():
        print(f'Directory: {input_path}')
        print(f'Files: {len(tex_files)}')
    else:
        print(f'Document: {input_path}')

    print(f'Total words: {result.total_words}')
    print(f'Unique words: {result.unique_words}')
    print('')
    print(f'Top {top_n} words:')
    for word, count in result.top_words:
        print(f'{word:>20}  {count}')


if __name__ == '__main__':
    raise SystemExit(main())
