SHELL := /bin/bash

NAME          := libmlx.so
MLX_TGZ       := mlx_CLXV-2.2.tgz
VENV          := .venv
PYTHON        := $(shell pwd)/$(VENV)/bin/python3
PIP           := $(shell pwd)/$(VENV)/bin/pip
MLX_SRC       := mlx_src

LOCAL   = $(HOME)/.local
export CPATH            := $(LOCAL)/include:$(CPATH)
export LIBRARY_PATH     := $(LOCAL)/lib:$(LIBRARY_PATH)
export LD_LIBRARY_PATH  := $(LOCAL)/lib:$(LD_LIBRARY_PATH)
export PKG_CONFIG_PATH  := $(LOCAL)/lib/pkgconfig:$(PKG_CONFIG_PATH)

install:
	@echo "Setting up virtual environment..."
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip > /dev/null 2>&1
	@$(PIP) install pydantic numpy flake8 mypy > /dev/null 2>&1
	@echo "Building MiniLibX..."
	@rm -rf $(MLX_SRC) && mkdir $(MLX_SRC)
	@tar -xf $(MLX_TGZ) -C $(MLX_SRC) --strip-components=1
	@cd $(MLX_SRC) && \
	if [ ! -d "xcb-util-keysyms-0.4.1" ]; then \
		if [ ! -d "xcb-util-keysyms-0.4.1.tar.xz" ]; then \
			wget -q https://xcb.freedesktop.org/dist/xcb-util-keysyms-0.4.1.tar.xz; \
		fi; \
		tar -xf xcb-util-keysyms-0.4.1.tar.xz; \
	fi; \
	cd xcb-util-keysyms-0.4.1 && \
	./configure --prefix=$(LOCAL) > /dev/null 2>&1 && \
	make -j$(shell nproc) > /dev/null 2>&1 && \
	make install > /dev/null 2>&1 && \
	cd .. && \
	./configure.sh > /dev/null 2>&1
	@make -C $(MLX_SRC) libmlx.so > /dev/null 2>&1
	@mkdir -p $(MLX_SRC)/python/src/mlx/
	@cp $(MLX_SRC)/$(NAME) $(MLX_SRC)/python/src/mlx/
	@cd $(MLX_SRC)/python && $(PYTHON) -m pip install . > /dev/null 2>&1
	@cp $(MLX_SRC)/$(NAME) .
	@rm -rf $(MLX_SRC)
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