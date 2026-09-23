#!/usr/bin/env bash
# Fail if Community catalogs or playbooks were copied into the overlay tree.
# The community/ submodule is the allowed copy and is not searched.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${root}"

matches="$(
  find . \
    \( -path ./.git -o -path ./community -o -path ./.venv \) -prune \
    -o -type d \( -name oscal -o -path '*/ansible/playbooks' \) -print
)"

if [[ -n "${matches}" ]]; then
  echo "Open-core check failed. Do not copy oscal/ or ansible/playbooks outside community/:" >&2
  echo "${matches}" >&2
  exit 1
fi

echo "open-core check ok"
