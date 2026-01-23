.PHONY: help lint format type test check clean build install

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

lint:  ## Run ruff linter
	uv run ruff check src tests

format:  ## Format code with ruff
	uv run ruff format src tests

type:  ## Run pyright type checker
	uv run pyright src

test:  ## Run pytest
	uv run pytest

check: lint type test  ## Run all checks (lint + type + test)

clean:  ## Remove build artifacts
	rm -rf dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

build:  ## Build distribution packages
	uv build

install:  ## Install in development mode
	uv sync --all-extras
