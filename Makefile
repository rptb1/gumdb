# Makefile -- set up working environment etc. for GUMDB
# Richard Brooksby, Ravenbrook Limited, 2018

PYTHON = python3

help:
	@echo 'Makefile for GUMDB'
	@echo
	@echo 'Usage:'
	@echo '  make tools	install Python, libraries, etc.'

tools: tool/bin/pip
	tool/bin/pip install -r requirements.pip

tool/bin/pip:
	virtualenv --python=$(PYTHON) tool

.PHONY: help
