#!/usr/bin/env bash
# Create PostgreSQL user/database only (skip apt).
# Usage: export DB_PASSWORD='...'; sudo -E bash deploy/setup-db-only.sh
set -euo pipefail

DB_NAME=faratech_news
DB_USER=faratech

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Run as root: sudo -E bash deploy/setup-db-only.sh"
  exit 1
fi

if [[ -z "${DB_PASSWORD:-}" ]]; then
  echo "export DB_PASSWORD='your-strong-password'"
  exit 1
fi

if ! systemctl is-active --quiet postgresql 2>/dev/null; then
  echo "PostgreSQL is not running. Install it first:"
  echo "  sudo bash deploy/fix-apt-iran.sh"
  echo "  sudo apt-get install -y postgresql postgresql-contrib"
  exit 1
fi

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
  ELSE
    ALTER ROLE ${DB_USER} PASSWORD '${DB_PASSWORD}';
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

echo "Database ready. Use the same password in .env DATABASE_URL."
