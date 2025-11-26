# 08_followers.md

## **Chapter 8 — Followers (Many‑to‑Many Relationships)**

---

###  Overview

Chapter 8 introduces a key social feature: **users can follow other users**.
This requires implementing a **self‑referential many‑to‑many relationship** using an association table.

This chapter adds:

* A `followers` association table
* User model relationships (`following` and `followers`)
* Helper methods for follow/unfollow behavior
* Methods to query followed posts for timeline feeds

The follower system is the core of the personalized “home timeline” functionality.

---

##  1. Followers Association Table

Self‑referential many‑to‑many relationships require an auxiliary table.

```python
import sqlalchemy as sa
from app import db

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)
```

### Notes

* Both columns act as a composite primary key
* No model class is used; the table is purely relational

---

##  2. Adding Relationship Attributes to the User Model

```python
class User(UserMixin, db.Model):
    # existing fields…

    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers'
    )

    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following'
    )
```

### Important Details

* `primaryjoin` and `secondaryjoin` define both ends of the relationship
* `WriteOnlyMapped` allows `.add()` and `.remove()` operations
* `back_populates` ties both sides together

---

##  3. Follow/Unfollow Methods

These helper methods encapsulate relationship operations:

```python
def follow(self, user):
    if not self.is_following(user):
        self.following.add(user)

def unfollow(self, user):
    if self.is_following(user):
        self.following.remove(user)

def is_following(self, user):
    query = self.following.select().where(User.id == user.id)
    return db.session.scalar(query) is not None


def followers_count(self):
    query = sa.select(sa.func.count()).select_from(self.followers.select().subquery())
    return db.session.scalar(query)

def following_count(self):
    query = sa.select(sa.func.count()).select_from(self.following.select().subquery())
    return db.session.scalar(query)
```

### Why helper methods?

* Encapsulate logic cleanly
* Prevent duplicate relationships
* Allow future changes without modifying view functions

---

##  4. Querying Posts from Followed Users

A combined feed of user + followed posts is needed for the index timeline.

### Complex SQLAlchemy query:

```python
def following_posts(self):
    Author = so.aliased(User)
    Follower = so.aliased(User)

    return (
        sa.select(Post)
        .join(Post.author.of_type(Author))
        .join(Author.followers.of_type(Follower), isouter=True)
        .where(sa.or_(
            Follower.id == self.id,
            Author.id == self.id
        ))
        .group_by(Post)
        .order_by(Post.timestamp.desc())
    )
```

### Behavior

* Returns posts by followed users and the user themself
* Uses aliased tables to differentiate follower/author roles
* Ordered by timestamp for efficient feed rendering

This query becomes the foundation of the home timeline in later chapters.

---

##  5. Database Migration

Generate migration:

```bash
flask db migrate -m "followers table"
```

Apply migration:

```bash
flask db upgrade
```

This adds the new association table to the database.

---

##  6. Integration with the Frontend (Preview)

In later chapters, the follower system connects to:

* Follow/Unfollow buttons and forms
* The user profile page
* Personalized index timeline
* API follower endpoints

Though the UI is implemented later, the backend logic is fully prepared here.

---

##  7. Role of the Followers System in the Full Project

The follower system enables:

* Personalized timelines
* Social graph operations
* Relationship-based API responses
* User recommendations
* Notification triggers
* Background job activity for bulk follower updates

It also introduces complex relationship queries that are used again for:

* Full-text search ranking
* API filtering
* Post aggregation features

---


