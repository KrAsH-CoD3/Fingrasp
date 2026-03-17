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

---

## Directory Structure

```text
.
├── app/
│   ├── __init__.py         # App factory and route registration
│   ├── config.py           # Configuration and environment management
│   ├── database.py         # MongoDB Atlas connection lifecycle
│   └── routes/
│       └── fingerprint.py  # Page rendering and data persistence endpoints
├── static/
│   ├── css/                # Theming and layout
│   └── js/                 # MixVisit integration and UI rendering
├── templates/              # Jinja2 HTML templates
├── main.py                 # Application entry point
├── pyproject.toml          # UV project configuration
└── uv.lock                 # Dependency lockfile
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
```

### 3. Running the Server
```bash
uv run -m uvicorn main:app --reload
```
The application will be available at `http://localhost:8000`.

---

## Deployment

Fingrasp is a standard FastAPI application deployable on any Python-compatible host.

1. Connect the repository to your deployment platform.
2. Set `MONGODB_URI` and `DB_NAME` as environment variables.
3. Start the application with `uvicorn main:app`.

---

## Signals Collected

| Category | Examples |
| :--- | :--- |
| Browser Metadata | User-agent, language, timezone, DNT flag |
| Hardware | CPU cores, device memory, screen resolution, color depth |
| Graphics | WebGL renderer, vendor, canvas hash |
| Audio | AudioContext oscillator output hash |
| Network | IP address (server-side), connection type |
| Browser Capabilities | Supported codecs, API availability, installed fonts |

All signals are combined into a single composite SHA-256 hash per session.

---

## Security

- Fingerprint data is encrypted at rest and in transit.
- No personally identifiable information is collected unless voluntarily provided.
- Access to stored records is restricted via role-based access control.

---

## Credits

- **MixVisit:** Core fingerprinting library providing the signal collection engine. [MixVisit](https://www.mixvisit.com/)
