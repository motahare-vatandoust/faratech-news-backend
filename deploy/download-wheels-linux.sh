#!/usr/bin/env bash
# Run on Mac (with internet). Upload wheels-linux/ to server after.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/wheels-linux"
mkdir -p "${OUT}"

pip download -r "${ROOT}/requirements.txt" -d "${OUT}" \
  --platform manylinux2014_x86_64 \
  --platform manylinux_2_17_x86_64 \
  --python-version 3.12 \
  --only-binary=:all:

# SQLAlchemy needs greenlet on Linux; not always pulled by pip download above
pip download greenlet -d "${OUT}" \
  --platform manylinux2014_x86_64 \
  --platform manylinux_2_17_x86_64 \
  --python-version 3.12 \
  --only-binary=:all:

echo "Done: $(ls "${OUT}" | wc -l | tr -d ' ') wheels in ${OUT}"
