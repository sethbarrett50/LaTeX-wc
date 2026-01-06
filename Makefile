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

fmt: 
	$(UV) run $(RUFF) format .

lint: 
	$(UV) run $(RUFF) check .

lint-fix: ## Lint with ruff and apply safe auto-fixes
	$(UV) run $(RUFF) check . --fix

lint-fix-unsafe: 
	$(UV) run $(RUFF) check . --fix --unsafe-fixes

style: fmt lint

main: ## Runs the main word count
	$(UV) run main.py --document-path $(DOCUMENT_PATH)