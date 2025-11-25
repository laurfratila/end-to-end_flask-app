# ---- Base image ----
FROM python:3.12-slim

# ---- Python & pip behavior ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ---- Workdir ----
WORKDIR /app

# ---- System deps (for building some wheels) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ---- App deps ----
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- App code ----
COPY . .

# ---- Ensure instance directory exists (SQLite lives here) ----
RUN mkdir -p /app/instance

# ---- Runtime env ----
# FLASK_APP should match your entry (microblog.py defines `app`, or use wsgi.py if you have a factory)
ENV FLASK_APP=microblog.py \
    FLASK_ENV=production \
    PORT=8000

# ---- Network ----
EXPOSE 8000

# ---- Start: run DB migrations, then launch Gunicorn ----
# Works with SQLite (default) or Postgres if you pass DATABASE_URL at runtime
CMD ["sh", "-c", "flask db upgrade && gunicorn -b 0.0.0.0:${PORT} microblog:app"]
