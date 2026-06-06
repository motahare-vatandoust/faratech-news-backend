#!/usr/bin/env bash
# Offline install on Iranian VPS. Run from /opt/faratech-news-backend
set -euo pipefail

APP_DIR=/opt/faratech-news-backend
WHEELS_DIR="${APP_DIR}/wheels-linux"

cd "${APP_DIR}"

if [[ ! -d "${WHEELS_DIR}" ]] || [[ -z "$(ls -A "${WHEELS_DIR}" 2>/dev/null)" ]]; then
  echo "Missing ${WHEELS_DIR}. Upload from Mac:"
  echo "  rsync -avz wheels-linux/ ubuntu@SERVER:/opt/faratech-news-backend/wheels-linux/"
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "Missing .env — copy .env.example and edit first."
  exit 1
fi

echo "==> Creating Linux venv..."
rm -rf .venv venv
python3 -m venv .venv

echo "==> Installing from wheels-linux (offline)..."
.venv/bin/pip install --no-index --find-links="${WHEELS_DIR}" -r requirements.txt

echo "==> Running migrations..."
.venv/bin/alembic upgrade head

echo "==> Permissions..."
sudo chown -R www-data:www-data "${APP_DIR}"

echo "==> systemd..."
sudo cp deploy/faratech-api.service /etc/systemd/system/
sudo sed -i 's/--workers 2/--workers 1/' /etc/systemd/system/faratech-api.service
sudo systemctl daemon-reload
sudo systemctl enable faratech-api
sudo systemctl restart faratech-api

sleep 2
if curl -sf http://127.0.0.1:8000/health >/dev/null; then
  echo "API OK: http://127.0.0.1:8000/health"
else
  echo "API failed — check: sudo journalctl -u faratech-api -n 30 --no-pager"
  exit 1
fi

if command -v nginx >/dev/null; then
  echo "==> Nginx..."
  sudo cp deploy/nginx-api.conf /etc/nginx/sites-available/faratech-api
  sudo ln -sf /etc/nginx/sites-available/faratech-api /etc/nginx/sites-enabled/
  sudo rm -f /etc/nginx/sites-enabled/default
  sudo nginx -t && sudo systemctl reload nginx
  echo "Nginx OK"
else
  echo "Install nginx: sudo apt-get install -y nginx"
fi

echo "Done. Test: curl -H 'Host: api.faratech.news' http://127.0.0.1/health"
