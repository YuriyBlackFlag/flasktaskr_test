# blog.py controller
# imports
from flask import Flask, render_template, request, session, \
    flash, redirect, url_for, g
from functools import wraps
from forms import AddTaskForm
import cx_Oracle

app = Flask(__name__)
# pulls in app configuration by looking for UPPERCASE variables
app.config.from_object('__config')


# function used for connecting to the database

def connect_db():
    return cx_Oracle.connect(app.config['DATABASE'])


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
        return redirect(url_for('login'))

    return wrap


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form['username'] != app.config["USERNAME"] or \
                        request.form["password"] != app.config["PASSWORD"]:
            error = "Invalid Credentials. Please try again"
        else:
            session["logged_in"] = True
            return redirect(url_for("tasks"))
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("Goodbye")
    return redirect(url_for("login"))


@app.route("/tasks")
@login_required
def tasks():
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute("SELECT name, due_date, priority, id FROM TASKS WHERE STATUS = 1 ORDER BY id DESC")
    open_tasks = [
        dict(name=row[0], due_date=row[1], priority=row[2],
             id=row[3]) for row in cur.fetchall()
        ]
    cur.execute("SELECT name, due_date, priority, id FROM TASKS WHERE STATUS = 0")
    closed_tasks = [
        dict(name=row[0], due_date=row[1], priority=row[2],
             id=row[3]) for row in cur.fetchall()
        ]
    cur.close()
    g.db.close()
    return render_template("tasks.html", form=AddTaskForm(request.form),
                           open_tasks=open_tasks,
                           closed_tasks=closed_tasks)


@app.route("/add", methods=["POST"])
@login_required
def new_task():
    g.db = connect_db()
    cur = g.db.cursor()
    name = request.form['name']
    date = request.form['due_date']
    priority = request.form['priority']
    if not name or not date or not priority:
        flash("All fields are required. Please try again.")
        return redirect(url_for('tasks'))
    else:
        cur.execute("select max(id) from tasks")
        max_id = cur.fetchone()
        cur.execute('insert into tasks (id, name, due_date, priority, status) \
        values(:1, :2, :3, :4,  1)',
                    [max_id[0] + 1, request.form['name'], request.form['due_date'], request.form['priority']])
        g.db.commit()
        cur.close()
        g.db.close()
        flash('New entry was successfully posted. Thanks.')
        return redirect(url_for('tasks'))


@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute('update tasks set status = 0 where id=' + str(task_id))
    g.db.commit()
    cur.close()
    g.db.close()
    flash('The task was marked as complete.')
    return redirect(url_for('tasks'))


# Delete Tasks
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute('delete from tasks where id=' + str(task_id))
    g.db.commit()
    cur.close()
    g.db.close()
    flash('The task was deleted.')
    return redirect(url_for('tasks'))


if __name__ == '__main__':
    app.run(debug=True)
