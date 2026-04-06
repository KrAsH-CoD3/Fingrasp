# Fingrasp

Fingrasp is a browser-fingerprint intelligence platform built with FastAPI, MongoDB Atlas, and MixVisit. When a user visits the site, Fingrasp collects a structured snapshot of their browser and device attributes, generates a composite SHA-256 hash, and displays the full signal breakdown directly on the page.

The collected fingerprints are stored for research into browser entropy, fingerprint stability over time, and fraud-prevention techniques. No personally identifiable information is collected or linked to the fingerprint data.

---

## Features

- **Transparent Collection:** Visitors see every signal collected from their device in a categorized, expandable breakdown.
- **Composite Hashing:** All signals are combined into a single SHA-256 fingerprint hash for identification and comparison.
- **Research-Oriented Storage:** Fingerprint records are persisted to MongoDB Atlas for entropy analysis and stability tracking.
- **Privacy-First Approach:** No names, emails, or personal data are collected. A full privacy policy is included.
- **Responsive Interface:** Dark-mode technical aesthetic, optimized for desktop and mobile viewports.
- **Access Code System:** One-time-use codes control who can submit fingerprints.
- **Rate Limiting:** API endpoints are rate-limited using SlowAPI to prevent abuse.
- **CSRF Protection:** Double-submit cookie pattern validates all state-changing requests.
- **Strict Security Headers:** CSP, HSTS, X-Frame-Options, and more for defense in depth.

---

## Directory Structure

```text
.
├── app/
│   ├── __init__.py          # App factory and route registration
│   ├── config.py            # Configuration and environment management
│   ├── database.py          # MongoDB Atlas connection lifecycle
│   ├── limiter.py           # SlowAPI rate limiter instance
│   ├── schemas.py           # Pydantic models for request/response validation
│ ├── security.py # IP anonymization, origin validation, headers middleware
│ └── routes/
│       ├── fingerprint.py   # Page rendering endpoints
│       └── api.py           # API endpoints (code validation, fingerprint submission)
├── static/
│   ├── css/                 # Theming and layout
│   └── js/                  # MixVisit integration and UI rendering
├── templates/ # Jinja2 HTML templates
├── main.py # Application entry point
├── pyproject.toml # UV project configuration
└── uv.lock                  # Dependency lockfile
```

---

## Local Development

Fingrasp uses the uv package manager for dependency management.

### 1. Environment Initialization
```bash
git clone <repository-url>
cd fingrasp
uv sync
```

### 2. Configuration
Create a `.env` file in the project root:
```env
MONGODB_URI="your_mongodb_atlas_connection_string"
DB_NAME="fingrasp"

# Optional
BASE_URL="http://localhost:8000"
CODE_EXPIRY_HOURS="48"
COLLECTION_NAME="access_codes"
ALLOWED_ORIGINS="http://localhost:8000,http://127.0.0.1:8000"
```

### 3. Running the Server
```bash
uv run -m uvicorn main:app --reload
```
The application will be available at `http://localhost:8000`.

---

## Access Code Flow

Fingrasp uses a one-time access code system to control fingerprint submissions:

1. **Admin generates code** via admin interface
2. **Visitor receives link** with embedded code (e.g., `/?code=123456`)
3. **Visitor submits fingerprint** - code is consumed and cannot be reused
4. **Fingerprint stored** with anonymized IP address

---

## API Endpoints

| Endpoint | Method | Rate Limit | Description |
| :--- | :--- | :--- | :--- |
| `/` | GET | - | Main fingerprint collection page |
| `/privacy` | GET | - | Privacy policy page |
| `/api/validate-code` | POST | 10/min | Pre-flight code validation |
| `/api/save` | POST | 10/min | Submit fingerprint data |

All POST endpoints require CSRF token (double-submit cookie pattern).

---

## Deployment

Fingrasp is a standard FastAPI application deployable on any Python-compatible host.

1. Connect the repository to your deployment platform.
2. Set environment variables (see Configuration section).
3. Enable `STRICT_SECURITY=true` for production.
4. Start the application with `uvicorn main:app`.

---

## Signals Collected

| Category | Examples |
| :--- | :--- |
| Browser Metadata | User-agent, language, timezone, DNT flag |
| Hardware | CPU cores, device memory, screen resolution, color depth |
| Graphics | WebGL renderer, vendor, canvas hash |
| Audio | AudioContext oscillator output hash |
| Network | IP address (server-side, anonymized), connection type |
| Browser Capabilities | Supported codecs, API availability, installed fonts |

All signals are combined into a single composite SHA-256 hash per session.

---

## Security

- **CSRF Protection:** Double-submit cookie pattern on all state-changing requests.
- **Rate Limiting:** SlowAPI limits requests per endpoint to prevent abuse.
- **IP Anonymization:** Last octet of IPv4 / last 80 bits of IPv6 zeroed before storage.
- **NoSQL Injection Prevention:** Payloads sanitized for MongoDB operator keys.
- **Strict CSP:** Content-Security-Policy with nonce-based scripts.
- **HSTS:** HTTP Strict Transport Security in production mode.
- **Security Headers:** X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy.
- **Payload Validation:** Max size, nesting depth, and string length limits enforced via Pydantic.
- No personally identifiable information is collected.

---

## Credits

- **MixVisit:** Core fingerprinting library providing the signal collection engine. [MixVisit](https://www.mixvisit.com/)
