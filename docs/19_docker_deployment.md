# 19_docker_deployment.md

## **Chapter 19 — Deployment on Docker Containers**

---

###  Overview

Chapter 19 introduces **containerized deployment** using **Docker**.
In this project, the database is **SQLite**, stored as a file (for example `app.db`) inside the container or on a mounted volume.

This chapter focuses on:

* Creating a production-ready Docker image
* Running the application with Gunicorn
* Managing configuration via environment variables
* Using Docker Compose to run the web app as a service

The goal is to make the application portable, reproducible, and easy to deploy while still using SQLite.

---

##  1. Production WSGI Server: Gunicorn

Flask’s built-in development server is **not** suitable for production.
Gunicorn is used instead.

Install Gunicorn:

```bash
pip install gunicorn
```

Gunicorn entry point:

```bash
gunicorn -b :5000 microblog:app
```

---

##  2. Dockerfile (Production Build with SQLite)

A production Dockerfile using SQLite as the database:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any are needed by Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose Gunicorn port
EXPOSE 5000

# Run application via Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "microblog:app"]
```

### Notes

* SQLite does not require a separate container or network service
* The SQLite database file (e.g. `app.db`) will be created inside `/app` by SQLAlchemy
* For persistence across container restarts, a Docker volume can be mounted on `/app`

---

##  3. Building and Running the Image

### Build the image

```bash
docker build -t microblog:latest .
```

### Run the container

```bash
docker run -p 5000:5000 microblog:latest
```

Visit:

```text
http://localhost:5000
```

At this point, the application runs inside Docker using SQLite for the database.

---

##  4. Environment Variables for Deployment

Important settings are still configurable via environment variables, even with SQLite:

```bash
docker run -p 5000:5000 \
  -e SECRET_KEY="production-secret" \
  -e MAIL_SERVER=smtp.googlemail.com \
  -e MAIL_PORT=587 \
  -e MAIL_USE_TLS=1 \
  -e MAIL_USERNAME="you@example.com" \
  -e MAIL_PASSWORD="your-password" \
  microblog:latest
```

If you keep SQLite:

* `DATABASE_URL` can be omitted and the default SQLite URI from `Config.SQLALCHEMY_DATABASE_URI` will be used
* Alternatively, you can explicitly point to a file path inside the container, for example:

```bash
-e DATABASE_URL="sqlite:////app/app.db"
```

---

##  5. Docker Compose with SQLite

When using SQLite, there is no need for a separate database container.
`docker-compose.yml` can focus solely on the web application (and optional services like Elasticsearch or Redis if you use them):

```yaml
version: "3"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=change-me
      - DATABASE_URL=sqlite:////app/app.db
      # - ELASTICSEARCH_URL=http://es:9200   # optional, if you run Elasticsearch
    volumes:
      - app_data:/app

  # Optional: Elasticsearch service for full-text search
  # es:
  #   image: docker.elastic.co/elasticsearch/elasticsearch:8.9.0
  #   environment:
  #     - discovery.type=single-node
  #   ports:
  #     - "9200:9200"

volumes:
  app_data:
```

### Notes

* `app_data` volume stores both the source code (if you copy it there) and the SQLite `app.db` file
* All data persists across container restarts
* You can uncomment and configure additional services (like Elasticsearch) as needed

---

##  6. Database Initialization in Docker

With SQLite, migrations work the same way inside the container.

After starting the stack:

```bash
docker-compose up -d
```

Run migrations inside the `web` container:

```bash
docker-compose exec web flask db upgrade
```

You can also open a Flask shell inside the container:

```bash
docker-compose exec web flask shell
```

---

##  7. Static Files, Logs & SQLite File Persistence

### Static files

Served by Flask from the `static/` directory as usual.

### Logs

Gunicorn logs appear via container logs:

```bash
docker logs <container-id>
```

### SQLite database file

* Stored at the path configured in `SQLALCHEMY_DATABASE_URI` (commonly `/app/app.db` inside the container)
* Persisted across restarts via the mounted Docker volume (`app_data` in the example)

---

##  8. Deployment Workflow with SQLite

Typical steps for deploying the SQLite-based application:

1. Build image:

```bash
docker build -t microblog:prod .
```

2. (Optional) Push to a registry

```bash
docker push registry.example.com/microblog:prod
```

3. Start services with Docker Compose:

```bash
docker-compose up -d
```

4. Run migrations in the running container:

```bash
docker-compose exec web flask db upgrade
```

5. Monitor logs and app status using `docker logs` and `docker ps`.

---

##  9. Role of Docker Deployment in the Full System

Even with SQLite, Docker provides:

* Environment isolation
* Repeatable deployments
* Easy configuration via environment variables
* A base for adding more services later (search, queues, etc.)

This containerized setup ensures that the same image can be run locally, in testing, or in production with minimal changes.

---

