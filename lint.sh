#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1

FILES=(
  ./rplugin/python3/kok_t9/*.py
  )

mypy --ignore-missing-imports -- "${FILES[@]}"
