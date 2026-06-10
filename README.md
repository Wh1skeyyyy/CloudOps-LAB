# CloudOps Lab

![CI](https://github.com/Wh1skeyyyy/CloudOps-LAB/actions/workflows/ci.yml/badge.svg)

A REST API for cataloguing and monitoring cloud services — APIs, databases, frontends,
workers, and containers — across environments. Built end to end to demonstrate backend
engineering: JWT authentication, relational data modelling, input validation, containerisation,
automated testing, CI/CD, security hardening, and cloud deployment.

**🔗 Live API:** https://cloudops-lab.onrender.com/health

> Hosted on Render's free tier, which sleeps after ~15 minutes of inactivity. The **first**
> request after an idle period can take 30–60s to cold-start; requests after that are fast.

---

## Features

- **JWT authentication** — register / login issue signed access tokens; protected routes require a `Bearer` token.
- **Per-user ownership** — every service belongs to a user. Cross-user access returns `404` (not `403`), so the API never reveals that another user's record exists.
- **Full CRUD + filtering** — create, read, update, delete services, with query-param filters on environment, provider, health status, deployment status, and type.
- **Consistent error contract** — every error (validation, auth, not-found, rate-limit, server) returns the same `{"error", "message"}` JSON shape, including the JWT library's own responses.
- **Input validation** — required-field checks, enum validation against the model's allowed values, and URL validation.
- **Rate limiting** — auth endpoints are throttled per client IP (5/min register, 10/min login) to blunt credential-stuffing.
- **Security in CI** — dependency audit (`pip-audit`) and container image scan (Trivy) on every push; Dependabot opens update PRs weekly.
- **Tested** — 23 pytest cases covering auth, CRUD, filtering, ownership isolation, and validation.
- **Containerised** — multi-stage-friendly Dockerfile (non-root user, healthcheck, gunicorn) plus a Compose stack with PostgreSQL.

## Tech stack

| Area | Tools |
|---|---|
| Language / framework | Python 3.12, Flask |
| Data | SQLAlchemy (Flask-SQLAlchemy), PostgreSQL (prod), SQLite (local) |
| Auth & security | Flask-JWT-Extended, Flask-Limiter, Werkzeug password hashing |
| Server | gunicorn |
| Testing & quality | pytest, ruff, pip-audit |
| Container & CI/CD | Docker, Docker Compose, GitHub Actions, Trivy, Dependabot |
| Hosting | Render (app, Docker) + Neon (managed PostgreSQL) |

## Architecture

```text
                    HTTPS
   Client ───────────────────────────►  Render  (Docker container)
                                         │  gunicorn → Flask app factory
                                         │   ├─ JWT auth + IP rate limiting
                                         │   ├─ /health
                                         │   ├─ /api/auth     (register, login, profile)
                                         │   ├─ /api/services  (CRUD + filtering)
                                         │   └─ SQLAlchemy ORM
                                         └───────────────►  Neon (PostgreSQL)

   Deployment pipeline:
   push to main ─► GitHub Actions ─┬─ lint (ruff) + test (pytest)
                                   └─ pip-audit ──► docker build + Trivy scan
                 └──────────────────────────────► Render auto-deploys the new image
```

The app uses the **application-factory** pattern (`create_app`), so the same code powers the
dev server, the test suite (in-memory SQLite), and the production container. Config is selected
by the `FLASK_CONFIG` environment variable.

## API reference

Base URL (local): `http://127.0.0.1:5000` · (live): `https://cloudops-lab.onrender.com`

| Method | Endpoint | Auth | Description |
|---|---|:---:|---|
| `GET` | `/health` | — | Liveness probe |
| `POST` | `/api/auth/register` | — | Create an account → returns JWT (5/min) |
| `POST` | `/api/auth/login` | — | Authenticate → returns JWT (10/min) |
| `GET` | `/api/auth/profile` | ✅ | Current authenticated user |
| `POST` | `/api/services` | ✅ | Create a service |
| `GET` | `/api/services` | ✅ | List own services (supports filters) |
| `GET` | `/api/services/{id}` | ✅ | Get one owned service |
| `PATCH` | `/api/services/{id}` | ✅ | Partial update of an owned service |
| `DELETE` | `/api/services/{id}` | ✅ | Delete an owned service |
| `PATCH` | `/api/services/{id}/health` | ✅ | Record a health status / response time |

**List filters** (query params on `GET /api/services`): `environment`, `provider`,
`health_status`, `deployment_status`, `service_type` — e.g. `/api/services?environment=production&provider=AWS`.

**Allowed values**

| Field | Values |
|---|---|
| `service_type` | `frontend`, `backend`, `database`, `worker`, `container`, `storage`, `other` |
| `provider` | `AWS`, `Azure`, `Google Cloud`, `Render`, `Railway`, `Vercel`, `Docker Local`, `Other` |
| `environment` | `development`, `testing`, `staging`, `production` |
| `deployment_status` | `pending`, `deploying`, `successful`, `failed`, `rolled_back` |
| `health_status` | `healthy`, `degraded`, `down`, `unknown` |

**Example — register then create a service**

```bash
# Register and capture the token
TOKEN=$(curl -s -X POST https://cloudops-lab.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Genesis","email":"you@example.com","password":"a-real-password"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Create a service
curl -X POST https://cloudops-lab.onrender.com/api/services \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"CloudOps API","environment":"production","provider":"Render"}'
```

## Getting started (local)

> Python 3.12 is recommended — it matches CI and the Docker image. Local dev uses SQLite,
> so no database server is required.

```bash
# 1. Enter the project
cd cloudops-lab

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env               # then edit the secrets

# 5. Create the database tables
export FLASK_APP=run.py            # Windows (PowerShell): $env:FLASK_APP="run.py"
flask init-db

# 6. Run the server
flask run                          # or: python run.py
```

```bash
curl http://127.0.0.1:5000/health
# {"application": "CloudOps Lab", "status": "healthy"}
```

## Running the tests

```bash
pip install -r requirements-dev.txt
ruff check .                       # lint
python -m pytest tests/ -v         # 23 tests
```

The suite spins up the app against an in-memory SQLite database per test, so it's fast and
leaves no state behind.

## Docker

```bash
# Run the full stack (API + PostgreSQL) locally
docker compose up --build
curl http://localhost:5000/health
```

The image runs as a non-root user, declares a `HEALTHCHECK`, binds to `$PORT` (defaulting to
5000), and serves via gunicorn. `flask init-db` runs on startup to create tables idempotently.

## CI/CD & security

Every push to `main` and every pull request runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

1. **Lint & test** — `ruff` + `pytest` on Python 3.12 (matching production).
2. **Dependency audit** — `pip-audit` against `requirements.txt`.
3. **Docker build & image scan** — builds the image and scans it with Trivy (fails on fixable
   CRITICAL/HIGH CVEs). This job only runs if lint, tests, and audit pass.

Additional hardening: password hashing (Werkzeug), JWT-signed sessions, per-IP rate limiting,
non-root container, and weekly [Dependabot](.github/dependabot.yml) update PRs for both pip and
GitHub Actions. The Trivy action is pinned to an immutable release tag as a supply-chain
precaution.

## Environment variables

| Variable | Purpose | Example |
|---|---|---|
| `FLASK_CONFIG` | Selects config: `development` / `testing` / `production` | `production` |
| `DATABASE_URL` | SQLAlchemy connection string (`postgres://` is auto-normalised) | `postgresql://…/neondb?sslmode=require` |
| `SECRET_KEY` | Flask session/signing key | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `JWT_SECRET_KEY` | Signing key for JWTs | (a second random 32-byte hex string) |

Secrets are never committed — `.env` is gitignored, and production values live only in the host's
environment settings.

## Project structure

```text
cloudops-lab/
├── app/
│   ├── __init__.py          # application factory + blueprint registration
│   ├── config.py            # dev / test / prod config
│   ├── extensions.py        # db, jwt, limiter singletons
│   ├── models/
│   │   ├── user.py          # User (auth, password hashing)
│   │   └── cloud_service.py # CloudService (+ allowed-value sets)
│   ├── routes/
│   │   ├── health.py
│   │   ├── auth.py          # register, login, profile
│   │   └── services.py      # CRUD, filtering, health updates
│   └── utils/
│       ├── errors.py        # APIError + global error/JWT handlers
│       └── validators.py    # required-field, enum, URL validation
├── tests/                   # pytest suite (auth + services)
├── .github/
│   ├── workflows/ci.yml     # lint · test · audit · build + scan
│   └── dependabot.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml           # ruff config
└── run.py
```

## Roadmap

- [x] Phase 1 — Flask setup + health endpoint
- [x] Phase 2 — Database models (User, CloudService)
- [x] Phase 3 — Authentication (register, login, JWT, ownership)
- [x] Phase 4 — Service CRUD + filtering
- [x] Phase 5 — Validation + error handling
- [x] Phase 6 — Docker + Docker Compose
- [x] Phase 7 — Pytest test suite
- [x] Phase 8 — GitHub Actions CI
- [x] Phase 9 — Security scanning + rate limiting (pip-audit, Trivy, Dependabot)
- [x] Phase 10 — Cloud deployment (Render + Neon)
