# Fingrasp

Fingrasp is a browser-fingerprint intelligence platform built with FastAPI, MongoDB Atlas, Redis, and MixVisit. When a user visits the site, Fingrasp collects a structured snapshot of their browser and device attributes, generates a composite SHA-256 hash, and displays the full signal breakdown directly on the page.

The collected fingerprints are stored for research into browser entropy, fingerprint stability over time, and fraud-prevention techniques. No personally identifiable information is collected or linked to the fingerprint data.

---

## Features

- **Layered Anti-Bot Protection:** Cloudflare Turnstile, browser honeypots, and behavioral interaction analysis for automated protection.
- **Redis-Powered Sessions:** Session tokens stored in Redis with automatic TTL for secure, stateless verification.
- **Duplicate Cache:** 2-tier fingerprint duplicate detection using Redis cache before MongoDB queries.
- **Transparent Collection:** Visitors see every signal collected from their device in a categorized, expandable breakdown.
- **Composite Hashing:** All signals are combined into a single SHA-256 fingerprint hash for identification and comparison.
- **Research-Oriented Storage:** Fingerprint records are persisted to MongoDB Atlas for entropy analysis and stability tracking.
- **Privacy-First Approach:** No names, emails, or personal data are collected. A full privacy policy is included.
- **Responsive Interface:** Dark-mode technical aesthetic, optimized for desktop and mobile viewports.
- **Rate Limiting:** API endpoints and static assets are rate-limited using SlowAPI to prevent abuse.
- **CSRF Protection:** Double-submit cookie pattern validates all state-changing requests.
- **Strict Security Headers:** CSP, HSTS, X-Frame-Options, and more for defense in depth.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB Atlas |
| **Cache/Session** | Redis |
| **Fingerprinting** | MixVisit |
| **CAPTCHA** | Cloudflare Turnstile |
| **Rate Limiting** | SlowAPI |
| **Package Manager** | UV |

---

## Directory Structure

```text
.
├── app/
│   ├── __init__.py          # App factory, lifespan, and middleware
│   ├── config.py            # Configuration and environment management
│   ├── database.py          # MongoDB Atlas connection lifecycle
│   ├── redis_client.py      # Redis client for session tokens and fingerprint cache
│   ├── limiter.py           # SlowAPI rate limiter instance
│   ├── schemas.py           # Pydantic models for request/response validation
│   ├── security.py          # IP anonymization, origin validation, headers middleware
│   ├── device_detection/    # Device model validation and detection
│   └── routes/
│       ├── fingerprint.py   # Page rendering endpoints
│       └── api.py           # API endpoints (Turnstile, fingerprint submission)
├── static/
│   ├── css/                 # Theming and layout
│   └── js/                  # MixVisit integration and UI rendering
├── templates/               # Jinja2 HTML templates
├── main.py                  # Application entry point
├── dev.py                   # Development server entry point
├── pyproject.toml           # UV project configuration
└── uv.lock                  # Dependency lockfile
```

---

## Local Development

