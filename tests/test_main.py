import unittest

from project import app, db, bcrypt

from project.models import User


class MainTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://py_test:123123@127.0.0.1:1521/test'
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

        # executed after each test

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password),
                             follow_redirects=True)

    def test_404_error(self):
        response = self.app.get("/this-route-does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Sorry. There\'s nothing here', response.data)

    # def test_500_error(self):
    #     bad_user = User(
    #         1,
    #         name='Jeremy',
    #         email='jeremy@realpython.com',
    #         password='django'.encode('utf-8')
    #     )
    #     db.session.add(bad_user)
    #     db.session.commit()
    #     response = self.login('Jeremy', 'django')
    #     self.assertEquals(response.statuscode, 500)
    #     self.assertNotIn(b'ValueError: Invalid salt', response.data)
    #     self.assertIn(b'Something went terribly wrong.', response.data)


if __name__ == '__main__':
    unittest.main()
