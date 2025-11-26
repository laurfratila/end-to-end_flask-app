# 07_error_handling.md

## **Chapter 7 — Error Handling**

---

###  Overview

Chapter 7 enhances the robustness of the application by adding custom error handling.
The default Flask error pages are replaced with user‑friendly versions, and the project introduces:

* Custom 404 (Not Found) and 500 (Server Error) handlers
* Error templates
* Database session cleanup on errors
* Optional email reporting for production

These mechanisms create a safer, more professional application that gracefully handles failures.

---

##  1. Error Blueprint Structure

Error handlers are typically placed in their own module or blueprint.
Before blueprint refactoring (Chapter 15), the handlers may live directly in `app/errors.py`.

Typical structure:

```
app/
├── errors/
│   ├── __init__.py
│   ├── handlers.py
│   └── templates/errors/
│       ├── 404.html
│       └── 500.html
```

---

##  2. Custom Error Handlers

### **404 — Page Not Found**

```python
from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
```

### **500 — Internal Server Error**

```python
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
```

### Key Notes

* Both functions return `(template, status_code)`
* The rollback in the 500 handler ensures the DB session isn't left in an invalid state

These handlers keep the application stable in case of unexpected behavior.

---

##  3. Error Templates

### **404.html**

```html
{% extends "base.html" %}

{% block content %}
  <h1>404 - Page Not Found</h1>
  <p>The requested page does not exist.</p>
{% endblock %}
```

### **500.html**

```html
{% extends "base.html" %}

{% block content %}
  <h1>500 - Internal Server Error</h1>
  <p>An unexpected error occurred. Please try again later.</p>
{% endblock %}
```

Templates inherit the main layout, keeping UI consistent.

---

##  4. Email Notifications for Errors (Production)

When running in production, it is useful to receive error reports by email.

In `config.py`:

```python
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMINS = ['your-email@example.com']
```

Then, in `create_app()`:

```python
if not app.debug and app.config['MAIL_SERVER']:
    auth = None
    if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
        auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

    secure = () if app.config['MAIL_USE_TLS'] else None

    mail_handler = SMTPHandler(
        mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        fromaddr='no-reply@' + app.config['MAIL_SERVER'],
        toaddrs=app.config['ADMINS'],
        subject='Microblog Failure',
        credentials=auth,
        secure=secure
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
```

### Behavior

* Errors trigger an email containing the full stack trace
* Only enabled outside debug mode
* Helps track production issues without exposing details to users

---

##  5. Logging to Files

To preserve logs over time:

```python
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
```

### Notes

* Logs rotate at 10KB with up to 10 archived files
* Includes timestamp, log level, and file location
* Useful for debugging issues that do not necessarily cause exceptions

---

##  6. Role in the Full Application

The error handling system supports:

* Clean UX for invalid routes and server issues
* Safety around database session state
* Reliable production diagnostics via email and file logs
* Foundation for API-specific error responses (Chapter 23)
* Integration with background jobs and asynchronous tasks

---


