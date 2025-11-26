# 09_pagination.md

## **Chapter 9 — Pagination**

---

###  Overview

Chapter 9 introduces **pagination** to efficiently handle lists of posts, preventing pages from becoming overloaded with content. This applies to:

* The main timeline (followed users)
* The explore page
* User profile pages
* API responses (later chapters)

Pagination ensures scalable performance and a clean user experience.

---

##  1. Pagination with Flask-SQLAlchemy

Flask-SQLAlchemy provides a convenient helper:

```python
posts = db.paginate(query, page=page, per_page=20, error_out=False)
```

### Parameters

* **`page`** — current page number
* **`per_page`** — number of items to show per page
* **`error_out=False`** — avoid automatic 404 for out-of-range pages

The returned object is a `Pagination` instance.

---

##  2. Configuration for Posts per Page

In `config.py`:

```python
class Config:
    POSTS_PER_PAGE = 25
```

This value is reused throughout the application.

---

##  3. Updating the Index Route

```python
@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = current_user.following_posts()

    posts = db.paginate(
        query,
        page=page,
        per_page=app.config['POSTS_PER_PAGE'],
        error_out=False
    )

    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    return render_template(
        'index.html',
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )
```

### Notes

* Reads `?page=N` from the query string
* Generates navigation URLs only when needed
* Uses `posts.items` to render the current page's subset

---

##  4. Pagination Template Markup

In `index.html` (or any post list template):

```html
{% for post in posts %}
  {% include '_post.html' %}
{% endfor %}

{% if prev_url %}
  <a href="{{ prev_url }}">Newer posts</a>
{% endif %}

{% if next_url %}
  <a href="{{ next_url }}">Older posts</a>
{% endif %}
```

This structure is reused for profile pages and the explore page.

---

##  5. Pagination in Profile Pages

```python
@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)

    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None

    return render_template(
        'user.html', user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )
```

### Notes

* Same pattern as index
* Adds `username` parameter to URLs
* Ensures post ordering by timestamp

---

##  6. Adding an Explore Page

A public feed showing all posts:

```python
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())

    posts = db.paginate(query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', posts=posts.items, next_url=next_url, prev_url=prev_url)
```

### Behavior

* Reuses the `index.html` template
* Shows global content instead of personalized feed

---

##  7. Pagination Object Properties

The `Pagination` object provides:

| Attribute   | Meaning                        |
| ----------- | ------------------------------ |
| `.items`    | List of items for current page |
| `.has_next` | If a next page exists          |
| `.has_prev` | If a previous page exists      |
| `.next_num` | Number of next page            |
| `.prev_num` | Number of previous page        |
| `.pages`    | Total number of pages          |
| `.total`    | Total items across all pages   |

These attributes support custom pagination UIs later in the project.

---

##  8. Integration Across the Application

Pagination becomes a structural element for:

* User timelines
* Explore page
* Profile post lists
* Search results (Chapter 16)
* Messages and notifications (Chapter 21)
* API endpoints (Chapter 23)

It ensures efficient user experience at scale.

---


