# 23_api.md

## **Chapter 23 — Application Programming Interfaces (APIs)**

---

###  Overview

Chapter 23 adds a fully functional **REST API layer** to the microblog application.
This enables:

* External applications to interact with user and post data
* Mobile or SPA frontends to consume backend functionality
* Machine-to-machine communication

The API supports:

* Authentication via tokens
* CRUD operations on posts
* Pagination
* Error responses in JSON format

This chapter also introduces the API blueprint and standardized response structures.

---

##  1. API Blueprint Structure

API routes live inside their own blueprint:

```
app/
└── api/
    ├── __init__.py
    ├── routes.py
    └── errors.py
```

### `app/api/__init__.py`

```python
from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routes, errors
```

Blueprint registered in `create_app()` with a `/api` prefix:

```python
app.register_blueprint(api_bp, url_prefix='/api')
```

---

##  2. Token-Based Authentication

Unlike session-based auth used in the browser, API clients authenticate via **Bearer tokens**.

### Token Generation

In `User` model:

```python
import base64
from datetime import datetime, timedelta
import os

class User(UserMixin, db.Model):

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now:
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
```

### Notes

* Tokens expire automatically
* A revoked token is simply expired immediately
* API routes authenticate users via `check_token()`

---

##  3. API Authentication Decorator

To enforce token authentication:

```python
from flask import g
from functools import wraps


def token_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        g.current_api_user = User.check_token(token)
        if g.current_api_user is None:
            return error_response(401, 'Invalid or missing token')
        return f(*args, **kwargs)
    return decorated
```

API clients now send headers like:

```http
Authorization: Bearer <token>
```

---

##  4. Serialization Helpers

Models expose dictionary-based representations for API output.

### In `User` model:

```python
def to_dict(self):
    return {
        'id': self.id,
        'username': self.username,
        'about_me': self.about_me,
        'last_seen': self.last_seen.isoformat() + 'Z' if self.last_seen else None,
        '_links': {
            'self': url_for('api.get_user', id=self.id),
            'posts': url_for('api.get_posts', id=self.id)
        }
    }
```

### In `Post` model:

```python
def to_dict(self):
    return {
        'id': self.id,
        'body': self.body,
        'timestamp': self.timestamp.isoformat() + 'Z',
        'author': self.author.username,
        '_links': {
            'self': url_for('api.get_post', id=self.id)
        }
    }
```

These structures enable consistent and discoverable JSON responses.

---

##  5. Standardized Error Responses

Errors should always be returned as JSON:

### `app/api/errors.py`

```python
from flask import jsonify


def error_response(status_code, message=None):
    payload = {'error': message or 'Unexpected error'}
    response = jsonify(payload)
    response.status_code = status_code
    return response


def not_found(message='Not found'):  # 404
    return error_response(404, message)
```

### Registered globally

```python
@bp.app_errorhandler(404)
def not_found_error(error):
    return not_found('Resource not found')
```

---

##  6. API Routes

### Get User

```python
@bp.route('/users/<int:id>', methods=['GET'])
@token_auth_required
def get_user(id):
    user = db.session.get(User, id) or abort(404)
    return user.to_dict()
```

### Get a User’s Posts

```python
@bp.route('/users/<int:id>/posts', methods=['GET'])
@token_auth_required
def get_user_posts(id):
    user = db.session.get(User, id) or abort(404)
    posts = user.posts.order_by(Post.timestamp.desc())
    return {'items': [p.to_dict() for p in posts]}
```

### Create a Post

```python
@bp.route('/posts', methods=['POST'])
@token_auth_required
def create_post():
    data = request.get_json() or {}
    if 'body' not in data:
        return error_response(400, 'Body text required')

    post = Post(body=data['body'], author=g.current_api_user)
    db.session.add(post)
    db.session.commit()
    return post.to_dict(), 201
```

---

##  7. Pagination Support

Pagination helper reused from website:

```python
def paginated_response(query, page, per_page):
    items = db.paginate(query, page=page, per_page=per_page, error_out=False)
    return {
        'items': [item.to_dict() for item in items.items],
        'total': items.total,
        'page': page,
        'pages': items.pages
    }
```

Example usage:

```python
return paginated_response(sa.select(Post), page, 20)
```

---

##  8. Full API Workflow

Clients can:

1. Request a token
2. Send requests authenticated with `Authorization: Bearer <token>`
3. Retrieve or create posts
4. Query users
5. Receive JSON responses exclusively

The API is now fully suitable for integration with any frontend or external system.

---

##  Final Notes

This chapter completes the major functionality of the Flask Mega-Tutorial:

* Web UI (Chapters 1–20)
* Notifications and background tasks (21–22)
* Search (16)
* Deployment (19)
* Full REST API (23)


