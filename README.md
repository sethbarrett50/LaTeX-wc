# LaTeX Word Count

A small CLI tool that counts words in a LaTeX `.tex` file while trying to ignore LaTeX “noise”:

- Removes comments (`% ...`)
- Removes common math forms (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`, and common math environments)
- Drops common non-content commands (e.g., citations/refs/urls/labels)
- Strips LaTeX command names while preserving human-visible brace text
- Tokenizes words and reports totals + top-N frequencies

It can also optionally write:
- `words.txt` (one token per line)
- `top_words.csv` (ranked word frequency table)

> Heuristic by design: the goal is a *human-ish* word count, not a TeX-perfect parse.

---

## Install (PyPI)

This project is designed to be used as an **isolated CLI tool** via `uv`.

### One-off run (no project setup)

```bash
uvx latex-wc --document-path ./paper.tex
```

### Install as a persistent tool

```bash
uv tool install latex-wc
latex-wc --document-path ./paper.tex
```

> Distribution name: `latex-word-count`
> CLI command: `latex-wc`
> Import package: `latex_wc`

---

## Usage

### Basic

```bash
latex-wc --document-path ./paper.tex
```

### Arguments

* `--document-path`
  Path to the `.tex` file.
  Default: `$DOCUMENT_PATH` if set, otherwise `./current_doc.tex`.

* `--top`
  Number of top words to display.
  Default: `100`.

* `--min-len`
  Minimum token length to include.
  Default: `1`.

* `--out-dir`
  If set, writes `words.txt` and `top_words.csv` into this directory.
  Default: `$LOG_DIR` if set; if empty, nothing is written.

Examples:

```bash
# Count words, show top 50, ignore tokens shorter than 4 chars
latex-wc --document-path ./paper.tex --top 50 --min-len 4

# Write outputs to ./logs/
latex-wc --document-path ./paper.tex --out-dir ./logs

# Use environment variables instead of flags
DOCUMENT_PATH=./paper.tex LOG_DIR=./logs latex-wc
```

---

## Output

The CLI prints:

* Document path
* Total words
* Unique words
* Top-N word frequency list

If `--out-dir` is set, two files are written:

* `words.txt` — one token per line
* `top_words.csv` — `rank,word,count`

---

## Build / Local Development

### Requirements

* Python `>=3.11`
* [`uv`](https://docs.astral.sh/uv/) installed

### Sync deps

```bash
make sync
```

### Run locally (repo version)

```bash
make run
```

Or test against the included sample:

```bash
make sample
```

### Lint / Format

```bash
make lint
```

### Tests

```bash
make test
```

### Build artifacts (wheel + sdist)

```bash
make build
```

### Preflight checks (build + metadata)

```bash
make preflight
```

---

## Using a local build in another repo (preflight install)

After building in this repo (`make build`), you can install the wheel or sdist into any other directory using uv only.

From the other repo:

```bash
uv init --layout=bare
uv add /ABS/PATH/TO/dist/latex_word_count-0.1.0-py3-none-any.whl
uv run -- latex-wc --document-path ./paper.tex
```

You can also install the sdist:

```bash
uv add /ABS/PATH/TO/dist/latex_word_count-0.1.0.tar.gz
```

---

## Project Layout

```text
.
├── current_doc.tex
├── Makefile
├── pyproject.toml
├── src/
│   └── latex_wc/
│       ├── cli.py
│       ├── latex_tokens.py
│       ├── counting.py
│       ├── writers.py
│       ├── io_utils.py
│       └── models.py
├── tests/
└── uv.lock
```

---

## Notes / Behavior

* Encoding: reads as UTF-8, falls back to Latin-1 if needed.
* LaTeX handling is heuristic (by design). It aims to approximate a human word count and intentionally drops
  some content associated with references/URLs/etc.
* Tokenization is English-letter oriented (`A-Za-z` with optional apostrophes).