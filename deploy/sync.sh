#!/usr/bin/env bash
# Run from your Mac in the project root. Uploads code and restarts the API on VPS.
set -euo pipefail

SERVER="${DEPLOY_SERVER:-ubuntu@95.38.160.122}"
APP_DIR="/opt/faratech-news-backend"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "${ROOT}"

RSYNC_EXCLUDES=(
  --exclude '.venv'
  --exclude 'venv'
  --exclude '__pycache__'
  --exclude '.git'
  --exclude '.env'
)

echo "==> Granting ubuntu write access to ${APP_DIR}..."
ssh "${SERVER}" "sudo chown -R ubuntu:ubuntu ${APP_DIR}"

echo "==> Uploading app to ${SERVER}:${APP_DIR}..."
rsync -avz "${RSYNC_EXCLUDES[@]}" ./ "${SERVER}:${APP_DIR}/"

echo "==> Migrate, reload nginx, restore permissions, restart API..."
ssh "${SERVER}" bash -s <<EOF
set -euo pipefail
cd ${APP_DIR}
.venv/bin/alembic upgrade head
sudo cp deploy/nginx-api.conf /etc/nginx/sites-available/faratech-api
sudo nginx -t && sudo systemctl reload nginx
sudo chown -R www-data:www-data ${APP_DIR}
sudo systemctl restart faratech-api
sleep 2
curl -sf http://127.0.0.1:8000/health
echo ""
EOF

echo "Done. Test: curl https://api.faratech.news/health"
