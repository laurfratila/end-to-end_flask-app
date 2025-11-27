# 13_internationalization_localization.md

## **Chapter 13 — Internationalization (i18n) & Localization (l10n)**

---

###  Overview

Chapter 13 adds **multi-language support** to the application using **Flask-Babel**.
This enables the application to:

* Translate text into multiple languages
* Format dates/times based on locale
* Detect user language preferences
* Provide translatable UI elements

This chapter lays the foundation for a globally usable interface.

---

##  1. Installing and Configuring Flask-Babel

Installation:

```bash
pip install flask-babel
```

Configuration (`config.py`):

```python
class Config:
    LANGUAGES = ['en', 'es']
```

Initialization in `app/__init__.py`:

```python
from flask_babel import Babel
from flask import request

babel = Babel()
babel.init_app(app)

@babel.locale_selector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])
```

### Notes

* `get_locale()` automatically selects the best language using the browser’s `Accept-Language` header.
* Supported languages are defined in `LANGUAGES`.
* This system scales easily to dozens of languages.

---

##  2. Marking Text for Translation

Flask-Babel provides translation helpers:

* `_()` – immediate translation
* `_l()` – lazy translation (evaluated later)

Example in Python:

```python
from flask_babel import _
flash(_('Invalid username or password'))
```

Example in templates:

```html
<title>{{ _('Welcome to Microblog') }}</title>
```

Lazy translations (`_l()`) are used for field labels and form messages.

Example in forms:

```python
from flask_babel import _l
username = StringField(_l('Username'))
```

---

##  3. Creating Translation Template

Create a `babel.cfg` file:

```cfg
[python: app/**.py]
[jinja2: app/templates/**.html]
```

Extract translatable strings:

```bash
pybabel extract -F babel.cfg -k _l -o messages.pot .
```

This generates a template (`.pot`) listing all marked phrases.

---

##  4. Generating a New Language Catalog

For Spanish (`es`):

```bash
pybabel init -i messages.pot -d app/translations -l es
```

This creates:

```
app/translations/es/LC_MESSAGES/messages.po
```

Developers translate the English strings inside `.po` files.

Compile translations:

```bash
pybabel compile -d app/translations
```

---

##  5. Using Translations in Templates

Example navigation bar:

```html
<li class="nav-item">
  <a class="nav-link" href="#">{{ _('Explore') }}</a>
</li>
```

Example login page:

```html
<h1>{{ _('Sign In') }}</h1>
```

All user-facing text becomes translatable.

---

##  6. Localized Date/Time Formatting

Flask-Moment integrates with Flask-Babel automatically.

```html
<p>{{ moment(post.timestamp).format('LLL') }}</p>
```

`LLL` format adapts to the user’s language.

* English → *October 2, 2024 5:32 PM*
* Spanish → *2 de octubre de 2024 17:32*

Localization applies across posts, timestamps, notifications, and activity logs.

---

##  7. Language Selection Logic

Currently, language selection is based exclusively on browser headers.

Possible extensions (outside this chapter):

* User-specific language settings stored in DB
* URL-based language switching
* Dedicated language dropdown in navbar

The chapter provides the automatic foundation.

---

##  8. Role of i18n in the Full Application

Internationalization supports:

* Email templates
* Form labels and validation messages
* Page titles and UI elements
* Error messages
* API error responses (Chapter 23)
* Dynamic time formatting

It also supports future translations without touching UI logic.

---


