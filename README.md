# Fingrasp

Browser-fingerprint intelligence platform. Collects browser/device attributes, generates SHA-256 composite hashes, and stores data for entropy research and fraud-prevention analysis.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| Database | MongoDB Atlas |
| Cache | Redis |
| CAPTCHA | Cloudflare Turnstile |
| Fingerprinting | MixVisit |

---

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB Atlas
- Redis
- Cloudflare Turnstile keys

### Setup

```bash
git clone https://github.com/KrAsH-CoD3/Fingrasp.git
cd fingrasp
uv sync
cp .env.example .env
# Edit .env with your credentials
```

### Run

```bash
# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Start server
uv run python -m dev
```

---

## Configuration

Required environment variables:

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `REDIS_URL` | Redis connection URL |
| `TURNSTILE_SITE_KEY` | Cloudflare Turnstile site key |
| `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile secret key |

See `.env.example` for all options.

---

## Architecture

```
Turnstile → Session Token (Redis) → Duplicate Check → MongoDB
```

| Data | Storage | TTL |
|------|---------|-----|
| Session Tokens | Redis | 5 min |
| Fingerprint Cache | Redis | 7 days |
| Records | MongoDB | Persistent |

---

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Fingerprint page |
| `/api/validate-turnstile` | POST | Validate CAPTCHA |
| `/api/save` | POST | Submit fingerprint |

---

## Deployment

```bash
docker build -t fingrasp .
docker run -p 8000:8000 --env-file .env fingrasp
```

Set `STRICT_SECURITY=true` for production.

---

## Security

- CSRF double-submit cookies
- Rate limiting
- IP anonymization
- NoSQL injection prevention
- CSP, HSTS, security headers

---

## License

MIT
