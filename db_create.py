from views import db
from models import Task
from datetime import date

# create the database and the db table
db.create_all()
# insert data
# db.session.add(Task(1, "Finish this tutorial", date(2015, 3, 13), 10,
#                     1))
# db.session.add(Task(2, "Finish Real Python", date(2015, 3, 13), 10, 1))
# commit the changes
db.session.commit()

# create a new database if the database doesn't already exist
