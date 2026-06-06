#!/usr/bin/env bash
# Run from your Mac in the project root. Uploads code + wheels, runs finish-setup on VPS.
set -euo pipefail

SERVER="${DEPLOY_SERVER:-ubuntu@95.38.160.122}"
APP_DIR="/opt/faratech-news-backend"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "${ROOT}"

if [[ ! -d wheels-linux ]] || [[ -z "$(ls -A wheels-linux/*.whl 2>/dev/null)" ]]; then
  echo "Downloading Linux wheels..."
  mkdir -p wheels-linux
  pip download -r requirements.txt -d wheels-linux \
    --platform manylinux2014_x86_64 \
    --platform manylinux_2_17_x86_64 \
    --python-version 3.12 \
    --only-binary=:all:
fi

echo "==> Uploading app to ${SERVER}:${APP_DIR}..."
rsync -avz --progress \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude 'wheels' \
  ./ "${SERVER}:${APP_DIR}/"

if [[ -f .env ]]; then
  echo "==> Uploading .env..."
  rsync -avz .env "${SERVER}:${APP_DIR}/.env"
else
  echo "WARN: No local .env — ensure ${APP_DIR}/.env exists on the server."
fi

echo "==> Running finish-setup on server..."
ssh "${SERVER}" "sudo mkdir -p ${APP_DIR} && sudo chown -R ubuntu:ubuntu ${APP_DIR} && bash ${APP_DIR}/deploy/finish-setup.sh"
