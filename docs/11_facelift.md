# 11_facelift.md

## **Chapter 11 — Facelift (UI Modernization with Bootstrap)**

---

###  Overview

Chapter 11 gives the project a complete visual upgrade by integrating **Bootstrap**, restructuring templates, and applying a modern, responsive UI.

This chapter focuses on:

* Bootstrap integration
* A unified base layout (`base.html`)
* Improved navigation bar
* Flash message styling
* Cleaner forms and container layouts
* Template organization and partials

These changes prepare the application for all upcoming UI-heavy features: pagination, forms, profile pages, search, and AJAX interactions.

---

##  1. Adding Bootstrap to the Project

Bootstrap is included via CDN inside `base.html`:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
```

This provides:

* Responsive layout system
* Styled forms & buttons
* Navigation components
* Utility classes

---

##  2. Revamped Base Template

`base.html` becomes the central UI backbone:

```html
<!doctype html>
<html lang="en">
  <head>
    <title>{{ title }} - Microblog</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css">
  </head>

  <body>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark">
      <div class="container-fluid">
        <a class="navbar-brand" href="{{ url_for('index') }}">Microblog</a>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Home</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('explore') }}">Explore</a></li>
          </ul>
          <ul class="navbar-nav ms-auto">
            {% if current_user.is_authenticated %}
              <li class="nav-item"><a class="nav-link" href="{{ url_for('user', username=current_user.username) }}">Profile</a></li>
              <li class="nav-item"><a class="nav-link" href="{{ url_for('logout') }}">Logout</a></li>
            {% else %}
              <li class="nav-item"><a class="nav-link" href="{{ url_for('login') }}">Login</a></li>
            {% endif %}
          </ul>
        </div>
      </div>
    </nav>

    <div class="container mt-4">
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          {% for message in messages %}
            <div class="alert alert-info alert-dismissible fade show" role="alert">
              {{ message }}
              <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
          {% endfor %}
        {% endif %}
      {% endwith %}

      {% block content %}{% endblock %}
    </div>
  </body>
</html>
```

### Improvements

* Responsive navigation bar
* Bootstrap alert styling for flash messages
* Container layout for consistent spacing
* Cleaner structure for all pages to inherit

---

##  3. Styling Forms with Bootstrap

Example of improved login form:

```html
<form action="" method="post">
  {{ form.hidden_tag() }}

  <div class="mb-3">
    {{ form.username.label(class="form-label") }}
    {{ form.username(class="form-control", size=32) }}
  </div>

  <div class="mb-3">
    {{ form.password.label(class="form-label") }}
    {{ form.password(class="form-control", size=32) }}
  </div>

  <div class="form-check mb-3">
    {{ form.remember_me(class="form-check-input") }}
    {{ form.remember_me.label(class="form-check-label") }}
  </div>

  {{ form.submit(class="btn btn-primary") }}
</form>
```

### Notes

* Fields adopt `.form-control`, `.form-label`, `.form-check-*` classes
* Buttons use `.btn` classes
* Layout becomes visually consistent and fully responsive

---

##  4. Post Partial Template (`_post.html`)

Reusable component for rendering posts:

```html
<div class="card mb-3">
  <div class="card-body">
    <h6>
      <img src="{{ post.author.avatar(40) }}" class="rounded me-2">
      <a href="{{ url_for('user', username=post.author.username) }}">{{ post.author.username }}</a>
    </h6>
    <p class="mt-2">{{ post.body }}</p>
  </div>
</div>
```

### Benefits

* Cleaner main templates
* Consistent styling of posts
* Supports later features: timestamps, translation, AJAX updates

---

##  5. Updating Index and Profile Pages

Pages now render posts using the new component:

```html
{% for post in posts %}
  {% include '_post.html' %}
{% endfor %}
```

Pagination links also receive Bootstrap styling:

```html
<div class="d-flex justify-content-between">
  {% if prev_url %}<a class="btn btn-outline-primary" href="{{ prev_url }}">Newer</a>{% endif %}
  {% if next_url %}<a class="btn btn-outline-primary" href="{{ next_url }}">Older</a>{% endif %}
</div>
```

---

##  6. Layout Improvements Across the Entire Application

The facelift impacts all templates:

* Navigation becomes consistent
* Forms become visually appealing and clean
* Posts gain structure and spacing
* Flash messages integrate with Bootstrap alerts
* Pages inherit a unified layout

This prepares the UI for upcoming chapters involving interactive elements and dynamic content.

---

