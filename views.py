# blog.py controller
# imports
from datetime import datetime

from flask import Flask, render_template, request, session, \
    flash, redirect, url_for
from functools import wraps

from sqlalchemy.exc import IntegrityError

from forms import AddTaskForm, LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# pulls in app configuration by looking for UPPERCASE variables
app.config.from_object('__config')

db = SQLAlchemy(app)

from models import Task, User


# function used for connecting to the database
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
        return redirect(url_for('login'))

    return wrap


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user_id = db.session.query(db.func.max(User.id)).scalar()
            if user_id is None:
                user_id = 0
            new_user = User(
                user_id + 1,
                form.name.data,
                form.email.data,
                form.password.data,
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Thanks for registering. Please login.')
                return redirect(url_for("login"))
            except IntegrityError:
                error = 'That username and/or email already exist'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                flash('Welcome!')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid username or password.'
        else:
            error = 'Both fields are required.'
    return render_template('login.html', form=form, error=error)


@app.route("/logout")
@login_required
def logout():
    session.pop("logged_in", None)
    session.pop('user_id', None)
    flash("Goodbye")
    return redirect(url_for("login"))


@login_required
def open_tasks():
    return db.session.query(Task).filter_by(status='1').order_by(Task.due_date.asc())


@login_required
def closed_tasks():
    return db.session.query(Task).filter_by(status='0').order_by(Task.due_date.asc())


@app.route("/tasks")
@login_required
def tasks():
    return render_template("tasks.html", form=AddTaskForm(request.form),
                           open_tasks=open_tasks(),
                           closed_tasks=closed_tasks(),
                           )


@app.route("/add", methods=["POST"])
@login_required
def new_task():
    form = AddTaskForm(request.form)
    error = None
    if request.method == 'POST':
        if form.validate_on_submit():
            task_id = db.session.query(db.func.max(Task.task_id)).scalar()
            if task_id is None:
                task_id = 0
            new_task = Task(
                task_id + 1,
                form.name.data,
                form.due_date.data,
                datetime.utcnow(),
                form.priority.data,
                '1',
                session['user_id']
            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
            return redirect(url_for('tasks'))
        else:
            return render_template('tasks.html', form=form, error=error, open_tasks=open_tasks(),
                                   closed_tasks=closed_tasks())
    return render_template("tasks.html", form=form, error=error, open_tasks=open_tasks(),
                           closed_tasks=closed_tasks())


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error in the {} field - {}".format(getattr(form.field).label.text, error))


@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id:
        task.update({"status": "0"})
        db.session.commit()
        flash('The task was marked as complete.')
        return redirect(url_for('tasks'))
    else:
        flash('You can only update tasks that belong to you.')
        return redirect(url_for('tasks'))


# Delete Tasks
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id:
        task.delete()
        db.session.commit()
        flash('The task was deleted.')
        return redirect(url_for('tasks'))
    else:
        flash('You can only delete tasks that belong to you.')
        return redirect(url_for('tasks'))


if __name__ == '__main__':
    app.run(debug=True)
