# LaTeX Word Count (Python)

A small CLI tool that counts words in a LaTeX `.tex` file while trying to ignore LaTeX noise:
- removes comments (`% ...`)
- removes common math forms (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`, and common math environments)
- drops common non-content commands (e.g., citations/refs/urls/labels)
- strips LaTeX command names while preserving human-visible brace text
- tokenizes words and reports totals + top-N frequencies

It can also optionally write:
- `words.txt` (one token per line)
- `top_words.csv` (ranked word frequency table)

---

## Requirements

- Python (managed via `uv`)
- `uv` installed on your system

---

## Project Layout

```text
.
├── current_doc.tex           # default input file
├── Makefile                  # common commands
├── pyproject.toml            # dependencies + tooling
├── src/                      # implementation modules
│   ├── cli.py                # CLI entrypoint
│   ├── latex_tokens.py       # LaTeX stripping/tokenization
│   ├── counting.py           # counting + top-N
│   ├── writers.py            # optional output files
│   └── io_utils.py           # read with encoding fallback
└── uv.lock
```

---

## Quick Start

1. Install dependencies:

```bash
make sync
```

2. Run the word counter (defaults to `./current_doc.tex` and `--min-len 4` per the Makefile):

```bash
make main
```

You should see output like:

* Document path
* Total words
* Unique words
* Top-N words

---

## Usage

The Makefile runs the CLI module like this:

```bash
uv run python -m src.cli --document-path ./current_doc.tex --min-len 4
```

You can run it manually as well:

```bash
uv run python -m src.cli --document-path ./current_doc.tex
```

### CLI Arguments

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
uv run python -m src.cli --document-path ./current_doc.tex --top 50 --min-len 4

# Write outputs to ./logs/
uv run python -m src.cli --document-path ./current_doc.tex --out-dir ./logs

# Use environment variables instead of flags
DOCUMENT_PATH=./current_doc.tex LOG_DIR=./logs uv run python -m src.cli
```

---

## Makefile Targets

### `make sync`

Installs/updates dependencies using `uv`:

```bash
make sync
```

### `make lint`

Formats and lints using Ruff, applying safe autofixes:

```bash
make lint
```

### `make main`

Runs the word counter with the Makefile defaults:

```bash
make main
```

---

## Notes / Behavior

* Encoding: reads as UTF-8, falls back to Latin-1 if needed.
* LaTeX handling is heuristic (by design). It aims to approximate “human word count”
  and intentionally drops content associated with references/URLs/etc.
* Tokenization is English-letter oriented (`A-Za-z` with optional apostrophes).
