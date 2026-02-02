from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from latex_wc.discovery import DEFAULT_EXCLUDE_DIRS, discover_tex_files

if TYPE_CHECKING:
    from pathlib import Path


def test_discover_tex_files_recursively_finds_tex(tmp_path: Path) -> None:
    (tmp_path / 'a.tex').write_text('a', encoding='utf-8')

    sub = tmp_path / 'sub'
    sub.mkdir()
    (sub / 'b.tex').write_text('b', encoding='utf-8')

    (sub / 'c.txt').write_text('c', encoding='utf-8')

    result = discover_tex_files(tmp_path)
    assert [p.name for p in result.files] == ['a.tex', 'b.tex']


def test_discover_tex_files_returns_deterministic_sorted_order(tmp_path: Path) -> None:
    (tmp_path / 'z.tex').write_text('z', encoding='utf-8')
    (tmp_path / 'a.tex').write_text('a', encoding='utf-8')
    (tmp_path / 'm.tex').write_text('m', encoding='utf-8')

    result = discover_tex_files(tmp_path)
    assert [p.name for p in result.files] == ['a.tex', 'm.tex', 'z.tex']


def test_discover_tex_files_matches_case_insensitive_extension(tmp_path: Path) -> None:
    (tmp_path / 'a.TeX').write_text('a', encoding='utf-8')
    (tmp_path / 'b.TEX').write_text('b', encoding='utf-8')
    (tmp_path / 'c.tex').write_text('c', encoding='utf-8')

    result = discover_tex_files(tmp_path)
    assert [p.name for p in result.files] == ['a.TeX', 'b.TEX', 'c.tex']


def test_discover_tex_files_prunes_default_exclude_dirs(tmp_path: Path) -> None:
    assert 'dist' in DEFAULT_EXCLUDE_DIRS

    (tmp_path / 'ok.tex').write_text('ok', encoding='utf-8')

    dist = tmp_path / 'dist'
    dist.mkdir()
    (dist / 'ignored.tex').write_text('ignored', encoding='utf-8')

    build = tmp_path / 'build'
    build.mkdir()
    (build / 'ignored2.tex').write_text('ignored2', encoding='utf-8')

    result = discover_tex_files(tmp_path)
    assert [p.name for p in result.files] == ['ok.tex']


def test_discover_tex_files_prunes_dot_directories(tmp_path: Path) -> None:
    (tmp_path / 'ok.tex').write_text('ok', encoding='utf-8')

    hidden = tmp_path / '.hidden'
    hidden.mkdir()
    (hidden / 'ignored.tex').write_text('ignored', encoding='utf-8')

    git = tmp_path / '.git'
    git.mkdir()
    (git / 'ignored2.tex').write_text('ignored2', encoding='utf-8')

    result = discover_tex_files(tmp_path)
    assert [p.name for p in result.files] == ['ok.tex']


def test_discover_tex_files_allows_custom_exclude_dirs(tmp_path: Path) -> None:
    (tmp_path / 'ok.tex').write_text('ok', encoding='utf-8')

    sub = tmp_path / 'sub'
    sub.mkdir()
    (sub / 'skip.tex').write_text('skip', encoding='utf-8')

    result = discover_tex_files(tmp_path, exclude_dirs=('sub',))
    assert [p.name for p in result.files] == ['ok.tex']


def test_discover_tex_files_raises_if_root_is_not_directory(tmp_path: Path) -> None:
    file_path = tmp_path / 'not_a_dir.tex'
    file_path.write_text('x', encoding='utf-8')

    with pytest.raises(NotADirectoryError):
        discover_tex_files(file_path)


def test_discover_tex_files_returns_resolved_paths(tmp_path: Path) -> None:
    (tmp_path / 'a.tex').write_text('a', encoding='utf-8')

    result = discover_tex_files(tmp_path)
    assert len(result.files) == 1
    assert result.files[0].is_absolute()
    assert result.files[0] == (tmp_path / 'a.tex').resolve()
