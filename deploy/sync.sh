#!/usr/bin/env bash
# Run from your Mac in the project root. Uploads code and restarts the API on VPS.
set -euo pipefail

SERVER="${DEPLOY_SERVER:-ubuntu@146.19.212.121}"
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

echo "==> Install deps (if wheels present), migrate, ensure 1 worker, restart API..."
ssh "${SERVER}" bash -s <<EOF
set -euo pipefail
cd ${APP_DIR}

if [[ -d wheels-linux ]] && ls wheels-linux/*.whl >/dev/null 2>&1; then
  echo "==> Installing Python deps from wheels-linux (offline)..."
  .venv/bin/pip install --no-index --find-links=wheels-linux -r requirements.txt
else
  echo "WARN: wheels-linux missing/empty — skipping pip install (apscheduler may be absent)."
fi

.venv/bin/python -c 'import apscheduler; print("apscheduler", apscheduler.__version__)'

.venv/bin/alembic upgrade head

sudo cp deploy/nginx-api.conf /etc/nginx/sites-available/faratech-api
sudo nginx -t && sudo systemctl reload nginx

# Auto-crawl lives in-process; multiple uvicorn workers leave status flaky
# and can strand the Postgres leader lock.
sudo cp deploy/faratech-api.service /etc/systemd/system/
sudo sed -i -E 's/--workers [0-9]+/--workers 1/' /etc/systemd/system/faratech-api.service
sudo systemctl daemon-reload

sudo chown -R www-data:www-data ${APP_DIR}
sudo systemctl restart faratech-api
sleep 3
curl -sf http://127.0.0.1:8000/health
echo ""
curl -sf http://127.0.0.1:8000/crawler/status
echo ""
EOF

echo "Done. Test: curl https://api.faratech.news/crawler/status"
