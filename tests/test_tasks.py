import unittest

from project import app, db

from project.models import User, Task


class TasksTests(unittest.TestCase):
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
        new_user = User(user_id=user_id, name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    def create_admin_user(self):
        new_user = User(
            user_id='2',
            name='Superman',
            email='admin@realpython.com',
            password='all_powerful',
            role='admin'
        )
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        return self.app.post('/add', data=dict(
            task_id=1,
            name='Go to the bank',
            due_date='02/05/2014',
            priority='1',
            posted_date='02/04/2014',
            status='1'
        ), follow_redirects=True)

    def test_users_can_add_tasks(self):
        self.create_user(1, 'Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'New entry was successfully posted. Thanks.', response.data)

    def test_users_cannot_add_tasks_when_error(self):
        self.create_user(1, 'Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks', follow_redirects=True)
        response = self.app.post('/add', data=dict(
            task_id='1',
            name='Go to the bank',
            due_date='',
            priority='1',
            posted_date='02/05/2014',
            status='1'), follow_redirects=True)
        self.assertIn(b'This field is required', response.data)

    def test_users_can_complete_tasks(self):
        self.create_user(1, 'Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks', follow_redirects=True)
        self.create_task()
        response = self.app.get("/complete/1", follow_redirects=True)
        self.assertIn(b'The task was marked as complete.', response.data)

    def test_users_can_delete_tasks(self):
        self.create_user(1, 'Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks', follow_redirects=True)
        self.create_task()
        response = self.app.get("/delete/1", follow_redirects=True)
        self.assertIn(b'The task was deleted', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.create_user(1, 'Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user(2, 'Fletcher', 'fletcher@realpython.com',
                         'python101')
        self.login('Fletcher', 'python101')
        self.app.get('/tasks', follow_redirects=True)
        response = self.app.get("/complete/1", follow_redirects=True)
        self.assertNotIn(b'The task was marked as complete.', response.data)
        self.assertIn(b'You can only update tasks that belong to you.', response.data)

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.create_user(1, 'Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user(2, 'Fletcher', 'fletcher@realpython.com',
                         'python101')
        self.login('Fletcher', 'python101')
        self.app.get('/tasks', follow_redirects=True)
        response = self.app.get("/delete/1", follow_redirects=True)
        self.assertNotIn(b'The task was deleted.', response.data)
        self.assertIn(b'You can only delete tasks that belong to you.', response.data)

    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user(1, 'Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'all_powerful')
        self.app.get('tasks', follow_redirects=True)
        response = self.app.get("/complete/1", follow_redirects=True)
        self.assertNotIn(b'You can only update tasks that belong to you.', response.data)

    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        self.create_user(1, 'Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'all_powerful')
        self.app.get('/tasks', follow_redirects=True)
        response = self.app.get("/delete/1", follow_redirects=True)
        self.assertNotIn(b'You can only delete tasks that belong to you.', response.data)


if __name__ == '__main__':
    unittest.main()
