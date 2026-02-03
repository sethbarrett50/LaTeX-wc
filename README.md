# `latex-wc`

A small CLI tool that counts words in LaTeX `.tex` files while trying to ignore LaTeX “noise”:

- Removes comments (`% ...`)
- Removes common math forms (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`, and common math environments)
- Drops common non-content commands (e.g., citations/refs/urls/labels)
- Strips LaTeX command names while preserving human-visible brace text
- Tokenizes words and reports totals + top-N frequencies

Optionally writes:
- `words.txt` (one token per line)
- `top_words.csv` (ranked word frequency table)

> Heuristic by design: the goal is a *human-ish* word count, not a TeX-perfect parse.

---

## Install (recommended: isolated CLI via `uv` / `pipx`)

**Distribution name:** `latex-word-count`  
**CLI command:** `latex-wc`  
**Import package:** `latex_wc`

### Option A: One-off run with `uvx` (no install)

```bash
uvx latex-wc ./paper.tex
```

If you want directory recursion:

```bash
uvx latex-wc ./tex/
```

### Option B: Install as a persistent tool with `uv`

```bash
uv tool install latex-wc
latex-wc ./paper.tex
```

Upgrade later:

```bash
uv tool upgrade latex-wc
```

### Option C: Install as a persistent tool with `pipx`

```bash
pipx install latex-wc
latex-wc ./paper.tex
```

Upgrade later:

```bash
pipx upgrade latex-wc
```

---

## Usage

### Basic

Pass either a **file** or a **directory**:

```bash
latex-wc ./paper.tex
latex-wc ./thesis/     # recursively counts all *.tex under ./thesis (one combined report)
```

### Backwards-compatible flag

`--document-path` is still supported (positional `PATH` wins if both are provided):

```bash
latex-wc --document-path ./paper.tex
latex-wc ./paper.tex --document-path ./ignored.tex
```

### Arguments

* `PATH` (positional, optional)
  Path to a `.tex` file or a directory.
  If omitted: uses `$DOCUMENT_PATH` or searches the current directory recursively.

* `--top N`
  Number of top words to display.
  Default: `100`

* `--min-len N`
  Minimum token length to include.
  Default: `1`

* `--out-dir DIR`
  If set, writes `words.txt` and `top_words.csv` into this directory.
  Default: `$LOG_DIR` if set; if empty, nothing is written.

* `--debug`
  Enables verbose debug logging to **stderr** (stdout remains the main report output).

### Examples

```bash
# Count words, show top 50, ignore tokens shorter than 4 chars
latex-wc ./paper.tex --top 50 --min-len 4

# Count all .tex files under a directory (combined report)
latex-wc ./tex/ --top 25

# Write outputs to ./logs/
latex-wc ./paper.tex --out-dir ./logs

# Use env vars (no args)
DOCUMENT_PATH=./paper.tex LOG_DIR=./logs latex-wc

# Verbose debug logs
latex-wc ./paper.tex --debug
```

---

## Output

The CLI prints:

* Document path (file mode) **or** directory + number of files (directory mode)
* Total words
* Unique words
* Top-N word frequency list

If `--out-dir` is set, two files are written:

* `words.txt` — one token per line
* `top_words.csv` — `rank,word,count`

---

## Development (repo)

This section is for contributors; most users should use `uvx`, `uv tool`, or `pipx` above.

Requirements:

* Python `>=3.11`
* `uv`

Common commands:

```bash
make sync
make test
make lint
make build
```

Project layout:

```text
.
├── src/
│   └── latex_wc/
│       ├── cli.py
│       ├── discovery.py
│       ├── latex_tokens.py
│       ├── counting.py
│       ├── writers.py
│       ├── io_utils.py
│       └── models.py
└── tests/
```