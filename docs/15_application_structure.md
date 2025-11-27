# 15_application_structure.md

## **Chapter 15 — Improved Application Structure (Blueprints & Factory Pattern)**

---

###  Overview

Chapter 15 restructures the application into a clean, scalable architecture using:

* The **application factory pattern**
* **Blueprints** for modular organization
* Separation of concerns across subsystems
* Package-based organization for errors, authentication, main routes, and APIs

This architectural upgrade prepares the project for complex features: REST APIs, background jobs, notifications, and search.

---

##  1. Motivation for a Better Structure

As the project grows, the earlier flat structure becomes difficult to maintain:

* Routes, forms, models, and errors intermingle
* Hard to reuse subsystems across projects
* Difficult to test different configurations

Blueprints and a factory-based initialization resolve these issues.

---

##  2. New Project Layout

The application is reorganized into multiple packages:

```
app/
│
├── __init__.py
├── models.py
│
├── main/
│   ├── __init__.py
│   ├── routes.py
│   ├── forms.py
│   └── errors.py
│
├── auth/
│   ├── __init__.py
│   ├── routes.py
│   ├── forms.py
│   └── email.py
│
├── errors/
│   ├── __init__.py
│   └── handlers.py
│
└── api/
    ├── __init__.py
    └── routes.py
```

### Notes

* Each subsystem becomes isolated in its own module
* Blueprints expose routes, templates, and views
* Models remain centralized, as they are shared across modules

---

##  3. The Application Factory (`create_app`)

The factory pattern allows multiple instances of the app with different configs:

```python
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from flask_moment import Moment

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
babel = Babel()
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    moment.init_app(app)

    # register blueprints
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
```

### Benefits

* Cleaner initialization logic
* Subsystems are independent and easy to test
* Allows multiple configurations: dev, test, production

---

##  4. Blueprint Structure

### Example: `app/main/__init__.py`

```python
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes, errors
```

### Example: `app/auth/__init__.py`

```python
bp = Blueprint('auth', __name__)

from app.auth import routes, forms
```

Each blueprint contains its own:

* Routes
* Templates
* Forms
* Error handlers (if needed)

---

##  5. Updating Routes to Use Blueprints

Example from `app/main/routes.py`:

```python
from app.main import bp
from app.models import User, Post
from flask_login import login_required


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # timeline rendering
    ...
```

Example from `app/auth/routes.py`:

```python
from app.auth import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    ...
```

### Notes

* Route functions now belong to their blueprint instead of the global app
* URL prefixes (such as `/auth`) are defined at registration time

---

##  6. Template Reorganization

Templates are also grouped by blueprint:

```
app/templates/
│
├── main/
│   ├── index.html
│   ├── user.html
│   └── _post.html
│
├── auth/
│   ├── login.html
│   ├── register.html
│   └── reset_password.html
│
└── errors/
    ├── 404.html
    └── 500.html
```

Blueprints allow Flask to automatically search inside:

```
app/templates/<blueprint_name>/...
```

---

##  7. Shell Context Updated

In `microblog.py`:

```python
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
```

The shell context remains globally available even though routes are now organized.

---

##  8. Architectural Impact on the Full Application

The new structure supports:

* Scalable routing
* API versioning
* Modular subsystems
* Cleaner error isolation
* Improved testability
* Easier maintenance as features expand

Future chapters (API, jobs, notifications, search) rely heavily on this improved design.

---

