# Microblog — Flask Mega-Tutorial Project

A complete, production-ready microblogging platform built by following and extending Miguel Grinberg’s **Flask Mega-Tutorial**.
This project implements **all major chapters** including templates, forms, authentication, pagination, followers, email support, UI enhancements, localization, AJAX features, full-text search, background jobs, REST APIs, and Docker deployment.

The project uses **SQLite** as its primary database, making it lightweight, portable, and easy to run anywhere.

---

#  Features Overview

### **Core Web Application**

* User registration & authentication (Flask-Login)
* Profile pages with Gravatar avatars
* Followers & personalized timeline
* Post creation & pagination
* Error handling system

### **Advanced Capabilities**

* Email support (password resets & error reporting)
* UI facelift with Bootstrap 5
* Internationalization (i18n) + localization (l10n)
* Date/time rendering with Moment.js
* AJAX-based post translation via Microsoft Translator API
* Full-text search using Elasticsearch helper layer
* Background jobs using Redis Queue (RQ)
* Notification system for real-time task updates
* REST API with token-based authentication

### **Deployment**

* Fully containerized Docker environment
* Gunicorn production server
* SQLite persistence via mounted volumes

---

#  Project Structure

```
microblog/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── tasks.py
│   ├── templates/
│   ├── translations/
│   │
│   ├── main/          ← UI pages, homepage, explore, profile
│   ├── auth/          ← login, registration, password reset
│   ├── errors/        ← error handlers
│   └── api/           ← REST API endpoints
│
├── migrations/        ← database migration scripts
├── docs/              ← full multi-chapter documentation
├── microblog.py       ← entry point for Flask application
├── config.py          ← configuration settings
├── Dockerfile
├── requirements.txt
└── README.md
```

---

#  Quick Start (Local Environment)

### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

(Optional — defaults will be used if omitted.)

```bash
export FLASK_APP=microblog.py
export SECRET_KEY="devkey"
```

### 4. Initialize the SQLite database

```bash
flask db upgrade
```

### 5. Run the development server

```bash
flask run
```

The application is now available at:

```
http://localhost:5000
```

---

#  Running with Docker

### 1. Build the image

```bash
docker build -t microblog .
```

### 2. Run the container

```bash
docker run -p 5000:5000 microblog
```

The SQLite database (`app.db`) will be created inside the container.
Use a Docker volume if you want persistent storage:

```bash
docker run -p 5000:5000 -v microblog_data:/app microblog
```

---

#  Full Documentation

Every chapter of the project is fully documented in the `docs/` folder.
Below is the complete list:

### **Chapters 1–23 Documentation**

```
docs/
├── 01_hello_world.md
├── 02_templates.md
├── 03_web_forms.md
├── 04_database.md
├── 05_user_logins.md
├── 06_profile_page_and_avatars.md
├── 07_error_handling.md
├── 08_followers.md
├── 09_pagination.md
├── 10_email_support.md
├── 11_facelift.md
├── 12_dates_and_times.md
├── 13_internationalization_localization.md
├── 14_ajax_translation.md
├── 15_application_structure.md
├── 16_full_text_search.md
├── 19_docker_deployment.md
├── 20_javascript_magic.md
├── 21_user_notifications.md
├── 22_background_jobs.md
└── 23_api.md
```

Each chapter provides:

* Explanations of what the feature does
* Step‑by‑step implementation details
* Code samples
* Integration notes

---

#  Testing

The project uses Flask’s built-in test utilities and SQLAlchemy’s in-memory SQLite mode for isolated tests.

To run tests (if implemented):

```bash
pytest
```

---

# 🔧 Configuration

All configuration is stored in `config.py` and can be overridden via environment variables.

Common variables:

```
SECRET_KEY
DATABASE_URL
MAIL_SERVER
MAIL_PORT
MAIL_USE_TLS
MAIL_USERNAME
MAIL_PASSWORD
MS_TRANSLATOR_KEY
REDIS_URL
ELASTICSEARCH_URL
```

---

#  API Overview

The `/api` blueprint exposes a REST API supporting:

* User retrieval
* Token authentication
* Post creation
* Pagination

Example: Get user information

```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/users/1
```

---

#  License

This project can use any license you choose (MIT suggested).
Add a `LICENSE` file to formalize distribution rights.

---

#  Acknowledgements

Built following the structure and concepts of Miguel Grinberg’s **Flask Mega-Tutorial**, with additional enhancements and modernizations.


