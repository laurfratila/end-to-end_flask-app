# 06_profile_page_and_avatars.md

## **Chapter 6 — Profile Page & Avatars**

---

###  Overview

Chapter 6 adds user profile pages, improves the User model with additional attributes, and integrates **Gravatar** avatars. This expands the authentication system into a fuller user identity feature, enabling:

* Public profile pages
* Displaying avatars
* Showing user metadata
* Preparing for profile editing (next chapter)
* Establishing patterns for dynamic, parameterized routes

This chapter also introduces **dynamic URLs** in Flask and basic user-related template rendering.

---

###  1. Expanding the User Model

A `about_me` field and a `last_seen` timestamp are added later, but for this chapter, the major addition is **Gravatar support**, implemented with a helper method.

```python
import hashlib
from flask import url_for

class User(UserMixin, db.Model):
    # existing fields...

    def avatar(self, size):
        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"
```

### Notes

* Gravatar uses MD5 hashes of email addresses
* `identicon` ensures a unique default image
* Size parameter allows consistent scaling in templates

This method becomes widely used in templates throughout the application.

---

###  2. User Profile Route

A **dynamic route** is used to retrieve a profile by username:

```python
@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]

    return render_template('user.html', user=user, posts=posts)
```

### Key Points

* `<username>` is a dynamic URL component
* `first_or_404()` returns 404 automatically if user doesn't exist
* Fake posts prepare the structure for real posts in later chapters

Dynamic routes are essential for:

* Profile access
* Post-specific views
* API endpoints
* Token URLs (password reset)

---

###  3. User Profile Template (`user.html`)

```html
{% extends "base.html" %}

{% block content %}
  <table>
    <tr>
      <td><img src="{{ user.avatar(128) }}"></td>
      <td>
        <h1>{{ user.username }}</h1>
        {% if user.about_me %}<p>{{ user.about_me }}</p>{% endif %}
        {% if user.last_seen %}<p>Last seen: {{ user.last_seen }}</p>{% endif %}
      </td>
    </tr>
  </table>

  <hr>

  {% for post in posts %}
    <p>{{ post.author.username }}: {{ post.body }}</p>
  {% endfor %}

{% endblock %}
```

### Template Behavior

* Displays avatar from `user.avatar()`
* Shows user metadata
* Lists content authored by the user

This establishes the standard layout used later for:

* Pagination
* Follow/unfollow forms
* Post timestamps (moment.js)
* AJAX-based translations

---

###  4. Displaying Avatars Across the Application

Common avatar usage pattern:

```html
<img src="{{ user.avatar(64) }}" alt="avatar">
```

Sizes vary depending on placement:

* Navbar: small (32px)
* Profile page: larger (128px)
* Post feed: medium (48–64px)

This provides a unified visual identity across components.

---

###  5. Navigation Link to Profile

`base.html` is updated to include a profile link for logged-in users:

```html
<a href="{{ url_for('user', username=current_user.username) }}">Profile</a>
```

This is the foundation for global navigation patterns.

---

###  6. Restricting Access

As with previous chapters, profile pages are protected with:

```python
@login_required
```

This ensures profile pages are only accessible to authenticated users.

Later chapters extend this with:

* Follow/unfollow controls
* Editing restrictions
* API permissions
* Role-based logic

---

###  7. How Profile Pages Fit Into the Larger System

Profile pages support:

* User identity and personalization
* Follower relationships (added in Chapter 8)
* Viewing a user's own posts
* Public presence accessible via dynamic routes
* Editing personal information (Chapter 7)
* Avatar display logic for the entire UI

They also establish route patterns reused extensively for:

* Post detail pages
* Notification feeds
* Search results
* API user endpoints

---

