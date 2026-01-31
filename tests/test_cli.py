from __future__ import annotations

from typing import TYPE_CHECKING

from latex_wc import cli

if TYPE_CHECKING:
    from pathlib import Path


def test_parse_args_uses_env_default_document_path(monkeypatch, tmp_path) -> None:
    doc = tmp_path / 'env_default.tex'
    doc.write_text('hello', encoding='utf-8')

    monkeypatch.setenv('DOCUMENT_PATH', str(doc))
    monkeypatch.setattr(cli.sys, 'argv', ['latex-wc'])

    args = cli.parse_args()
    assert args.document_path == str(doc)


def test_validate_inputs_missing_file(tmp_path) -> None:
    missing = tmp_path / 'missing.tex'
    err = cli._validate_inputs(doc_path=missing, top=10, min_len=1)
    assert err is not None
    assert 'document not found' in err


def test_validate_inputs_wrong_suffix(tmp_path) -> None:
    p = tmp_path / 'doc.txt'
    p.write_text('hi', encoding='utf-8')
    err = cli._validate_inputs(doc_path=p, top=10, min_len=1)
    assert err == 'expected a .tex file, got: doc.txt'


def test_validate_inputs_invalid_top_and_min_len(tmp_path) -> None:
    p = tmp_path / 'doc.tex'
    p.write_text('hi', encoding='utf-8')

    assert cli._validate_inputs(doc_path=p, top=0, min_len=1) == '--top must be > 0'
    assert cli._validate_inputs(doc_path=p, top=1, min_len=0) == '--min-len must be > 0'


def test_resolve_out_dir_empty() -> None:
    assert cli._resolve_out_dir('') is None
    assert cli._resolve_out_dir('   ') is not None


def test_main_success_no_out_dir(monkeypatch, tmp_path, capsys) -> None:
    doc = tmp_path / 'doc.tex'
    doc.write_text('does not matter', encoding='utf-8')

    monkeypatch.setattr(cli, 'extract_tokens_from_latex', lambda _tex: ['aa', 'bbb', 'bbb'])

    monkeypatch.setattr(
        cli.sys,
        'argv',
        ['latex-wc', '--document-path', str(doc), '--top', '2', '--min-len', '2'],
    )

    code = cli.main()
    assert code == 0

    captured = capsys.readouterr()
    assert 'Document:' in captured.out
    assert 'Total words: 3' in captured.out
    assert 'Unique words: 2' in captured.out
    assert 'Top 2 words:' in captured.out
    assert 'bbb' in captured.out


def test_main_writes_outputs_when_out_dir_set(monkeypatch, tmp_path, capsys) -> None:
    doc = tmp_path / 'doc.tex'
    doc.write_text('does not matter', encoding='utf-8')
    out_dir = tmp_path / 'out'

    monkeypatch.setattr(cli, 'extract_tokens_from_latex', lambda _tex: ['hello', 'hello', 'world'])
    monkeypatch.setattr(
        cli.sys,
        'argv',
        [
            'latex-wc',
            '--document-path',
            str(doc),
            '--top',
            '10',
            '--min-len',
            '1',
            '--out-dir',
            str(out_dir),
        ],
    )

    code = cli.main()
    assert code == 0

    words_path = out_dir / 'words.txt'
    top_csv_path = out_dir / 'top_words.csv'

    assert words_path.exists()
    assert top_csv_path.exists()

    assert words_path.read_text(encoding='utf-8') == 'hello\nhello\nworld\n'

    captured = capsys.readouterr()
    assert 'Wrote:' in captured.out


def test_main_returns_2_for_missing_document(monkeypatch, tmp_path, capsys) -> None:
    missing = tmp_path / 'missing.tex'

    monkeypatch.setattr(cli.sys, 'argv', ['latex-wc', '--document-path', str(missing)])
    code = cli.main()
    assert code == 2

    captured = capsys.readouterr()
    assert 'Error: document not found' in captured.err


def test_main_returns_2_if_read_fails(monkeypatch, tmp_path, capsys) -> None:
    doc = tmp_path / 'doc.tex'
    doc.write_text('hi', encoding='utf-8')

    def _boom(_path: Path) -> str:
        raise OSError('read failed')

    monkeypatch.setattr(cli, 'read_text_best_effort', _boom)
    monkeypatch.setattr(cli.sys, 'argv', ['latex-wc', '--document-path', str(doc)])

    code = cli.main()
    assert code == 2

    captured = capsys.readouterr()
    assert 'Error: failed to read' in captured.err
