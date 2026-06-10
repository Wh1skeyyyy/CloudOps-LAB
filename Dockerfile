# CloudOps Lab — production container.
# Python 3.12 is chosen because psycopg2-binary ships prebuilt wheels for it
# (3.14, while newer, may not yet have wheels and would force a slow source build).
FROM python:3.12-slim

# curl is used by the HEALTHCHECK below; clean apt caches to keep the layer slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

ENV FLASK_APP=run.py \
    FLASK_CONFIG=production \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python deps first so the layer cache survives source changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY . .

# Run as a non-root user (security best practice — defends against
# container escapes turning into root-on-host)
RUN useradd --create-home --shell /bin/bash app \
 && chown -R app:app /app
USER app

EXPOSE 5000

# Liveness probe — Docker / Render / Railway / k8s all read this
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:5000/health || exit 1

# Create tables on startup (idempotent — create_all skips existing tables),
# then `exec` so gunicorn replaces the shell and receives SIGTERM directly.
CMD flask init-db && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - run:app
