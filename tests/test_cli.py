from __future__ import annotations

from typing import TYPE_CHECKING

from latex_wc import cli

if TYPE_CHECKING:
    from pathlib import Path


def test_parse_args_debug_flag() -> None:
    args = cli.parse_args(['--debug'])
    assert args.debug is True


def test_resolve_input_path_uses_env_document_path_when_no_args(monkeypatch, tmp_path: Path) -> None:
    doc = tmp_path / 'env_default.tex'
    doc.write_text('hello', encoding='utf-8')

    monkeypatch.setenv('DOCUMENT_PATH', str(doc))

    resolved = cli._resolve_input_path(positional=None, document_path=None)
    assert resolved == doc.expanduser().resolve()


def test_resolve_input_path_prefers_positional_over_document_path(monkeypatch, tmp_path: Path) -> None:
    doc1 = tmp_path / 'a.tex'
    doc2 = tmp_path / 'b.tex'
    doc1.write_text('a', encoding='utf-8')
    doc2.write_text('b', encoding='utf-8')

    monkeypatch.setenv('DOCUMENT_PATH', str(doc1))

    resolved = cli._resolve_input_path(positional=str(doc2), document_path=str(doc1))
    assert resolved == doc2.expanduser().resolve()


def test_validate_common_inputs_invalid_top_and_min_len() -> None:
    assert cli._validate_common_inputs(top=0, min_len=1) == '--top must be > 0'
    assert cli._validate_common_inputs(top=1, min_len=0) == '--min-len must be > 0'


def test_validate_common_inputs_ok() -> None:
    assert cli._validate_common_inputs(top=1, min_len=1) is None


def test_resolve_out_dir_empty() -> None:
    assert cli._resolve_out_dir('') is None


def test_resolve_out_dir_non_empty(tmp_path: Path) -> None:
    out = cli._resolve_out_dir(str(tmp_path))
    assert out == tmp_path.expanduser().resolve()


def test_main_success_file_no_out_dir(monkeypatch, tmp_path: Path, capsys) -> None:
    doc = tmp_path / 'doc.tex'
    doc.write_text('does not matter', encoding='utf-8')

    monkeypatch.setattr(cli, 'extract_tokens_from_latex', lambda _tex: ['aa', 'bbb', 'bbb'])

    code = cli.main([str(doc), '--top', '2', '--min-len', '2'])
    assert code == 0

    captured = capsys.readouterr()
    assert 'Document:' in captured.out
    assert 'Total words: 3' in captured.out
    assert 'Unique words: 2' in captured.out
    assert 'Top 2 words:' in captured.out
    assert 'bbb' in captured.out


def test_main_success_directory_aggregates(monkeypatch, tmp_path: Path, capsys) -> None:
    d = tmp_path / 'paper'
    d.mkdir()
    (d / 'a.tex').write_text('a', encoding='utf-8')
    (d / 'b.tex').write_text('b', encoding='utf-8')

    monkeypatch.setattr(cli, 'extract_tokens_from_latex', lambda _tex: ['word'])

    code = cli.main([str(d), '--top', '10'])
    assert code == 0

    captured = capsys.readouterr()
    assert 'Directory:' in captured.out
    assert 'Files: 2' in captured.out
    assert 'Total words: 2' in captured.out
    assert 'Unique words:' in captured.out


def test_main_writes_outputs_when_out_dir_set(monkeypatch, tmp_path: Path, capsys) -> None:
    doc = tmp_path / 'doc.tex'
    doc.write_text('does not matter', encoding='utf-8')

    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    monkeypatch.setattr(cli, 'extract_tokens_from_latex', lambda _tex: ['hello', 'hello', 'world'])

    code = cli.main([str(doc), '--top', '10', '--min-len', '1', '--out-dir', str(out_dir)])
    assert code == 0

    words_path = out_dir / 'words.txt'
    top_csv_path = out_dir / 'top_words.csv'

    assert words_path.exists()
    assert top_csv_path.exists()

    assert words_path.read_text(encoding='utf-8') == 'hello\nhello\nworld\n'

    captured = capsys.readouterr()
    assert 'Wrote:' in captured.out


def test_main_returns_2_for_missing_path(tmp_path: Path, capsys) -> None:
    missing = tmp_path / 'missing.tex'

    code = cli.main([str(missing)])
    assert code == 2

    captured = capsys.readouterr()
    assert 'Error: path not found:' in captured.err


def test_main_returns_2_if_read_fails(monkeypatch, tmp_path: Path, capsys) -> None:
    doc = tmp_path / 'doc.tex'
    doc.write_text('hi', encoding='utf-8')

    def _boom(_path: Path) -> str:
        raise OSError('read failed')

    monkeypatch.setattr(cli, 'read_text_best_effort', _boom)

    code = cli.main([str(doc)])
    assert code == 2

    captured = capsys.readouterr()
    assert 'Warning: failed to read' in captured.err
    assert 'Error: no tokens extracted' in captured.err
