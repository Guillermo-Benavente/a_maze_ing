SHELL := /bin/bash

NAME          := libmlx.so
MLX_TGZ       := mlx_CLXV-2.2.tgz
VENV          := .venv
PYTHON        := $(shell pwd)/$(VENV)/bin/python3
PIP           := $(shell pwd)/$(VENV)/bin/pip

install:
	@echo "Setting up virtual environment..."
	@python3 -m venv $(VENV)
	@$(PYTHON) --version
	@$(PIP) install --upgrade pip > /dev/null 2>&1
	@$(PIP) install pydantic numpy flake8 mypy > /dev/null 2>&1
	$(PIP) install mlx-2.2-py3-none-any.whl 2>&1
	@echo "Done."

run:
	@$(PYTHON) a_maze_ing.py $(filter-out $@, $(MAKECMDGOALS))

%:
	@:

debug:
	@$(PYTHON) -m pdb a_maze_ing.py $(filter-out $@, $(MAKECMDGOALS))

clean:
	@rm -rf __pycache__ .mypy_cache 
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

lint:
	@$(VENV)/bin/mypy . --exclude='\.venv' --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs && \
	$(VENV)/bin/flake8 . --exclude=.venv,__pycache__

lint-strict:
	@$(VENV)/bin/mypy . --exclude='\.venv' --strict && \
  	$(VENV)/bin/flake8 . --exclude=.venv,__pycache__

.PHONY: install run debug clean lint lint-strict