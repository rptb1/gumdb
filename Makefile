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
	@echo 'To set up environment, run:'
	@echo "    export PATH=\"$$(pwd)/tool/bin:\$$PATH\""

tool/bin/pip:
	virtualenv --python=$(PYTHON) tool

.PHONY: help
