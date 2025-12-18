#!/usr/bin/env python
from datetime import datetime, timezone, timedelta
import unittest
from app import create_app, db
from app.models import User, Post
from config import Config
from app.translate import translate
from app import mail
from app.email import send_email



class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL = None
    MAIL_SUPPRESS_SEND = True
    WTF_CSRF_ENABLED = False
    MS_TRANSLATOR_KEY = None
    MS_TRANSLATOR_REGION = None


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan', email='susan@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        following = db.session.scalars(u1.following.select()).all()
        followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following, [])
        self.assertEqual(followers, [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1_following = db.session.scalars(u1.following.select()).all()
        u2_followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].username, 'susan')
        self.assertEqual(u2_followers[0].username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.now(timezone.utc)
        p1 = Post(body="post from john", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the following posts of each user
        f1 = db.session.scalars(u1.following_posts()).all()
        f2 = db.session.scalars(u2.following_posts()).all()
        f3 = db.session.scalars(u3.following_posts()).all()
        f4 = db.session.scalars(u4.following_posts()).all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])



    def test_reset_password_token(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()

        token = u.get_reset_password_token()
        self.assertIsNotNone(token)

        # Valid token loads same user
        u2 = User.verify_reset_password_token(token)
        self.assertEqual(u2.id, u.id)

        # Invalid token returns None
        self.assertIsNone(User.verify_reset_password_token("invalid-token"))

    def test_reset_token_expired(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()

        token = u.get_reset_password_token(expires_in=-1)  # expires immediately
        u2 = User.verify_reset_password_token(token)
        self.assertIsNone(u2)

    def test_send_email(self):
        from app.email import send_email

        with mail.record_messages() as outbox:
            send_email(
               subject="Test Email",
               sender="test@example.com",
               recipients=["john@example.com"],
                text_body="Hello",
                html_body="<p>Hello</p>",
                sync=True  # force synchronous send
            )

            self.assertEqual(len(outbox), 1)
            msg = outbox[0]
            self.assertEqual(msg.subject, "Test Email")
            self.assertIn("john@example.com", msg.recipients)



    def test_translation_fallback(self):
        # Translator API disabled in TestConfig by design
        text = "Hello world"
        with self.app.test_request_context('/'):
            translated = translate(text, "en", "es")

        self.assertEqual(
            translated,
            'Error: the translation service is not configured.'
        )


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()



    def test_follow_route(self):
        u1 = User(username='john', email='john@example.com')
        u1.set_password('cat')
        u2 = User(username='susan', email='susan@example.com')
        u2.set_password('dog')

        db.session.add_all([u1, u2])
        db.session.commit()

        # log in john
        resp = self.client.post('/auth/login', data={
            'username': 'john',     # if your form uses 'username'
            'password': 'cat'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # follow susan – note we send a submit field so the form validates
        resp = self.client.post('/follow/susan', data={'submit': 'Follow'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # reload from DB to see fresh state
        john = db.session.get(User, u1.id)
        susan = db.session.get(User, u2.id)

        self.assertTrue(john.is_following(susan))
        self.assertEqual(john.following_count(), 1)
        self.assertEqual(susan.followers_count(), 1)


    def test_unfollow_route(self):
        u1 = User(username='john', email='john@example.com')
        u1.set_password('cat')
        u2 = User(username='susan', email='susan@example.com')
        u2.set_password('dog')

        db.session.add_all([u1, u2])
        db.session.commit()

        # john initially follows susan
        u1.follow(u2)
        db.session.commit()

        # log in john
        resp = self.client.post('/auth/login', data={
            'username': 'john',
            'password': 'cat'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # unfollow susan
        resp = self.client.post('/unfollow/susan', data={'submit': 'Unfollow'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        john = db.session.get(User, u1.id)
        susan = db.session.get(User, u2.id)

        self.assertFalse(john.is_following(susan))
        self.assertEqual(john.following_count(), 0)
        self.assertEqual(susan.followers_count(), 0)

    def test_search_indexing(self):
        if self.app.elasticsearch:
            u = User(username='john', email='john@example.com')
            db.session.add(u)
            db.session.commit()

            p = Post(body="flask microblog test", author=u)
            db.session.add(p)
            db.session.commit()

            results, total = Post.search("microblog")
            self.assertIn(p.id, [hit.id for hit in results])






if __name__ == '__main__':
    unittest.main(verbosity=2)
