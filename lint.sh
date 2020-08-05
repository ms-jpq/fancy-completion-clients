#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1

FILES=(
  ./rplugin/python3/nap_clients/*.py
  ./rplugin/python3/nap_clients/**/*.py
  )

mypy --ignore-missing-imports -- "${FILES[@]}"
