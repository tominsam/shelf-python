# wrapper Makefile for py2app invocation and cleaning

PYTHON ?= python

.PHONY: all
all: dev
	@ :

.PHONY: dev
dev:
	@echo -
	@echo - dev build will not work under Snow Leopard unless you\'ve fixed your local build!!
	@echo -
	$(PYTHON) setup.py py2app -A

.PHONY: dist
dist:
	$(PYTHON) setup.py py2app

.PHONY: clean
clean:
	rm -rf build dist
