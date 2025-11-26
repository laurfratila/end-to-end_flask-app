# 10_email_support.md

## **Chapter 10 — Email Support**

---

###  Overview

Chapter 10 introduces **email capabilities**, enabling the application to:

* Send password reset links
* Notify administrators of errors (from Chapter 7)
* Send user-related notifications (later chapters)

Flask-Mail is integrated for sending emails via SMTP servers.
The chapter also introduces **text and HTML templates for emails**, including safe external URLs.

---

##  1. Flask-Mail Setup

Installation:

```bash
pip install flask-mail
```

Configuration in `config.py`:

```python
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMINS = ['your-email@example.com']
```

### Notes

* These values come from environment variables
* TLS can be enabled using `MAIL_USE_TLS`
* `ADMINS` is used to receive error alerts and can be reused for other system notifications

---

##  2. Initializing Flask-Mail

In `app/__init__.py`:

```python
from flask_mail import Mail

mail = Mail()

mail.init_app(app)
```

---

##  3. Sending an Email (Helper Function)

A generic `send_email()` helper makes email sending reusable:

```python
from flask_mail import Message
from app import mail
from flask import current_app


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
```

### Notes

* Supports both plain-text and HTML versions
* Uses `mail.send()` to transmit over SMTP
* Can be later expanded for asynchronous mailing

---

##  4. Password Reset Email Support

Password reset email functionality requires:

1. **Token generation** (model level – implemented in Chapter 10)
2. **Email templates** (text and HTML)
3. **send_password_reset_email()** helper

### Generating Reset Tokens

Using **JWT** via PyJWT:

```python
import jwt
from time import time
from app import app


def get_reset_password_token(self, expires_in=600):
    return jwt.encode(
        {'reset_password': self.id, 'exp': time() + expires_in},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

@staticmethod
def verify_reset_password_token(token):
    try:
        user_id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
    except Exception:
        return None
    return db.session.get(User, user_id)
```

### Behavior

* Tokens expire after 10 minutes (default)
* Expiration is built into the JWT payload
* The token is tamper-proof because it is signed using the application's `SECRET_KEY`

---

##  5. Password Reset Email Function

```python
from flask import render_template

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        '[Microblog] Reset Your Password',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )
```

### Notes

* Renders templates with token URL
* Uses the first admin email as sender

---

##  6. Email Templates

### **Text Email (`reset_password.txt`)**

```txt
Dear {{ user.username }},

To reset your password, click the following link:
{{ url_for('reset_password', token=token, _external=True) }}

If you did not request a password reset, simply ignore this message.
```

### **HTML Email (`reset_password.html`)**

```html
<!doctype html>
<html>
  <body>
    <p>Dear {{ user.username }},</p>
    <p>
      To reset your password
      <a href="{{ url_for('reset_password', token=token, _external=True) }}">click here</a>.
    </p>
    <p>If you did not request a password reset, you may safely ignore this message.</p>
  </body>
</html>
```

### Notes

* `_external=True` ensures absolute URLs (required for email clients)
* Both text and HTML variants improve compatibility

---

##  7. Testing Email Delivery

### Using a Debug SMTP Server

```bash
pip install aiosmtpd
aiosmtpd -n -c aiosmtpd.handlers.Debugging -l localhost:8025
```

### Environment variables for debug mode

```bash
export MAIL_SERVER=localhost
export MAIL_PORT=8025
```

Output will appear in the terminal where the SMTP server runs.

This enables safe testing without sending real emails.

---

##  8. Email Support in the Full Project

Email functionality is used for:

* Error notifications (production)
* Password resets (user-facing)
* Automated alerts (later chapters)
* Potential future features: verification emails, 2FA, digest notifications

The modular helper-based design makes the system flexible and easy to extend.

---
