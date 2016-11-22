import cx_Oracle
from __config import DATABASE

# create a new database if the database doesn't already exist
with cx_Oracle.connect(DATABASE) as connection:
    c = connection.cursor()
    # create the table
    # insert dummy data into the table
    c.execute(
        """CREATE TABLE tasks(id NUMBER PRIMARY KEY,
 name VARCHAR2(40) NOT NULL,
 due_date VARCHAR2(150)NOT NULL,
  priority NUMBER NOT NULL,
  status NUMBER NOT NULL)""")
    c.execute("""INSERT INTO tasks (id,name, due_date, priority, status)
VALUES(1,'Finish this tutorial', '03/25/2015', 10, 1)""")
    c.execute(
        """INSERT INTO tasks (id,name, due_date, priority, status)
        VALUES(2,'Finish Real Python Course 2', '03/25/2015', 10, 1)""")
