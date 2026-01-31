from __future__ import annotations

import re

from typing import List

_LATEX_COMMENT_RE = re.compile(r'(?<!\\)%.*$')

_LATEX_COMMAND_RE = re.compile(
    r"""
    \\                                  # leading backslash
    [a-zA-Z@]+[*]?                      # command name (+ optional *)
    (?:\s*\[[^\]]*\])?                  # optional [options]
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

_BEGIN_END_TAG_RE = re.compile(r'\\(?:begin|end)\{[^}]+\}')

_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def extract_tokens_from_latex(tex: str) -> List[str]:
    """
    Extract lowercase word tokens from a LaTeX document string.

    This attempts to count "human words" by:
    - removing comments,
    - removing math (inline/display/environments),
    - removing citations/refs/urls/etc. via a drop-list,
    - stripping \\begin{...}/\\end{...} tags,
    - removing command names while keeping brace text,
    - cleaning braces and control characters,
    - tokenizing A–Z words (optionally with apostrophes).

    Args:
        tex: Raw LaTeX content.

    Returns:
        List of lowercase tokens.
    """
    tex = _strip_comments(tex)
    tex = _remove_math(tex)
    tex = _remove_drop_commands(tex)
    tex = _remove_begin_end_tags(tex)
    tex = _remove_commands_keep_text(tex)
    tex = _cleanup_braces_and_controls(tex)
    return [t.lower() for t in _TOKEN_RE.findall(tex)]


def _strip_comments(tex: str) -> str:
    lines: List[str] = []
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

    Examples:
        \\section{Intro} -> {Intro}
        \\textbf{Hello}  -> {Hello}
        \\LaTeX          -> (removed)
    """
    return _LATEX_COMMAND_RE.sub(' ', tex)


def _cleanup_braces_and_controls(tex: str) -> str:
    tex = tex.replace('{', ' ').replace('}', ' ')
    tex = tex.replace('~', ' ')
    tex = tex.replace('\\', ' ')
    return tex
