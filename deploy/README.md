# Deploy to Arvan Cloud + Pars Pack DNS

Server IP example: `95.38.160.122`  
API hostname: `api.faratech.news`

## 1. DNS (Pars Pack)

In [my.parspack.com](https://my.parspack.com/) → domain **faratech.news** → DNS:

| Type | Name | Value        | TTL  |
|------|------|--------------|------|
| A    | api  | 95.38.160.122 | 300 |

Optional (frontend on same VPS later):

| Type | Name | Value        |
|------|------|--------------|
| A    | @    | 95.38.160.122 |
| A    | www  | 95.38.160.122 |

Wait until `dig api.faratech.news +short` returns `95.38.160.122`.

## 2. Arvan Cloud firewall

In [panel.arvancloud.ir](https://panel.arvancloud.ir/) → your VPS → firewall/security:

- Allow **22** (SSH), **80**, **443**

## 3. Server setup (Iran / Arvan VPS)

If `apt` or `git clone` hang or show **Temporary failure resolving**, fix mirrors and DNS first:

```bash
cd /opt/faratech-news-backend
sudo bash deploy/fix-apt-iran.sh
sudo apt-get install -y postgresql postgresql-contrib nginx python3-venv python3-pip certbot python3-certbot-nginx
```

Upload code with `rsync` from your Mac if GitHub is unreachable on the server.

SSH in:

```bash
ssh root@95.38.160.122
```

Clone and configure:

```bash
export DB_PASSWORD='choose-a-strong-db-password'
git clone <your-repo-url> /opt/faratech-news-backend
cd /opt/faratech-news-backend
sudo -E bash deploy/setup-server.sh

cp .env.example .env
# Edit .env: DATABASE_URL, GAPGPT_API_KEY, JWT_SECRET_KEY, CORS_ORIGINS
nano .env

sudo chown -R www-data:www-data /opt/faratech-news-backend

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/alembic upgrade head

sudo cp deploy/faratech-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now faratech-api

sudo cp deploy/nginx-api.conf /etc/nginx/sites-available/faratech-api
sudo ln -sf /etc/nginx/sites-available/faratech-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

sudo certbot --nginx -d api.faratech.news
```

## 4. Verify

```bash
curl https://api.faratech.news/health
```

## 5. Updates

```bash
cd /opt/faratech-news-backend
git pull
.venv/bin/pip install -r requirements.txt
.venv/bin/alembic upgrade head
sudo systemctl restart faratech-api
```
