# 22_background_jobs.md

## **Chapter 22 — Background Jobs (Redis Queue / RQ Integration)**

---

###  Overview

Chapter 22 integrates **background job processing** into the application using **Redis Queue (RQ)**.
This enables long-running tasks to execute outside the request/response cycle without blocking the user interface.

Combined with Chapter 21’s notification system, background tasks can update the user with real-time progress messages.

Use cases include:

* Bulk operations
* Reindexing for search
* Sending batch emails
* Heavy computations

---

##  1. Redis Configuration

Redis acts as the message broker for queued jobs.

### Install Redis (for local dev)

Linux/macOS:

```bash
sudo apt install redis-server
```

Or via Docker:

```bash
docker run -p 6379:6379 redis:7
```

### Install Python RQ library

```bash
pip install rq
```

---

##  2. Starting the RQ Worker

A worker process must run continuously:

```bash
rq worker microblog-tasks
```

This listens for background jobs under the queue name `microblog-tasks`.

---

##  3. Task Queue Setup

In `app/tasks.py`:

```python
from redis import Redis
from rq import Queue
from flask import current_app

redis = Redis.from_url(current_app.config['REDIS_URL'])
queue = Queue('microblog-tasks', connection=redis)
```

### Configuration in `config.py`:

```python
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
```

If Redis is running locally with default settings, `redis://` works automatically.

---

##  4. Example Background Task

A simple example that sends progress notifications:

```python
import time
from app import db
from app.models import User


def example_long_task(user_id):
    user = db.session.get(User, user_id)
    for i in range(10):
        user.add_notification('task_progress', {'step': i + 1, 'total': 10})
        db.session.commit()
        time.sleep(1)
    return "done"
```

### Behavior

* Simulates a long 10-step job
* Sends updates after each iteration
* Integrated with the notification polling system (Chapter 21)

---

##  5. Launching Tasks from Routes

Inside a Flask route:

```python
from app.tasks import queue
from app.tasks import example_long_task

@bp.route('/start-task')
@login_required
def start_task():
    job = queue.enqueue(example_long_task, current_user.id)
    return redirect(url_for('main.index'))
```

### Notes

* `queue.enqueue()` schedules the task immediately
* The route returns instantly
* The user is notified every second through notifications

---

##  6. Displaying Task Progress on the Client

Notifications from Chapter 21 deliver updates:

```html
<script>
// from Chapter 21
function checkNotifications() { ... }

// Example of handling progress
if (item.name === 'task_progress') {
  const step = item.data.step;
  const total = item.data.total;
  const pct = Math.round((step / total) * 100);
  document.getElementById('task-status').innerText = `Progress: ${pct}%`;
}
</script>
```

In your template:

```html
<div id="task-status" class="mt-3 text-muted"></div>
```

---

##  7. RQ Worker Deployment in Docker

If you use Docker:

### Updated `docker-compose.yml` (SQLite-friendly version)

```yaml
services:
  web:
    build: .
    environment:
      - SECRET_KEY=change-me
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  worker:
    build: .
    command: rq worker -u redis://redis:6379/0 microblog-tasks
    depends_on:
      - redis
```

### Notes

* Web, worker, and Redis are separate containers
* Both web and worker containers share the same image
* Worker executes tasks while web handles requests

SQLite compatibility:

* Works as long as tasks do not require parallel writes
* Background workers using SQLite are acceptable for student / hobby projects
* For production, PostgreSQL is normally preferred

---

##  8. Role of Background Jobs in the Full Application

Background jobs enable:

* Long-running or expensive operations
* Smooth, non-blocking user experience
* Real-time progress messaging
* Integration with API workflows
* Future batch-processing features

This chapter forms the backbone for asynchronous capabilities.

---


