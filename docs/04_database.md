# 04_database.md

## **Chapter 4 — Database Integration**

---

###  Overview

Chapter 4 adds persistent data storage to the application using **SQLAlchemy** and **Flask‑SQLAlchemy**, along with **Flask‑Migrate** for schema versioning.

This chapter introduces:

* Database configuration
* ORM models for users and posts
* Database migrations
* Basic querying patterns
* Application context usage

These components establish long-term data handling for authentication, posts, followers, notifications, search indexing, and API operations.

---

###  1. Database Configuration (`config.py`)

The configuration adds a database URI pointing to SQLite by default.

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Notes

* SQLite is used during development
* PostgreSQL or MySQL can be used in production via `DATABASE_URL`
* `SQLALCHEMY_TRACK_MODIFICATIONS` is disabled for performance

---

###  2. Initializing SQLAlchemy and Migrations (`app/__init__.py`)

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # blueprints imported later in chapter 15

    return app
```

### Key Components

* `SQLAlchemy()` creates the ORM engine
* `Migrate()` manages database schema changes
* Both are lazily initialized inside `create_app`

---

###  3. Defining the User Model (`app/models.py`)

```python
from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return f'<User {self.username}>'
```

### Explanation

* ORM model maps to `user` table
* Type hints are integrated using SQLAlchemy 2.0 style
* `mapped_column()` defines fields
* Database-level constraints (indexed, unique)

This model evolves in later chapters: password hashing, relationships, Flask-Login mixins, follower table, avatar generation, timestamps, and API token methods.

---

###  4. Defining the Post Model

```python
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))

    author: so.Mapped['User'] = so.relationship(back_populates='posts')
```

Corresponding addition to the User model:

```python
posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
```

### Notes

* One‑to‑many user‑post relationship
* Posts are indexed by timestamp for feed ordering
* Models use SQLAlchemy relationship mapping rather than raw foreign keys

---

###  5. Database Migration Setup

Initialize a migration repository:

```bash
flask db init
```

Generate migrations:

```bash
flask db migrate -m "users and posts table"
```

Apply migrations:

```bash
flask db upgrade
```

### How It Works

* Alembic compares model definitions to the DB schema
* Writes migration scripts under `migrations/versions/`
* Upgrade applies schema changes
* Downgrade reverses them

Migrations ensure safe schema evolution throughout the project.

---

###  6. Working with the Database in Flask Shell

Flask provides a shell context for convenient ORM usage.

`microblog.py` includes:

```python
from app import db, create_app
from app.models import User, Post

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
```

Start interactive shell:

```bash
flask shell
```

### Example Usage

#### Create users:

```python
u = User(username='john', email='john@example.com')
db.session.add(u)
db.session.commit()
```

#### Query users:

```python
users = User.query.all()
```

#### Create a post:

```python
p = Post(body='First post!', author=u)
db.session.add(p)
db.session.commit()
```

#### Retrieve posts:

```python
u.posts.select()
```

This workflow is foundational for follower relationships, timeline queries, notifications, and the search index.

---

###  7. Sessions, Commits, and Rollbacks

SQLAlchemy session behavior:

* `db.session.add()` adds operations to the transaction
* `db.session.commit()` writes all staged changes
* `db.session.rollback()` reverts uncommitted changes on error

This ensures database consistency.

---

###  8. Role of the Database Layer in the Project

The DB layer enables:

* User authentication
* Blog post storage
* Follower relationships
* Password reset tokens
* Notifications & message queues
* Full‑text indexing
* API resource serialization
* Background job state storage

This chapter establishes the persistence layer for all higher‑level features.

---



