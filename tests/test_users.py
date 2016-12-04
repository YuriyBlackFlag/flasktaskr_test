import unittest

from project import app, db, bcrypt

from project.models import User


class UsersTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://py_test:123123@127.0.0.1:1521/test'
        self.app = app.test_client()
        db.create_all()

        # executed after each test

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password),
                             follow_redirects=True)

    def register(self, id, name, email, password, confirm):
        return self.app.post('/register',
                             data=dict(id=id,
                                       name=name,
                                       email=email,
                                       password=password,
                                       confirm=confirm),
                             follow_redirects=True
                             )

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def create_user(self, user_id, name, email, password):
        new_user = User(user_id=user_id, name=name, email=email, password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # each test should start with 'test'

    def test_form_is_present_on_login_page(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please login to access your task list',
                      response.data)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_users_can_login(self):
        self.register(1, 'Michael', 'michael@realpython.com', 'python',
                      'python')
        response = self.login('Michael', 'python')
        self.assertIn(b'Welcome!', response.data)

    def test_invalid_form_data(self):
        self.register(1, 'Michael', 'michael@realpython.com', 'python',
                      'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid username or password', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list.', response.data)

    def test_user_registration(self):
        self.app.get('/register', follow_redirects=True)
        response = self.register(1, 'Michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn(b'Thanks for registering. Please login.', response.data)

    def test_user_registration_error(self):
        self.app.get('/register', follow_redirects=True)

        self.register(1, 'Michael', 'michael@realpython.com', 'python',
                      'python')
        self.app.get('/register', follow_redirects=True)
        response = self.register(1, 'Michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn(b'That username and/or email already exist',
                      response.data)

    def test_logged_in_users_can_logout(self):
        self.register(1, 'Fletcher', 'fletcher@realpython.com',
                      'python101', 'python101')
        self.login('Fletcher', 'python101')
        response = self.logout()
        self.assertIn(b'Goodbye', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye', response.data)

    def test_default_user_role(self):
        db.session.add(
            User(1,
                 "Johnny",
                 "john@doe.com",
                 "johnny".encode('utf-8')
                 )
        )
        db.session.commit()
        users = db.session.query(User).all()
        print(users)
        for user in users:
            self.assertEquals(user.role, 'user')


if __name__ == '__main__':
    unittest.main()
