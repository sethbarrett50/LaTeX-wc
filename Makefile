SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

UV  ?= uv
PY  ?= python
RUFF ?= ruff

DOCUMENT_PATH ?= ./current_doc.tex
LOG_DIR      ?=

.PHONY: help sync test clean \
        sim-bin sim-mc xseciot \
        bin-label merge \
        overall-perf overall-scrape

help: 
	@echo "Targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make sync"
	@echo "  make test"
	@echo "  make main DOCUMENT_PATH=datasets/CEFlows/CEFlows2_merged.csv"

sync: 
	$(UV) sync

lint: ## Lint with ruff and apply safe auto-fixes
	$(UV) run $(RUFF) format .
	$(UV) run $(RUFF) check . --fix

main: ## Runs the main word count
	$(UV) run python -m src.cli \
		--document-path ./current_doc.tex \
		--min-len 4

test: ## Runs a sample version of this script 
	$(UV) run python -m src.cli \
		--document-path ./sample.tex \
		--min-len 4