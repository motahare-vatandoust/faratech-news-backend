# Faratech News API

Base URL (local): `http://localhost:8000`  
Production: `https://api.faratech.news`

Interactive docs (when the server is running):

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

---

## Authentication

Most endpoints are public. Admin endpoints under `/admin` use JWT bearer tokens.

After login or register, send the token on protected routes:

```http
Authorization: Bearer <access_token>
```

| Endpoint | Auth required |
|----------|---------------|
| `GET /health` | No |
| `/news/*` | No |
| `/crawler/*` | No |
| `POST /ai/chat` | No |
| `POST /admin/register`, `POST /admin/login` | No |
| `GET /admin/me`, `POST /admin/change-password` | Yes |

---

## Error responses

FastAPI returns errors in this shape:

```json
{
  "detail": "Human-readable message"
}
```

Validation errors (`422`) return:

```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "title"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```

Common status codes:

| Code | Meaning |
|------|---------|
| `400` | Bad request (invalid input or business rule) |
| `401` | Missing or invalid auth token |
| `404` | Resource not found |
| `409` | Conflict (e.g. duplicate admin email) |
| `422` | Request body/query validation failed |
| `429` | GapGPT rate limit |
| `502` | Upstream service error (GapGPT) |
| `503` | Service unavailable (GapGPT not configured) |

---

## Health

### `GET /health`

Check that the API is running.

**Response `200`**

```json
{
  "status": "ok"
}
```

---

## News

### `GET /news`

List all news articles, newest first.

**Query parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `status` | string | No | Filter by status: `draft`, `review`, or `published` |

**Response `200`** — array of `NewsResponse`

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "عنوان خبر",
    "content": "متن کامل مقاله...",
    "summary": "خلاصه کوتاه",
    "category": "هوش مصنوعی",
    "tags": ["AI", "یادگیری ماشین"],
    "source": "deepmind",
    "source_url": "https://deepmind.google/blog/example",
    "status": "published",
    "created_at": "2026-06-07T10:00:00+00:00",
    "updated_at": "2026-06-07T10:00:00+00:00"
  }
]
```

---

### `GET /news/{news_id}`

Get a single article by UUID.

**Response `200`** — `NewsResponse`

**Response `404`**

```json
{
  "detail": "News not found"
}
```

---

### `POST /news`

Create a new article.

If `category` or `tags` are omitted, defaults are applied based on `source` (falls back to `"General"` and `[]`).

**Request body** — `NewsCreate`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | Yes | — | Article title |
| `content` | string | Yes | — | Full body |
| `summary` | string | No | `null` | Short summary |
| `category` | string | No | source default | Primary category |
| `tags` | string[] | No | source default | Topic tags |
| `source` | string | No | `null` | Crawler/source name |
| `source_url` | string | No | `null` | Original URL |
| `status` | string | No | `draft` | `draft`, `review`, or `published` |

**Example request**

```json
{
  "title": "عنوان خبر",
  "content": "متن کامل...",
  "summary": "خلاصه",
  "category": "توسعه نرم‌افزار",
  "tags": ["Python", "Backend"],
  "source": "dzone",
  "source_url": "https://dzone.com/articles/example",
  "status": "draft"
}
```

**Response `201`** — `NewsResponse`

---

### `PUT /news/{news_id}`

Replace an article. All base fields should be sent; omitted optional fields become `null`.

**Request body** — `NewsUpdate` (same fields as create, plus optional `status`)

**Response `200`** — `NewsResponse`  
**Response `404`** — news not found

---

### `PATCH /news/{news_id}`

Partial update. Only include fields to change.

**Request body** — `NewsPatch`

| Field | Type | Required |
|-------|------|----------|
| `title` | string | No |
| `content` | string | No |
| `summary` | string | No |
| `category` | string | No |
| `tags` | string[] | No |
| `source` | string | No |
| `source_url` | string | No |
| `status` | string | No |

**Example request**

```json
{
  "status": "published",
  "category": "بازاریابی"
}
```

**Response `200`** — `NewsResponse`  
**Response `404`** — news not found

---

### `DELETE /news/{news_id}`

Delete an article.

**Response `204`** — no body  
**Response `404`** — news not found

---

## Crawler

Sources: `bensbites`, `deepmind`, `dzone`, `hubspot`, `marketingweek`, `rundown`

Sync endpoints crawl the source, optionally translate to Farsi via GapGPT, and save new articles (skipping duplicates by `source` + `source_url`).

### `GET /crawler/sources`

List registered crawler sources.

**Response `200`**

```json
[
  {
    "name": "dzone",
    "base_url": "https://dzone.com"
  },
  {
    "name": "deepmind",
    "base_url": "https://deepmind.google"
  }
]
```

---

### `POST /crawler/run`

Run a generic crawl for any registered source.

**Request body** — `CrawlRequest`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source` | string | No | `dzone` | Source name |
| `limit` | integer | No | crawler default | Max articles (`1`–`100`) |
| `persist` | boolean | No | `true` | Save new articles to DB |
| `translate_to_farsi` | boolean | No | `true` | Translate via GapGPT |

**Example request**

```json
{
  "source": "deepmind",
  "limit": 5,
  "persist": true,
  "translate_to_farsi": true
}
```

**Response `200`** — `CrawlResponse`  
**Response `400`** — unknown source

