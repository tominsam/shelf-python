# wrapper Makefile for py2app invocation and cleaning

PYTHON ?= python

# EVIL EVIL EVIL
VERSION = $(shell grep 'version =' setup.py | cut -d'"' -f 2)

.PHONY: all
all: dist
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

.PHONY: zip
zip:
	cd dist && rm -f Shelf-$(VERSION).zip
	cd dist && zip -r9 Shelf-$(VERSION).zip Shelf.app/
	du -k dist/*.zip

.PHONY: clean
clean:
	rm -rf build dist
