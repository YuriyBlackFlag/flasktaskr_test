from datetime import date
from project import db
from project.models import Task, User

# create the database and the db table
db.create_all()
# insert data
db.session.add(
    User(2, "admin", "ad@min.com", "admin", "admin")
)
db.session.add(
    Task(3, "Finish this tutorial", date(2015, 10, 10), date(2015, 10, 10), 10, 1, 2)
)
db.session.add(
    Task(4, "Finish Real Python", date(2015, 10, 10), date(2015, 10, 10), 10, 1, 2)
)
# commit the changes
db.session.commit()

# create a new database if the database doesn't already exist
