# blog.py controller
# imports
from datetime import datetime
from functools import wraps
from flask import flash, redirect, render_template, \
    request, session, url_for, Blueprint
from .forms import AddTaskForm
from project import db
from project.models import Task

tasks_blueprint = Blueprint('tasks', __name__)


# function used for connecting to the database
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
        return redirect(url_for('users.login'))

    return wrap


@login_required
def open_tasks():
    return db.session.query(Task).filter_by(status='1').order_by(Task.due_date.asc())


@login_required
def closed_tasks():
    return db.session.query(Task).filter_by(status='0').order_by(Task.due_date.asc())


@tasks_blueprint.route("/tasks")
@login_required
def tasks():
    return render_template("tasks.html", form=AddTaskForm(request.form),
                           open_tasks=open_tasks(),
                           closed_tasks=closed_tasks(),
                           )


@tasks_blueprint.route("/add", methods=["POST"])
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
            return redirect(url_for('tasks.tasks'))
        else:
            return render_template('tasks.html', form=form, error=error, open_tasks=open_tasks(),
                                   closed_tasks=closed_tasks())
    return render_template("tasks.html", form=form, error=error, open_tasks=open_tasks(),
                           closed_tasks=closed_tasks())


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error in the {} field - {}".format(getattr(form.field).label.text, error))


@tasks_blueprint.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.update({"status": "0"})
        db.session.commit()
        flash('The task was marked as complete.')
        return redirect(url_for('tasks.tasks'))
    else:
        flash('You can only update tasks that belong to you.')
        return redirect(url_for('tasks.tasks'))


# Delete Tasks
@tasks_blueprint.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.delete()
        db.session.commit()
        flash('The task was deleted.')
        return redirect(url_for('tasks.tasks'))
    else:
        flash('You can only delete tasks that belong to you.')
        return redirect(url_for('tasks.tasks'))
