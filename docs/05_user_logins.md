# 05_user_logins.md

## **Chapter 5 — User Logins**

---

###  Overview

Chapter 5 introduces the **authentication system** using `Flask-Login`.
This adds:

* User session management
* Login/logout functionality
* Password hashing
* Login-required access control
* Redirects for unauthorized users

This chapter establishes the core of user authentication, enabling protected routes, personalized content, timeline feeds, profile pages, followers, notifications, and API authentication.

---

###  1. Password Hashing

Passwords are never stored directly.
Instead, the User model implements secure hashing:

```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    # fields...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### Notes

* `generate_password_hash()` applies strong cryptographic hashing
* `check_password_hash()` safely verifies user-provided passwords
* No plaintext passwords ever stored in the database

---

###  2. Integrating Flask-Login

Initialization occurs in `app/__init__.py`:

```python
from flask_login import LoginManager

login = LoginManager()
login.login_view = 'auth.login'  # updated later when blueprints are added

login.init_app(app)
```

### Purpose

* Manages user sessions
* Loads current user on each request
* Provides `login_required` decorator
* Handles automatic redirects to login page

---

###  3. Adding UserMixin

`Flask-Login` expects four attributes:

* `is_authenticated`
* `is_active`
* `is_anonymous`
* `get_id()`

Instead of implementing them manually, the model inherits from `UserMixin`:

```python
from flask_login import UserMixin

class User(UserMixin, db.Model):
    # fields...
    pass
```

---

###  4. User Loader Function

Flask-Login needs a callback to load users by ID:

```python
from app import login

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
```

### Purpose

* Restores logged-in users from session storage
* Allows `current_user` to be available on each request

---

###  5. Login Route

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        # redirect protection
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)
```

### Highlights

* Blocks access to login page if already logged in
* Validates user credentials
* Uses secure password verification
* Implements `remember me` cookie functionality
* Supports redirecting to protected pages via `next` parameter

---

###  6. Logout Route

```python
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
```

### Notes

* Clears authentication session
* Redirects user back to public page

---

###  7. Protecting Routes with `@login_required`

Example:

```python
from flask_login import login_required

@app.route('/index')
@login_required
def index():
    # view logic
```

### Behavior

* If user is **not logged in** → redirect to login page
* If user is **authenticated** → render normally

`login.login_view` determines which login endpoint is used for the redirect.

---

###  8. Using `current_user`

Flask-Login injects a `current_user` proxy:

```python
from flask_login import current_user
```

It provides:

* Access to the logged-in user's data
* Status (authenticated or anonymous)
* Integration with templates

Example in templates:

```html
{% if current_user.is_authenticated %}
  Hello, {{ current_user.username }}!
{% endif %}
```

This is foundational for profile pages, navigation bars, posting forms, and feed personalization.

---

###  9. Login Redirect Security

When a user tries to access a protected page while logged out, Flask-Login adds a query parameter:

```
/login?next=/profile
```

After successful login, the application:

* Validates that `next` is a **relative path** (prevents open redirects)
* Redirects to that page

This pattern is essential for secure UX and is reused for registration, password resets, and role-based routing.

---

###  10. Authentication in Context of the Full Project

Authentication enables:

* User profiles
* Posting and following workflows
* Personalized timeline pages
* Private messaging and notifications
* API authentication
* Admin-only views
* Background job ownership

It is one of the central systems that the rest of the application builds upon.

---

