import cx_Oracle

from project.views import db

# create a new database if the database doesn't already exist
with cx_Oracle.connect("pyth/123123@127.0.0.1/test") as connection:
    # get a cursor object used to execute SQL commands
    c = connection.cursor()
    # create the table
    # insert dummy data into the table
    # temporarily change the name of tasks table
    # c.execute("""ALTER TABLE tasks RENAME TO old_tasks""")
    # recreate a new tasks table with updated schema
    # db.create_all()
    # # retrieve data from old_tasks table
    # c.execute("""SELECT task_id, name, due_date, priority, status FROM old_tasks ORDER BY task_id ASC""")
    #
    # # save all rows as a list of tuples; set posted_date to now and user_id to 1
    # data = [(row[0], row[1], row[2], row[3], row[4],
    #          datetime.now(), 1) for row in c.fetchall()]
    # # insert data to tasks table
    # c.executemany(
    #     """INSERT INTO tasks (task_id, name, due_date, priority,status,posted_date, user_id)
    #     VALUES (:1, :2, :3, :4, :5, :6, :7)""", data)
    # # delete old_tasks table
    # c.execute("DROP TABLE old_tasks")

    c.execute("""ALTER TABLE users RENAME TO old_users""")
    # recreate a new tasks table with updated schema
    db.create_all()
    # retrieve data from old_tasks table
    c.execute("""SELECT id, name, email, password FROM old_users ORDER BY id ASC""")

    # save all rows as a list of tuples; set posted_date to now and user_id to 1
    data = [(row[0], row[1], row[2], row[3], 'user') for row in c.fetchall()]
    # insert data to tasks table
    c.executemany(
        """INSERT INTO users (id, name, email, password, role)
        VALUES (:1, :2, :3, :4, :5)""", data)
    # delete old_tasks table
    c.execute("DROP TABLE old_users")
