# 03_web_forms.md

## **Chapter 3 — Web Forms**

---

###  Overview

Chapter 3 introduces **web forms** using the `Flask-WTF` extension, which integrates Flask with the powerful `WTForms` library. Forms enable user interaction with the application—login, registration, profile editing, posting content, password resets, and more.

This chapter establishes a secure, scalable way to handle form submission, server-side validation, and CSRF protection.

---

###  1. Flask-WTF Setup

`Flask-WTF` is installed and configured to manage forms with built‑in features:

* CSRF protection
* Field validation
* Error handling
* Python class-based form definitions

Configuration is added in `config.py`:

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
```

### Purpose of `SECRET_KEY`

* Required for CSRF protection
* Used to sign form tokens
* Also used later by sessions, login, and other cryptographic features

---

###  2. Creating a Form Class (`forms.py`)

The login form is the first form in the project:

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
```

### Key Concepts

* Each field is a Python attribute
* Validators enforce rules (e.g., DataRequired)
* Class structure enables reuse and testing

This form will be rendered in `login.html` and processed in the login route.

---

###  3. Displaying the Form in a Template

Example login template:

```html
{% extends "base.html" %}

{% block content %}
  <h1>Sign In</h1>
  <form action="" method="post" novalidate>
      {{ form.hidden_tag() }}

      <p>
        {{ form.username.label }}<br>
        {{ form.username(size=32) }}
      </p>

      <p>
        {{ form.password.label }}<br>
        {{ form.password(size=32) }}
      </p>

      <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
      <p>{{ form.submit() }}</p>
  </form>
{% endblock %}
```

### Notes on Template Behavior

* `form.hidden_tag()` inserts the CSRF token
* Fields render themselves as HTML
* Form errors can be displayed by looping over `form.<field>.errors`

---

###  4. Form View Function (`routes.py`)

The form requires a route that handles both `GET` and `POST`:

```python
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for user {form.username.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
```

### View Logic Breakdown

* `validate_on_submit()` runs only on POST
* Performs all validations
* Returns True if submission is valid
* Flash messages provide feedback

This pattern is used throughout the project for all form handling.

---

###  5. CSRF Protection

Flask-WTF automatically adds CSRF protection to all forms.

How it works:

* A secure token is inserted via `form.hidden_tag()`
* Every POST request includes the token
* Token is validated server-side

This prevents cross-site request forgery attacks.

---

###  6. Form Validation Flow

`form.validate_on_submit()` performs:

1. Check if request method is POST
2. Parse form data from request
3. Apply validators on each field
4. Return True when all validations pass
5. Otherwise return False

Errors are accessible via:

```
form.<field>.errors
```

---

###  7. How Forms Fit Into the Project

Forms are essential to nearly every major feature:

* Login and registration
* Editing profiles
* Posting content
* Resetting passwords
* Following/unfollowing users
* Searching
* Submitting AJAX-powered translations
* Managing background job triggers

This chapter provides the foundational structure for all upcoming user interactions.

---

###  8. Example: Adding Form Validation Errors to Template

To display validation errors:

```html
<p>
  {{ form.username.label }}<br>
  {{ form.username() }}<br>
  {% for error in form.username.errors %}
    <span style="color: red">[{{ error }}]</span>
  {% endfor %}
</p>
```

This pattern becomes important for user registration, password resets, and profile editing.

---

###  9. Summary of Key Components Introduced

* **FlaskForm** class for structuring forms
* **WTForms fields** (`StringField`, `PasswordField`, etc.)
* **Field validators** (`DataRequired`, `Email`, `EqualTo`, etc.)
* **CSRF protection** via `hidden_tag()`
* **Rendering fields in templates** using Jinja2
* **validate_on_submit()** request handling pattern

These concepts enable safe, robust user interactions across the entire system.

---

