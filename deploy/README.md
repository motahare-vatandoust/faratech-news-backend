# Deploy & update (Arvan VPS + Pars Pack CDN)

Server: `ubuntu@95.38.160.122`  
App path: `/opt/faratech-news-backend`  
API: `https://api.faratech.news`

Iranian VPS cannot reach GitHub/PyPI reliably — **always rsync from Mac** and **install Python deps offline**.

---

## First-time setup (once)

### Mac — download Linux wheels

```bash
cd /Users/mac/Developer/faratech-news-backend
bash deploy/download-wheels-linux.sh
```

### Mac — upload code + wheels

```bash
rsync -avz --exclude '.venv' --exclude 'venv' --exclude '__pycache__' --exclude '.git' --exclude '.env' \
  ./ ubuntu@95.38.160.122:/opt/faratech-news-backend/

rsync -avz wheels-linux/ ubuntu@95.38.160.122:/opt/faratech-news-backend/wheels-linux/
```

### Server — Postgres, .env, install

```bash
ssh ubuntu@95.38.160.122
cd /opt/faratech-news-backend

cp .env.example .env
nano .env   # DATABASE_URL uses user faratech, not postgres

bash deploy/install-offline.sh
```

`.env` minimum:

```env
DATABASE_URL=postgresql+psycopg://faratech:PASSWORD@localhost:5432/faratech_news
GAPGPT_API_KEY=...
JWT_SECRET_KEY=...
CORS_ORIGINS=https://faratech.news,https://www.faratech.news
```

### Pars Pack CDN

- Nameservers: `mountain.parspack.net`, `savanna.parspack.net`
- A record: `api` → `95.38.160.122`
- Origin: `95.38.160.122:80` (HTTP)
- SSL: enable in CDN panel

### Verify

```bash
# server
curl http://127.0.0.1:8000/health
curl -H "Host: api.faratech.news" http://127.0.0.1/health

# Mac
curl https://api.faratech.news/health
```

---

## Every code update (normal workflow)

### 1. Mac — upload changes

```bash
cd /Users/mac/Developer/faratech-news-backend

rsync -avz --exclude '.venv' --exclude 'venv' --exclude '__pycache__' --exclude '.git' --exclude '.env' \
  ./ ubuntu@95.38.160.122:/opt/faratech-news-backend/
```

If `requirements.txt` changed, also on Mac:

```bash
bash deploy/download-wheels-linux.sh
rsync -avz wheels-linux/ ubuntu@95.38.160.122:/opt/faratech-news-backend/wheels-linux/
```

### 2. Server — install + migrate + restart

```bash
ssh ubuntu@95.38.160.122
cd /opt/faratech-news-backend

# deps changed:
.venv/bin/pip install --no-index --find-links=./wheels-linux -r requirements.txt

# always after code changes:
.venv/bin/alembic upgrade head
sudo chown -R www-data:www-data /opt/faratech-news-backend
sudo systemctl restart faratech-api
```

Or full reinstall (recreates venv):

```bash
bash deploy/install-offline.sh
```

### 3. Verify

```bash
curl http://127.0.0.1:8000/health
```

---

## Troubleshooting

| Problem | Command |
|---------|---------|
| API down | `sudo journalctl -u faratech-api -n 30 --no-pager` |
| DB auth fail | `grep DATABASE_URL .env` — user must be `faratech` |
| 502 from CDN | `sudo systemctl status nginx`; CDN origin `95.38.160.122:80` |
| apt slow/broken | `sudo bash deploy/fix-apt-iran.sh` |
