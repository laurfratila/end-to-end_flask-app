# 02_templates.md

## **Chapter 2 — Templates**

---

###  Overview

In Chapter 2, the project evolves from returning plain strings to rendering rich HTML pages using **Flask templates** powered by **Jinja2**, the templating engine integrated into Flask.

Templates allow you to:

* Separate Python logic from presentation (HTML)
* Insert dynamic data into HTML pages
* Use control structures (conditions, loops)
* Use template inheritance to avoid repetition
* Maintain a clean, scalable frontend architecture

This chapter introduces the core building blocks of all future UI functionality.

---

###  1. Template Folder Structure

Flask looks for templates inside the `app/templates/` directory:

```
app/
│
├── templates/
│   ├── base.html
│   └── index.html
```

As the project grows, this folder will contain dozens of pages, partials, popups, and component files.

---

###  2. Introducing `render_template()`

Your route now returns a rendered HTML file instead of a plain string:

```python
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = { 'username': 'Miguel' }
    return render_template('index.html', title='Home', user=user)
```

### ** What `render_template()` does:**

* Loads a HTML file from the `templates` directory
* Passes variables to it
* Renders final HTML sent to the user's browser

This is how dynamic pages (e.g., user feeds, profile pages, notifications) become possible.

---

###  3. Creating Your First Template (`index.html`)

```html
<!doctype html>
<html>
  <head>
    {% if title %}
      <title>{{ title }} - Microblog</title>
    {% else %}
      <title>Welcome to Microblog</title>
    {% endif %}
  </head>
  <body>
    <h1>Hello, {{ user.username }}!</h1>
  </body>
</html>
```

### **Key Jinja2 Concepts Introduced**

| Feature                   | Example               | Purpose                |
| ------------------------- | --------------------- | ---------------------- |
| **Variable substitution** | `{{ user.username }}` | Insert dynamic content |
| **Conditionals**          | `{% if title %}`      | Render based on logic  |
| **Control blocks**        | `{% ... %}`           | Structure logic        |

Jinja2's syntax makes templates expressive and clean.

---

###  4. Adding Lists and Loops (Posts)

A common requirement is displaying a list of items.
Example mock list:

```python
posts = [
    {'author': {'username': 'John'}, 'body': 'Beautiful day in Portland!'},
    {'author': {'username': 'Susan'}, 'body': 'The Avengers movie was so cool!'}
]
```

Your template can loop through this list:

```html
{% for post in posts %}
  <div>
    <p>{{ post.author.username }} says: <b>{{ post.body }}</b></p>
  </div>
{% endfor %}
```

### ** Why loops matter**

* You will use loops for:

  * Rendering posts
  * Displaying followers
  * Search results
  * Notifications
  * API responses
  * Sidebar widgets

---

###  5. Template Inheritance (`base.html`)

A modern web application needs a **consistent layout**.
Instead of repeating navigation bars, headers, scripts, footers, etc., Flask templates support **inheritance**.

You define a base template:

```html
<!-- app/templates/base.html -->
<!doctype html>
<html>
  <head>
    <title>{% block title %}Microblog{% endblock %}</title>
  </head>
  <body>
    <div>Microblog Navigation Bar</div>

    <hr>

    {% block content %}{% endblock %}
  </body>
</html>
```

Then extend it in other templates:

```html
{% extends "base.html" %}

{% block content %}
  <h1>Hello, {{ user.username }}!</h1>
  {% for post in posts %}
    <p>{{ post.author.username }}: {{ post.body }}</p>
  {% endfor %}
{% endblock %}
```

### ** Benefits of Template Inheritance**

* Consistency
* Reduced duplication
* Easier maintenance
* Faster UI iteration
* Cleaner architecture

Later chapters rely heavily on this for:
Navigation menus, Flash messages, Pagination controls, User popups, and Search UI.

---

###  6. Jinja2 Syntax Summary

#### **Variables**

```
{{ variable }}
```

#### **Control structures**

```
{% if ... %}
{% for ... %}
{% block ... %}
```

#### **Comments**

```
{# This is a comment #}
```

#### **Filters** (used later)

```
{{ text|capitalize }}
```

These tools power dynamic HTML generation across the entire project.

---

###  7. Why Templates Matter

Templates turn your backend into a real user-facing application.

Without templates:

* No UI
* No posts
* No forms
* No login page
* No user profiles
* No error pages
* No AJAX responses

Everything beyond Chapter 1 depends on Jinja2.

This chapter establishes the **presentation layer** of the application.

---

###  Summary


* Use `render_template()`
* Build dynamic pages using HTML + Jinja2
* Render python variables inside templates
* Loop through collections
* Use template inheritance
* Structure your HTML cleanly and professionally

These concepts lay the groundwork for Chapter 3 (Web Forms) and all user-facing functionality.

---