```json
{
  "detail": "Unknown crawler source 'foo'. Known sources: bensbites, deepmind, dzone, hubspot, marketingweek, rundown"
}
```

---

### Source sync endpoints

Convenience endpoints that crawl, translate (by default), and persist.

| Method | Path |
|--------|------|
| `POST` | `/crawler/dzone/sync` |
| `POST` | `/crawler/deepmind/sync` |
| `POST` | `/crawler/hubspot/sync` |
| `POST` | `/crawler/marketingweek/sync` |
| `POST` | `/crawler/rundown/sync` |
| `POST` | `/crawler/bensbites/sync` |

**Query parameters**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `limit` | integer | No | crawler default | Max articles (`1`–`100`) |
| `translate_to_farsi` | boolean | No | `true` | Translate via GapGPT |

**Example**

```http
POST /crawler/deepmind/sync?limit=3&translate_to_farsi=true
```

**Response `200`** — `CrawlResponse` (see below)

---

### `CrawlResponse`

Returned by `/crawler/run` and all sync endpoints.

```json
{
  "source": "deepmind",
  "fetched_count": 3,
  "saved_count": 2,
  "skipped_count": 1,
  "errors": [],
  "articles": [
    {
      "title": "Translated title",
      "content": "Full article body...",
      "source_url": "https://deepmind.google/blog/example",
      "summary": "Optional summary",
      "category": "هوش مصنوعی",
      "tags": ["تحقیق", "یادگیری ماشین"],
      "author": "Google DeepMind",
      "published_at": null
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Crawler source name |
| `fetched_count` | integer | Articles fetched in this run |
| `saved_count` | integer | New articles written to DB |
| `skipped_count` | integer | URLs already in DB (duplicates) |
| `errors` | string[] | Per-URL or translation errors |
| `articles` | `CrawledArticle[]` | Fetched article payloads |

---

## AI (GapGPT)

### `POST /ai/chat`

OpenAI-compatible chat completion via GapGPT.

**Request body** — `ChatRequest`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | array | Yes | At least one message |
| `messages[].role` | string | Yes | `system`, `user`, or `assistant` |
| `messages[].content` | string | Yes | Message text |
| `model` | string | No | Defaults to `GAPGPT_DEFAULT_MODEL` |

**Example request**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Summarize this article in Farsi."
    }
  ],
  "model": "gpt-4o"
}
```

**Response `200`**

```json
{
  "content": "Assistant reply text...",
  "model": "gpt-4o"
}
```

**Error responses**

| Status | When |
|--------|------|
| `429` | GapGPT rate limit |
| `502` | Connection or upstream failure |
| `503` | Missing/invalid API key or quota exhausted |

---

## Admin auth

### `POST /admin/register`

Create a new admin account and return a JWT.

**Request body**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email |
| `full_name` | string | Yes | 2–255 characters |
| `password` | string | Yes | 8–128 characters |

**Response `201`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "admin": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "is_active": true,
    "created_at": "2026-06-07T10:00:00+00:00",
    "updated_at": "2026-06-07T10:00:00+00:00"
  }
}
```

**Response `409`**

```json
{
  "detail": "Admin with this email already exists"
}
```

---

### `POST /admin/login`

Authenticate and receive a JWT.

**Request body**

| Field | Type | Required |
|-------|------|----------|
| `email` | string | Yes |
| `password` | string | Yes |

**Response `200`** — same shape as register (`AuthTokenResponse`)  
**Response `401`**

```json
{
  "detail": "Invalid email or password"
}
```

---

### `GET /admin/me`

Return the currently authenticated admin.

**Headers:** `Authorization: Bearer <token>`

**Response `200`** — `AdminResponse`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "is_active": true,
  "created_at": "2026-06-07T10:00:00+00:00",
  "updated_at": "2026-06-07T10:00:00+00:00"
}
```

**Response `401`**

```json
{
  "detail": "Missing bearer token"
}
```

---

### `POST /admin/change-password`

Change password for the authenticated admin.

**Headers:** `Authorization: Bearer <token>`

**Request body**

| Field | Type | Required |
|-------|------|----------|
| `current_password` | string | Yes |
| `new_password` | string | Yes |

**Response `204`** — no body  
**Response `400`**

```json
{
  "detail": "Current password is incorrect"
}
```

---

## Shared types

### `NewsStatus`

| Value | Description |
|-------|-------------|
| `draft` | Not published |
| `review` | Awaiting review |
| `published` | Live |

### `NewsResponse`

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `title` | string | Title |
| `content` | string | Full body |
| `summary` | string \| null | Short summary |
| `category` | string \| null | Primary category |
| `tags` | string[] \| null | Topic tags |
| `source` | string \| null | Source identifier |
| `source_url` | string \| null | Original article URL |
| `status` | `NewsStatus` | Publication status |
| `created_at` | datetime (ISO 8601) | Created timestamp |
| `updated_at` | datetime (ISO 8601) | Last updated timestamp |

### Source default categories

When crawlers or `POST /news` omit category/tags, these defaults apply:

| Source | Default category | Default tags |
|--------|------------------|--------------|
| `dzone` | Development | programming |
| `deepmind` | AI | research, machine learning |
| `hubspot` | Marketing | marketing |
| `marketingweek` | Marketing | marketing |
| `rundown` | AI | artificial intelligence |
| `bensbites` | AI | artificial intelligence |
| (other / none) | General | `[]` |
