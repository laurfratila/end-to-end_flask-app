# 21_user_notifications.md

## **Chapter 21 — User Notifications**

---

###  Overview

Chapter 21 adds a **notification system** that allows the application to deliver messages to users asynchronously.
Notifications are stored in the database and retrieved by the client via **AJAX polling**.

This feature supports:

* Real-time updates
* Background job progress messages
* API-driven alerting
* Future WebSocket integration

---

##  1. Notification Model

A new model is added to store notification events:

```python
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
```

### Notes

* `name` identifies the notification type
* `payload_json` stores structured data
* `timestamp` allows sorted retrieval

---

##  2. Adding Notification Relationship to User

```python
class User(UserMixin, db.Model):
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
```

Users can have many notifications, queryable via:

```python
current_user.notifications.order_by(Notification.timestamp.desc())
```

---

##  3. Helper Method to Add Notifications

```python
import json
from time import time

class User(UserMixin, db.Model):

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data),
                         user=self, timestamp=time())
        db.session.add(n)
        return n
```

### Behavior

* Removes previous notifications with the same name (avoid duplicates)
* Stores JSON payload of any structure
* Timestamp added for sorting

---

##  4. AJAX Polling Endpoint

The client polls the server for new notifications:

```python
@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notes = current_user.notifications.filter(
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())

    return [{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notes]
```

### Notes

* Accepts a timestamp to fetch notifications **since** the last check
* Returns a list of new notifications in ascending order

---

##  5. Client-Side JavaScript Polling

Placed in `base.html` or a dedicated script block:

```html
<script>
let lastTimestamp = 0;

function checkNotifications() {
  fetch(`/notifications?since=${lastTimestamp}`)
    .then(response => response.json())
    .then(data => {
      for (let item of data) {
        lastTimestamp = item.timestamp;

        if (item.name === 'task_progress') {
          // Display or process progress update
          console.log('Task update:', item.data);
        }
      }
    });
}

setInterval(checkNotifications, 10000); // poll every 10 seconds
</script>
```

### Behavior

* Stores last seen timestamp
* Repeatedly polls for new notifications
* Handles received items dynamically

---

##  6. How Notifications Fit Into the App

Notifications enable:

* Live progress messages from background jobs (Chapter 22)
* Search index progress updates
* Alerts for asynchronous operations
* User messages from API endpoints

This chapter provides the foundation for any real-time or semi-real-time communication in the application.

---

