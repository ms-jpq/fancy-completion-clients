#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1


mypy --ignore-missing-imports -- clients/*.py clients/**/*.py rplugin/python3/fuzzy_completion_clients/*.py
