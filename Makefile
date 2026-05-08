# install:
# run:
# debug:
# clean:
#  rm __pycache__ & .mypy_cache
# lint:
#  flake8 . & mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
# lint-strict:
#  flake8 . & mypy . --strict


all: mlx

mlx:
	cd mlx_CLXV && \
	wget -q https://xcb.freedesktop.org/dist/xcb-util-keysyms-0.4.1.tar.xz && \
	tar -xf xcb-util-keysyms-0.4.1.tar.xz && \
	cd xcb-util-keysyms-0.4.1 && \
	./configure --prefix=$(HOME)/.local && \
	make && \
	make install && \
	cd .. && \
	sed -i 's/$${CC:-cc} -E -/$${CC:-cc} $$(CFLAGS) -E -/' configure.sh && \
	sed -i 's/$${CC:-cc} -x c - -l$$LIBNAME/$${CC:-cc} $$(LDFLAGS) -x c - -l$$LIBNAME/' configure.sh && \
	CFLAGS="-I$(HOME)/.local/include" LDFLAGS="-L$(HOME)/.local/lib" ./configure.sh && \
	make && \
	cd .. && \
	mv mlx_CLXV/libmlx.so . && \
	cd mlx_CLXV && \
	make clean

.PHONY: all mlx