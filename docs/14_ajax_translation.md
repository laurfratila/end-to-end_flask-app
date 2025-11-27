# 14_ajax_translation.md

## **Chapter 14 — AJAX-Based Live Translation**

---

###  Overview

Chapter 14 introduces **asynchronous translation** of post content using:

* Client-side AJAX requests
* A server-side `/translate` endpoint
* The Microsoft Translator API
* Dynamic UI updates without page reloads

This enables users to click a “Translate” link under a foreign-language post and instantly view the translated version inline.

---

##  1. Language Detection for Posts

When a post is submitted, its language can be detected automatically using `langdetect`:

```bash
pip install langdetect
```

In the Post model:

```python
from langdetect import detect, LangDetectException

class Post(db.Model):
    language = mapped_column(sa.String(5))
```

Detect on post creation:

```python
try:
    post.language = detect(post.body)
except LangDetectException:
    post.language = ''
```

### Purpose

* Avoid offering translation for content already in the user’s language
* Pass correct `source_language` to translation service

---

##  2. Microsoft Translator API Integration

Set the API key in the environment:

```bash
export MS_TRANSLATOR_KEY="your-key-here"
```

In `config.py`:

```python
MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
```

### Translation Helper (`app/translate.py`)

```python
import requests
from flask_babel import _
from flask import current_app


def translate(text, source_language, dest_language):
    key = current_app.config['MS_TRANSLATOR_KEY']
    if not key:
        return _('Error: translation service not configured.')

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': 'westus',  # region based on Azure setup
    }

    url = (
        'https://api.cognitive.microsofttranslator.com/translate'
        f'?api-version=3.0&from={source_language}&to={dest_language}'
    )

    response = requests.post(url, headers=headers, json=[{'Text': text}])

    if response.status_code != 200:
        return _('Error: translation service failed.')

    return response.json()[0]['translations'][0]['text']
```

### Notes

* Returns translated text or an error string
* JSON request/response format matches Microsoft’s API
* Abstracted to allow future replacement (e.g., Google Cloud Translation)

---

##  3. AJAX Translation Route

A minimal POST endpoint:

```python
from flask import request
from flask_login import login_required
from app.translate import translate

@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    data = request.get_json() or {}
    return {
        'text': translate(
            data.get('text', ''),
            data.get('source_language', ''),
            data.get('dest_language', '')
        )
    }
```

### Notes

* Expects JSON payload
* Returns JSON response
* No template rendering (pure AJAX service)

---

##  4. Adding the Translate Link in Templates

Inside the post component (`_post.html`):

```html
{% if post.language and post.language != g.locale %}
  <a href="#" class="translate-link" 
     data-post-id="{{ post.id }}"
     data-source-language="{{ post.language }}"
     data-dest-language="{{ g.locale }}"
     data-text="{{ post.body }}">
     {{ _('Translate') }}
  </a>
  <div id="translated-{{ post.id }}" class="mt-2 text-muted"></div>
{% endif %}
```

### Notes

* The link appears only if the post language differs from the user’s locale
* Post text and languages are embedded as `data-*` attributes
* Target element for translated text is preallocated

---

##  5. JavaScript for AJAX Request

Add this script in `base.html` (or a dedicated JS file):

```html
<script>
document.addEventListener('click', function(event) {
    if (!event.target.classList.contains('translate-link')) return;
    event.preventDefault();

    const link = event.target;
    const postId = link.dataset.postId;
    const text = link.dataset.text;
    const source = link.dataset.sourceLanguage;
    const dest = link.dataset.destLanguage;

    fetch('/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: text,
            source_language: source,
            dest_language: dest
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('translated-' + postId).innerText = data.text;
    });
});
</script>
```

### Behavior

* Captures clicks on “Translate” links
* Sends AJAX POST request
* Inserts translated text below the post
* No page refresh required

---

##  6. Integration with the Application

The AJAX translation system enhances the UX by:

* Avoiding full page reloads
* Allowing fast translation on demand
* Respecting user locale preferences (via Flask-Babel)
* Supporting any number of posts per page

This also prepares the application for:

* Future AJAX features (in later chapters)
* API-based translations
* Real-time UI updates

---

