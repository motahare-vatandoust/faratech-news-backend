#!/usr/bin/env bash
# Run on the VPS after code + wheels-linux are in /opt/faratech-news-backend
set -euo pipefail

APP_DIR=/opt/faratech-news-backend
WHEELS_DIR="${APP_DIR}/wheels-linux"

cd "${APP_DIR}"

if [[ ! -f .env ]]; then
  echo "ERROR: ${APP_DIR}/.env missing. Create it before running this script."
  exit 1
fi

if [[ ! -d "${WHEELS_DIR}" ]] || [[ -z "$(ls -A "${WHEELS_DIR}"/*.whl 2>/dev/null)" ]]; then
  echo "ERROR: ${WHEELS_DIR} missing or empty. Upload wheels-linux from your Mac first."
  exit 1
fi

echo "==> Creating Linux venv and installing deps offline..."
rm -rf .venv venv
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install --no-index --find-links="${WHEELS_DIR}" -r requirements.txt

echo "==> Running database migrations..."
.venv/bin/alembic upgrade head

echo "==> Installing systemd service..."
sudo cp deploy/faratech-api.service /etc/systemd/system/
sudo sed -i 's/--workers 2/--workers 1/' /etc/systemd/system/faratech-api.service
sudo chown -R www-data:www-data "${APP_DIR}"
sudo systemctl daemon-reload
sudo systemctl enable faratech-api
sudo systemctl restart faratech-api

echo "==> Configuring nginx..."
sudo apt-get install -y nginx
sudo cp deploy/nginx-api.conf /etc/nginx/sites-available/faratech-api
sudo ln -sf /etc/nginx/sites-available/faratech-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx

echo "==> Health checks..."
sleep 2
curl -sf http://127.0.0.1:8000/health
echo ""
curl -sf -H "Host: api.faratech.news" http://127.0.0.1/health
echo ""

sudo systemctl status faratech-api --no-pager
echo ""
echo "Done. Test from your Mac: curl https://api.faratech.news/health"
