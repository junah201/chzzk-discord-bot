#!/bin/sh -e
set -x
ruff check lambdas shared scripts --fix
ruff format lambdas shared scripts scripts