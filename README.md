# CloudOps Lab

![CI](https://github.com/Wh1skeyyyy/CloudOps-LAB/actions/workflows/ci.yml/badge.svg)

A REST API for registering and monitoring cloud services (APIs, databases, frontends,
containers) across environments. Built to demonstrate backend engineering, authentication,
database design, Docker, CI/CD, and security practices.

> **Status: Phases 1–8 complete** — auth (JWT), service CRUD with ownership, validation
> and unified JSON error handling, Docker + Compose, a 23-test pytest suite, and a GitHub
> Actions CI pipeline (lint → test → audit → image build + scan). Security hardening and
> cloud deployment are next.

## Tech stack

Python · Flask · Flask-SQLAlchemy · Flask-JWT-Extended · PostgreSQL (SQLite for local dev)

## Getting started

```bash
# 1. Clone and enter the project
cd cloudops-lab

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env             # then edit the secrets

# 5. Create the database tables
export FLASK_APP=run.py          # Windows: set FLASK_APP=run.py
flask init-db

# 6. Run the server
flask run
# or: python run.py
```

## Verify it works

```bash
curl http://127.0.0.1:5000/health
# {"application": "CloudOps Lab", "status": "healthy"}
```

## Project structure

```text
cloudops-lab/
├── app/
│   ├── __init__.py        # application factory
│   ├── config.py          # dev / test / prod config
│   ├── extensions.py      # db, jwt instances
│   ├── models/
│   │   ├── user.py
│   │   └── cloud_service.py
│   └── routes/
│       └── health.py
├── run.py
├── requirements.txt
├── .env.example
└── .gitignore
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
- [ ] Phase 9 — Security scanning (pip-audit, Trivy, Dependabot)
- [ ] Phase 10 — Cloud deployment (Render / Railway)
```
