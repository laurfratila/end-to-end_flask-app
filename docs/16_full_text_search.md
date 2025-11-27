# 16_full_text_search.md

## **Chapter 16 — Full‑Text Search (Elasticsearch Integration)**

---

###  Overview

Chapter 16 introduces **full‑text search** into the application, enabling users to search across posts efficiently.
The implementation uses **Elasticsearch**, but it is abstracted behind a helper layer so the backend search engine can be swapped without modifying core application code.

This chapter adds:

* A search index
* Search helper functions
* Integration with the Post model
* Search form and UI
* Search route

---

##  1. Elasticsearch Setup

Installation (for local development):

```bash
pip install elasticsearch==8.9.0   # version aligned with tutorial
```

Environment configuration:

```bash
export ELASTICSEARCH_URL="http://localhost:9200"
```

### In `config.py`:

```python
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
```

### Initializing Elasticsearch in `app/__init__.py`:

```python
from elasticsearch import Elasticsearch

app.elasticsearch = None
if app.config['ELASTICSEARCH_URL']:
    app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH_URL'])
```

This attaches an Elasticsearch client to the Flask application.

---

##  2. Search Index Helper Functions

A small abstraction layer wraps Elasticsearch operations.

### **Adding/Updating a document**

```python
def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)
```

### **Removing a document**

```python
def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id, ignore=[404])
```

### **Performing a search**

```python
def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0

    search = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page
    )

    ids = [hit['_id'] for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
```

---

##  3. Making Models Searchable

The Post model declares which fields should be indexed:

```python
class Post(db.Model):
    __searchable__ = ['body']  # fields indexed by Elasticsearch
```

Events are added to automatically update the index:

```python
from sqlalchemy import event
from app.search import add_to_index, remove_from_index

@event.listens_for(Post, 'after_insert')
def index_post(mapper, connection, target):
    add_to_index('posts', target)

@event.listens_for(Post, 'after_update')
def reindex_post(mapper, connection, target):
    add_to_index('posts', target)

@event.listens_for(Post, 'after_delete')
def unindex_post(mapper, connection, target):
    remove_from_index('posts', target)
```

### Notes

* Index updates occur automatically
* Supports real‑time search results
* Keeps Elasticsearch synchronized with the database

---

##  4. Search Form

A lightweight search form is added to the navigation bar.

### `SearchForm` (WTForms)

```python
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_babel import _l

class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])
    submit = SubmitField(_l('Search'))
```

### Adding the form to every request

In `app/main/routes.py`:

```python
from flask import g
from app.main.forms import SearchForm

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()
```

Now templates can refer to `g.search_form` globally.

---

##  5. Search Template Snippet

In `base.html` navbar:

```html
<form class="d-flex" method="get" action="{{ url_for('main.search') }}">
  {{ g.search_form.q(class_='form-control me-2', placeholder=_('Search')) }}
</form>
```

This provides a single‑field search input.

---

##  6. Search Route

```python
@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))

    page = request.args.get('page', 1, type=int)
    query = g.search_form.q.data

    ids, total = query_index('posts', query, page, current_app.config['POSTS_PER_PAGE'])

    posts = []
    if ids:
        posts = db.session.scalars(
            sa.select(Post).where(Post.id.in_(ids))
        ).all()

    next_url = url_for('main.search', q=query, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None

    prev_url = url_for('main.search', q=query, page=page - 1) \
        if page > 1 else None

    return render_template(
        'main/search.html',
        title=_('Search Results'),
        posts=posts,
        next_url=next_url,
        prev_url=prev_url
    )
```

### Notes

* ID list preserves Elasticsearch ranking order
* Pagination supported via search results
* Falls back to explore view if form is invalid

---

##  7. Search Results Template

In `app/templates/main/search.html`:

```html
{% extends 'base.html' %}

{% block content %}
  <h1>{{ _('Search Results') }}</h1>
  {% for post in posts %}
    {% include 'main/_post.html' %}
  {% endfor %}

  <div class="d-flex justify-content-between">
    {% if prev_url %}<a class="btn btn-outline-primary" href="{{ prev_url }}">{{ _('Newer') }}</a>{% endif %}
    {% if next_url %}<a class="btn btn-outline-primary" href="{{ next_url }}">{{ _('Older') }}</a>{% endif %}
  </div>
{% endblock %}
```

---

##  8. Role of Search in the Full Application

Full‑text search enhances:

* Discoverability of content
* Explore functionality
* API search endpoints
* Post ranking workflows
* Background reindexing tasks (Chapter 22)

The helper‑based implementation keeps the system flexible, engine‑agnostic, and modular.

---


