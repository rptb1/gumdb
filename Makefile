# Makefile -- set up working environment etc. for GUMDB
#
# Grand Unified Mail Database
# Copyright (C) 2018 Richard Brooksby
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
