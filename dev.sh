#!/usr/bin/env bash
# One-command local startup: venv, deps, DB, migrations, API server.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

DB_NAME="${DB_NAME:-faratech_news}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOCAL_USER="${USER:-$(id -un)}"
LOCAL_URL="postgresql+psycopg://${LOCAL_USER}@localhost:5432/${DB_NAME}"

red() { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
info() { printf '→ %s\n' "$*"; }

die() {
  red "$*"
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing '$1'. $2"
}

set_database_url() {
  local url="$1"
  if [[ ! -f .env ]]; then
    printf 'DATABASE_URL=%s\n' "$url" > .env
    return
  fi
  if grep -q '^DATABASE_URL=' .env; then
    if [[ "$(uname)" == "Darwin" ]]; then
      sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=${url}|" .env
    else
      sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${url}|" .env
    fi
  else
    printf '\nDATABASE_URL=%s\n' "$url" >> .env
  fi
}

# --- prerequisites -----------------------------------------------------------
require_cmd python3 "Install Python 3.9+."
require_cmd psql "Install PostgreSQL (e.g. brew install postgresql@14)."
require_cmd pg_isready "Install PostgreSQL client tools."

if ! pg_isready -q; then
  die "PostgreSQL is not running. Try: brew services start postgresql@14"
fi

# --- python env --------------------------------------------------------------
info "Setting up virtualenv"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

# --- env file ----------------------------------------------------------------
if [[ ! -f .env ]]; then
  info "Creating .env from .env.example"
  cp .env.example .env
fi

# Local Homebrew Postgres typically authenticates as the OS user.
# Override the production-style faratech role from .env.example so local just works.
# Set KEEP_DATABASE_URL=1 to preserve an existing DATABASE_URL.
if [[ "${KEEP_DATABASE_URL:-0}" == "1" ]]; then
  info "Keeping existing DATABASE_URL (KEEP_DATABASE_URL=1)"
else
  info "Using local DATABASE_URL for user '${LOCAL_USER}'"
  set_database_url "$LOCAL_URL"
fi

# --- database ----------------------------------------------------------------
info "Ensuring database '${DB_NAME}' exists"
if ! psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1; then
  createdb "$DB_NAME" || die "Could not create database '${DB_NAME}'"
fi

info "Ensuring '${LOCAL_USER}' owns public tables (fixes permission denied)"
psql -d "$DB_NAME" -v ON_ERROR_STOP=1 <<SQL >/dev/null
GRANT ALL ON SCHEMA public TO "${LOCAL_USER}";
GRANT ALL ON ALL TABLES IN SCHEMA public TO "${LOCAL_USER}";
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO "${LOCAL_USER}";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "${LOCAL_USER}";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "${LOCAL_USER}";
DO \$\$
DECLARE r RECORD;
BEGIN
  FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    EXECUTE format('ALTER TABLE public.%I OWNER TO %I', r.tablename, '${LOCAL_USER}');
  END LOOP;
  FOR r IN SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public'
  LOOP
    EXECUTE format('ALTER SEQUENCE public.%I OWNER TO %I', r.sequence_name, '${LOCAL_USER}');
  END LOOP;
END
\$\$;
SQL

info "Checking database connection"
python - <<PY
from dotenv import load_dotenv
import os
import sys
from sqlalchemy import create_engine, text

load_dotenv("${ROOT}/.env", override=True)
url = os.environ.get("DATABASE_URL", "")
if not url:
    print("DATABASE_URL is empty", file=sys.stderr)
    sys.exit(1)
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        user = conn.execute(text("SELECT current_user")).scalar()
        print(f"  connected as {user}")
except Exception as exc:
    print(f"Database connection failed: {exc}", file=sys.stderr)
    sys.exit(1)
PY

# --- migrations --------------------------------------------------------------
info "Running migrations"
alembic upgrade head

# --- server ------------------------------------------------------------------
green "Starting API at http://localhost:${PORT}  (docs: /docs)"
exec uvicorn main:app --reload --host "$HOST" --port "$PORT"
