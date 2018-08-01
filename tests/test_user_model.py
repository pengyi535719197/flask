import unittest
from app.models import User, db, Role, Permission, AnonymousUser
from datetime import datetime


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='ct')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))

    def test_valid_email_change_token(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan@example.org')

    def test_invalid_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')

        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        token = u1.generate_email_change_token('david@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_duplicate_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')

        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    def test_timestamps(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue((datetime.utcnow() - u.member_since).total_seconds() < 3 )
        self.assertTrue((datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_gravatar(self):
        u = User(email='john@example.com', password='cat')
        with self.app.test_request_context('/'):

            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')

        with self.app.test_request_context('/', base_url='https://example.com'):
            gravatar_ssl = u.gravatar()
            self.assertTrue('http://www.gravatar.com/avatar/' +
                                                     'd4c74594d841139328695756648b6bd6' in gravatar)
            self.assertTrue('s=256' in gravatar_256)
            self.assertTrue('r=pg' in gravatar_pg)
            self.assertTrue('d=retro' in gravatar_retro)
            self.assertTrue('https://secure.gravatar.com/avatar/' +
                                                  'd4c74594d841139328695756648b6bd6' in gravatar_ssl)

    def test_to_json(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        with self.app.test_request_context('/'):
            json_user = u.to_json()
        expected_keys = ['url', 'username', 'member_since', 'last_seen',
                         'post_url', 'followed_posts_url', 'post_count']
        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/users/' + str(u.id), json_user['url'])
