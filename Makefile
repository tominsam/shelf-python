# wrapper Makefile for py2app invocation and cleaning

PYTHON ?= python

.PHONY: all
all: dev
	@ :

.PHONY: dev
dev:
	$(PYTHON) setup.py py2app -A

.PHONY: dist
dist:
	$(PYTHON) setup.py py2app

.PHONY: clean
clean:
	rm -rf build dist
