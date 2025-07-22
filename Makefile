# Load environment variables
include .env
export

# Define files/folders for formatting and checking
files_to_fmt     ?= app tests
files_to_check   ?= app tests

# Sphinx documentation settings
SPHINX_BUILD     ?= sphinx-build
SPHINX_TEMPLATES ?= ./docs/_templates
SOURCE_DIR       = ./docs
BUILD_DIR        = ./docs/_build

# Default target
.DEFAULT_GOAL := run

.PHONY: fmt chk

# Formatting the code.
fmt: remove_imports isort black docformatter add_trailing_comma

remove_imports:
	autoflake -ir --remove-unused-variables --ignore-init-module-imports --remove-all-unused-imports ${files_to_fmt}

isort:
	isort ${files_to_fmt}

black:
	black ${files_to_fmt}

docformatter:
	find ${files_to_fmt} -name "*.py" -exec docformatter -ir '{}' +

add_trailing_comma:
	find ${files_to_fmt} -name "*.py" -exec add-trailing-comma '{}' \;

# Code quality check.
chk: check

check: flake8 pylint ruff black_check docformatter_check safety bandit mypy

black_check:
	black --check ${files_to_check}

docformatter_check:
	docformatter -cr ${files_to_check}

flake8:
	flake8 ${files_to_check}

pylint:
	pylint ${files_to_check}

ruff:
	ruff ${files_to_check}

mypy:
	mypy ${files_to_check}

safety:
	safety check --full-report

bandit:
	bandit -r ${files_to_check} -x tests