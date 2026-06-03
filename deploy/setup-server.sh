#!/usr/bin/env bash
# Run on the Arvan Cloud VPS (Ubuntu/Debian) as root or with sudo.
# Usage: sudo bash deploy/setup-server.sh
set -euo pipefail

APP_DIR=/opt/faratech-news-backend
APP_USER=www-data
DB_NAME=faratech_news
DB_USER=faratech

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Run as root: sudo bash deploy/setup-server.sh"
  exit 1
fi

if [[ -f "${APP_DIR}/deploy/fix-apt-iran.sh" ]]; then
  bash "${APP_DIR}/deploy/fix-apt-iran.sh"
else
  apt-get update
fi
apt-get install -y python3 python3-venv python3-pip git nginx postgresql postgresql-contrib certbot python3-certbot-nginx ufw

# Firewall: SSH + HTTP/HTTPS
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# PostgreSQL role + database (set password when prompted or via env)
if [[ -z "${DB_PASSWORD:-}" ]]; then
  echo "Set DB_PASSWORD before running, e.g.:"
  echo "  export DB_PASSWORD='your-strong-password'"
  echo "  sudo -E bash deploy/setup-server.sh"
  exit 1
fi

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
  END IF;
END
\$\$;
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
\c ${DB_NAME}
GRANT ALL ON SCHEMA public TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER};
SQL

mkdir -p "${APP_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

echo ""
echo "Next steps (as root or deploy user):"
echo "  1. Clone the repo into ${APP_DIR}"
echo "  2. Create ${APP_DIR}/.env (see .env.example)"
echo "  3. cd ${APP_DIR} && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
echo "  4. .venv/bin/alembic upgrade head"
echo "  5. cp deploy/faratech-api.service /etc/systemd/system/ && systemctl daemon-reload && systemctl enable --now faratech-api"
echo "  6. cp deploy/nginx-api.conf /etc/nginx/sites-available/faratech-api"
echo "     ln -sf /etc/nginx/sites-available/faratech-api /etc/nginx/sites-enabled/"
echo "     nginx -t && systemctl reload nginx"
echo "  7. certbot --nginx -d api.faratech.news"
echo ""
