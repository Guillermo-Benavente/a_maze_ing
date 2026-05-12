SHELL := /bin/bash

NAME          := libmlx.so
MLX_TGZ       := mlx_CLXV-2.2.tgz
VENV          := .venv
PYTHON        := $(shell pwd)/$(VENV)/bin/python3
PIP           := $(shell pwd)/$(VENV)/bin/pip
MLX_SRC       := mlx_src

install:
	@echo "Setting up virtual environment..."
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip > /dev/null 2>&1
	@$(PIP) install pydantic numpy flake8 mypy > /dev/null 2>&1
	@echo "Building MiniLibX..."
	@rm -rf $(MLX_SRC) && mkdir $(MLX_SRC)
	@tar -xf $(MLX_TGZ) -C $(MLX_SRC) --strip-components=1
	@cd $(MLX_SRC) && ./configure.sh > /dev/null 2>&1
	@make -C $(MLX_SRC) libmlx.so > /dev/null 2>&1
	@mkdir -p $(MLX_SRC)/python/src/mlx/
	@cp $(MLX_SRC)/$(NAME) $(MLX_SRC)/python/src/mlx/
	@cd $(MLX_SRC)/python && $(PYTHON) -m pip install . > /dev/null 2>&1
	@cp $(MLX_SRC)/$(NAME) .
	@rm -rf $(MLX_SRC)
	@echo "Done."

run:
	@$(PYTHON) a_maze_ing.py

debug:
	@$(PYTHON) -m pdb a_maze_ing.py

clean:
	@rm -rf __pycache__ .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

lint:
	@$(VENV)/bin/flake8 . --exclude=.venv,__pycache__
	@$(VENV)/bin/mypy . --exclude='\.venv' --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@$(VENV)/bin/flake8 . --exclude=.venv,__pycache__
	@$(VENV)/bin/mypy . --exclude='\.venv' --strict

.PHONY: install run debug clean lint lint-strict