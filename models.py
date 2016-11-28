from datetime import datetime

from views import db


class Task(db.Model):
    __tablename__ = "tasks"

    task_id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    posted_date = db.Column(db.Date, default=datetime.utcnow())
    priority = db.Column(db.INTEGER, nullable=False)
    status = db.Column(db.INTEGER)
    user_id = db.Column(db.INTEGER, db.ForeignKey('users.id'))

    def __init__(self, task_id, name, due_date, posted_date, priority, status, user_id):
        self.task_id = task_id
        self.name = name
        self.due_date = due_date
        self.posted_date = posted_date
        self.priority = priority
        self.status = status
        self.user_id = user_id

    def __repr__(self):
        return '<name {0}>'.format(self.name)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)
    tasks = db.relationship('Task', backref='poster')
    role = db.Column(db.String(15), default='user')

    def __init__(self, user_id, name=None, email=None, password=None, role=None):
        self.id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return '<User {0}>'.format(self.name)
