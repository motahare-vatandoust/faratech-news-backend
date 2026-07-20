# Faratech News Backend

FastAPI backend for [Faratech News](https://faratech.news). It stores and serves news articles, crawls content from external sources, translates articles to Farsi via GapGPT, and provides admin authentication.

## Features

- REST API for news CRUD (`/news`)
- Web crawlers for DZone, DeepMind, HubSpot, Marketing Week, The Rundown AI, and Ben's Bites
- Farsi translation and categorization via GapGPT
- Admin JWT auth
- PostgreSQL + SQLAlchemy + Alembic

## Requirements

- Python 3.9+
- PostgreSQL 14+

## Quick start

**One command** (venv, deps, DB, migrations, server):

```bash
./dev.sh
```

Requires PostgreSQL running locally (`brew services start postgresql@14`).  
API: http://localhost:8000 · Docs: http://localhost:8000/docs

Optional env overrides: `PORT=8001 ./dev.sh`, `DB_NAME=faratech_news ./dev.sh`.

### Manual setup

<details>
<summary>Step-by-step (if you prefer not to use ./dev.sh)</summary>

#### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd faratech-news-backend

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure environment

Copy the example env file and edit it:

```bash
cp .env.example .env
```

On macOS Homebrew Postgres, use your OS username (no password):

```env
DATABASE_URL=postgresql+psycopg://YOUR_MAC_USER@localhost:5432/faratech_news
GAPGPT_API_KEY=your-gapgpt-api-key-here
JWT_SECRET_KEY=change-this-in-production
```

`GAPGPT_API_KEY` is required for translation and the `/ai/chat` endpoint. Crawling works without it if you pass `--no-translate` on the CLI or set `translate_to_farsi=false` on API calls.

#### 4. Create the database

```bash
createdb faratech_news
```

Or with `psql`:

```sql
CREATE DATABASE faratech_news;
```

#### 5. Run migrations

```bash
alembic upgrade head
```

#### 6. Start the API server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python main.py
```

</details>

The API is available at `http://localhost:8000`.

## Verify it works

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok","database":"ok"}
```

Interactive API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Full endpoint reference: [docs/API.md](docs/API.md)

## Running crawlers

### Via CLI

Preview articles without saving:

```bash
python -m crawler --source deepmind --limit 3
```

Crawl, translate to Farsi, and save to the database:

```bash
python -m crawler --source deepmind --limit 5 --save
```

Skip translation (English only):

```bash
python -m crawler --source dzone --limit 5 --save --no-translate
```

Available sources: `bensbites`, `deepmind`, `dzone`, `hubspot`, `marketingweek`, `rundown`

### Via API

With the server running:

```bash
# Sync a specific source
curl -X POST "http://localhost:8000/crawler/deepmind/sync?limit=3"

# Generic crawl
curl -X POST http://localhost:8000/crawler/run \
  -H "Content-Type: application/json" \
  -d '{"source": "deepmind", "limit": 3, "persist": true, "translate_to_farsi": true}'
```

## Admin auth

Register an admin:

```bash
curl -X POST http://localhost:8000/admin/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","full_name":"Admin","password":"secret123"}'
```

Use the returned `access_token` on protected routes:

```bash
curl http://localhost:8000/admin/me \
  -H "Authorization: Bearer <access_token>"
```

## Project structure

```
├── main.py              # FastAPI app entrypoint
├── routers/             # HTTP route handlers
├── services/            # Business logic (news, crawler, auth, GapGPT)
├── models/              # Pydantic request/response schemas
├── db/                  # SQLAlchemy models and session
├── crawler/             # Source crawlers and CLI
├── alembic/             # Database migrations
├── docs/API.md          # Endpoint documentation
└── deploy/              # Production deployment guide
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | local Postgres URL | PostgreSQL connection string |
| `GAPGPT_API_KEY` | For AI/translation | — | GapGPT API key |
| `GAPGPT_BASE_URL` | No | `https://api.gapgpt.app/v1` | GapGPT API base URL |
| `GAPGPT_DEFAULT_MODEL` | No | `gpt-4o` | Default chat model |
| `GAPGPT_TRANSLATION_MODEL` | No | same as default | Model used for article translation |
| `JWT_SECRET_KEY` | Yes (prod) | dev placeholder | Secret for signing admin JWTs |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | Token lifetime in minutes |
| `CORS_ORIGINS` | No | — | Comma-separated allowed frontend origins |
| `CRAWLER_USE_CURL_CFFI` | No | `true` | Use curl_cffi to bypass Cloudflare |
| `CRAWLER_IMPERSONATE` | No | `chrome120` | Browser impersonation profile |
| `CRAWLER_REQUEST_TIMEOUT` | No | `60` | HTTP timeout in seconds |
| `CRAWLER_MAX_RETRIES` | No | `3` | Retry count for failed requests |
| `CRAWLER_DEFAULT_LIMIT` | No | `10` | Default articles per crawl |

See [.env.example](.env.example) for a full template.

## Production deployment

See [deploy/README.md](deploy/README.md) for VPS setup, offline wheel installs, and rsync-based updates.

Production API: `https://api.faratech.news`

## Development

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```
