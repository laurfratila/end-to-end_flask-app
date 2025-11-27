# 12_dates_and_times.md

## **Chapter 12 — Dates and Times (UTC Storage & Moment.js)**

---

###  Overview

Chapter 12 standardizes how timestamps are handled across the application.
All server-side timestamps are stored in **UTC**, while the client browser displays them in the user’s **local timezone** using **Moment.js** and the `Flask-Moment` extension.

The chapter introduces:

* UTC timestamp usage in the database
* `last_seen` user activity tracking
* Client-side rendering with Moment.js
* Time formatting in templates

This adds both accuracy and usability across all user-facing timelines.

---

##  1. Storing Timestamps in UTC

Python’s `datetime` with timezone awareness ensures all stored timestamps are consistent.

Example (in the Post model):

```python
from datetime import datetime, timezone

timestamp: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(timezone.utc), index=True
)
```

### Why UTC?

* Avoids timezone drift across regions
* Ensures consistent cross-user timestamps
* Prevents issues with DST changes
* Simplifies sorting and database comparisons

UTC becomes the internal standard for all timestamp fields in the project.

---

##  2. Tracking "Last Seen" Time

User activity is tracked using `last_seen` in the User model:

```python
from datetime import datetime, timezone

class User(UserMixin, db.Model):
    last_seen = mapped_column(default=lambda: datetime.now(timezone.utc))
```

### Updating on Every Request

In `app/routes.py` or later within the `main` blueprint:

```python
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
```

### Notes

* Executed before every view function
* Ensures profiles and activity feeds display accurate timestamps

---

##  3. Integrating Flask-Moment

Installation:

```bash
pip install flask-moment
```

Initialization (`app/__init__.py`):

```python
from flask_moment import Moment
moment = Moment()
moment.init_app(app)
```

Add the Moment.js script via helper in `base.html`:

```html
{{ moment.include_moment() }}
```

---

##  4. Rendering Timestamps in Templates

Flask-Moment lets you send a Python `datetime` to the client and format it using JavaScript.

### **Example for Post Timestamp**

In `_post.html`:

```html
<p class="text-muted">
  {{ moment(post.timestamp).fromNow() }}
</p>
```

### **Example for Last Seen**

In `user.html`:

```html
{% if user.last_seen %}
  <p>Last seen: {{ moment(user.last_seen).format('LLL') }}</p>
{% endif %}
```

### Moment.js Format Options

* `.fromNow()` → “5 minutes ago”
* `.format('LLL')` → localized date + time
* `.calendar()` → contextual human-readable format

---

##  5. Benefits of Client-Side Rendering

Rendering timestamps in the browser allows:

* Automatic conversion to user’s timezone
* Localized formatting based on browser locale
* Better readability (“3 hours ago”) instead of fixed UTC strings

This improves global user experience significantly.

---

##  6. Integration in the Full Application

Timestamps become essential for:

* Post feeds
* Activity tracking
* Profile pages
* Notifications (Chapter 21)
* Background jobs (Chapter 22)
* Search results and sorting (Chapter 16)
* API responses (Chapter 23)

Moment.js provides the flexibility needed to handle these cases cleanly.

---

