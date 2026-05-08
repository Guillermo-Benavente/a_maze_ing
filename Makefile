# install:
# run:
# debug:
# clean:
#  rm __pycache__ & .mypy_cache
# lint:
#  flake8 . & mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
# lint-strict:
#  flake8 . & mypy . --strict


NAME    = libmlx.so
LOCAL   = $(HOME)/.local
# Add local paths to environment variables
export CPATH            := $(LOCAL)/include:$(CPATH)
export LIBRARY_PATH     := $(LOCAL)/lib:$(LIBRARY_PATH)
export LD_LIBRARY_PATH  := $(LOCAL)/lib:$(LD_LIBRARY_PATH)
export PKG_CONFIG_PATH  := $(LOCAL)/lib/pkgconfig:$(PKG_CONFIG_PATH)

all: mlx

mlx:
	cd mlx_CLXV && \
	if [ ! -d "xcb-util-keysyms-0.4.1" ]; then \
		wget -q https://xcb.freedesktop.org/dist/xcb-util-keysyms-0.4.1.tar.xz && \
		tar -xf xcb-util-keysyms-0.4.1.tar.xz; \
	fi && \
	cd xcb-util-keysyms-0.4.1 && \
	./configure --prefix=$(LOCAL) && \
	make -j$(shell nproc) && \
	make install && \
	cd .. && \
	./configure.sh && \
	make -j$(shell nproc) && \
	pip install mlx-2.2-py3-none-any.whl && \
	cd .. && \
	cp mlx_CLXV/libmlx.so .

clean:
	rm -rf mlx_CLXV/xcb-util-keysyms-0.4.1
	$(MAKE) -C mlx_CLXV clean

.PHONY: all mlx clean