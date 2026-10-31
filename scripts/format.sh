#!/bin/sh -e
set -x
uv run ruff check lambdas --fix
uv run ruff format lambdas