Fingrasp uses the [UV package manager](https://github.com/astral-sh/uv) for dependency management.

### Prerequisites

- Python 3.11+
- MongoDB Atlas account
- Redis server (local or managed)
- Cloudflare Turnstile account

### 1. Clone and Install

```bash
git clone https://github.com/KrAsH-CoD3/Fingrasp.git
cd fingrasp
uv sync
```

### 2. Configure Environment

Create a `.env` file in the project root (see `.env.example`):

```env
# ── Database ──
MONGODB_URI="your_mongodb_atlas_connection_string"
DB_NAME="fingrasp"

# ── Redis ──
REDIS_URL="redis://localhost:6379/0"

# ── Cloudflare Turnstile ──
TURNSTILE_SITE_KEY="your_site_key"
TURNSTILE_SECRET_KEY="your_secret_key"

# ── Environment ──
DEBUG=true
STRICT_SECURITY=false

# ── CORS ──
ALLOWED_ORIGINS="http://localhost:8000,http://127.0.0.1:8000"

# ── Rate Limiting ──
RATE_LIMIT_SAVE=1/minute
RATE_LIMIT_API=5/minute
RATE_LIMIT_FRONTEND=30/minute
RATE_LIMIT_STATIC=30/minute

# ── IP Privacy ──
ANONYMIZE_IP=true

# ── Application ──
BASE_URL="http://localhost:8000"
```

### 3. Start Redis

**Using Docker:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Using local installation:**
```bash
redis-server
```

### 4. Run the Server

```bash
uv run python -m dev
```

Or using uvicorn directly:
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`.

---

## API Endpoints

| Endpoint | Method | Rate Limit | Description |
|:---------|:-------|:-----------|:------------|
| `/` | GET | 30/min | Main fingerprint collection page |
| `/privacy` | GET | - | Privacy policy page |
| `/api/validate-turnstile` | POST | 5/min | Validate Turnstile and generate session token |
| `/api/save` | POST | 1/min | Submit fingerprint data |

### Authentication Flow

1. **Turnstile Validation**: Client completes Cloudflare Turnstile challenge
2. **Session Token**: Server generates UUID stored in Redis with TTL
3. **Fingerprint Submission**: Client submits fingerprint with session token
4. **Token Consumption**: Server validates and deletes token (single-use)

---

## Architecture

### Request Flow

```
Client Request
     │
     ▼
Rate Limit Check (SlowAPI)
     │
     ▼
CSRF/Origin Validation
     │
     ▼
Turnstile Verification
     │
     ▼
Session Token (Redis)
     │
     ▼
Duplicate Check (Redis Cache → MongoDB)
     │
     ▼
Save Fingerprint (MongoDB)
     │
     ▼
Cache Fingerprint Hash (Redis)
```

### Data Flow

| Data | Storage | TTL |
|------|---------|-----|
| Session Tokens | Redis | 5 minutes |
| Fingerprint Hashes (cache) | Redis | 7 days |
| Fingerprint Records | MongoDB | Persistent |
| Counter Stats | MongoDB | Persistent |

---

## Deployment

### Vercel/Railway

1. Connect repository to deployment platform
2. Add Redis addon (Upstash recommended)
3. Set environment variables (see Configuration)
4. Enable `STRICT_SECURITY=true` for production
5. Deploy

### Docker

```bash
docker build -t fingrasp .
docker run -p 8000:8000 --env-file .env fingrasp
```

### Production Checklist

- [ ] Set `STRICT_SECURITY=true`
- [ ] Configure `ALLOWED_ORIGINS` for production domain
- [ ] Use managed Redis (Upstash, Redis Cloud)
- [ ] Enable MongoDB connection pooling
- [ ] Configure rate limits appropriately
- [ ] Set up monitoring for Redis and MongoDB

---

## Signals Collected

| Category | Examples |
|:---------|:---------|
| Browser Metadata | User-agent, language, timezone, DNT flag |
| Hardware | CPU cores, device memory, screen resolution, color depth |
| Graphics | WebGL renderer, vendor, canvas hash |
| Audio | AudioContext oscillator output hash |
| Network | IP address (server-side, anonymized), connection type |
| Browser Capabilities | Supported codecs, API availability, installed fonts |

All signals are combined into a single composite SHA-256 hash per session.

---

## Security

| Feature | Implementation |
|---------|---------------|
| **CSRF Protection** | Double-submit cookie pattern on all state-changing requests |
| **Rate Limiting** | SlowAPI limits requests per endpoint |
| **IP Anonymization** | Last octet of IPv4 / last 80 bits of IPv6 zeroed |
| **NoSQL Injection** | Payloads sanitized for MongoDB operator keys |
| **Content Security Policy** | Nonce-based script allowlisting |
| **HSTS** | HTTP Strict Transport Security in production |
| **Security Headers** | X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy |
| **Payload Validation** | Max size, nesting depth, and string limits via Pydantic |
| **Session Tokens** | Single-use, Redis-backed with automatic TTL |

No personally identifiable information is collected.

---

## Redis Usage

Fingrasp uses Redis for:

1. **Session Token Storage**
   - Generated after Turnstile validation
   - Single-use tokens with 5-minute TTL
   - Atomic consumption prevents replay attacks

2. **Fingerprint Duplicate Cache**
   - 2-tier check: Redis first, then MongoDB
   - 7-day TTL for cached hashes
   - Reduces MongoDB reads by ~90% for duplicates

**Free Tier Friendly**: ~2-3 requests per submission (well within Upstash 10K/day limit)

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGODB_URI` | Yes* | - | MongoDB Atlas connection string |
| `DB_NAME` | No | `fingrasp` | Database name |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis connection URL |
| `TURNSTILE_SITE_KEY` | Yes | - | Cloudflare Turnstile site key |
| `TURNSTILE_SECRET_KEY` | Yes | - | Cloudflare Turnstile secret key |
| `DEBUG` | No | `true` | Enable debug mode |
| `STRICT_SECURITY` | No | `false` | Enable production security headers |
| `ALLOWED_ORIGINS` | No | `http://localhost:8000` | CORS allowed origins |
| `RATE_LIMIT_SAVE` | No | `1/minute` | Rate limit for fingerprint save |
| `RATE_LIMIT_API` | No | `5/minute` | Rate limit for API endpoints |
| `RATE_LIMIT_STATIC` | No | `30/minute` | Rate limit for static files |
| `ANONYMIZE_IP` | No | `true` | Anonymize IP addresses |
| `BASE_URL` | No | `http://localhost:8000` | Application base URL |

*Required in production (`STRICT_SECURITY=true`)

---

## Credits

- **MixVisit:** Core fingerprinting library providing the signal collection engine. [MixVisit](https://www.mixvisit.com/)
