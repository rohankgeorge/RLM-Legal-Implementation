.PHONY: help install install-dev lint format test check run-gui

help:
	@echo "RLM Legal Document Tools"
	@echo ""
	@echo "Usage:"
	@echo "  make install        - Install dependencies"
	@echo "  make install-dev    - Install dev dependencies"
	@echo "  make run-gui        - Launch GUI application"
	@echo ""
	@echo "Development:"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Run ruff formatter"
	@echo "  make test          - Run tests"
	@echo "  make check         - Run lint + format + tests"

install:
	uv sync

install-dev:
	uv sync --group dev --group test

run-gui:
	uv run rlm-legal-gui

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest

check: lint format test
