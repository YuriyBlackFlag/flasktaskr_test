# blog.py controller
# imports
from flask import Flask, render_template, request, session, \
    flash, redirect, url_for, g
from functools import wraps
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


@app.route("/main")
@login_required
def main():
    g.db = connect_db()
    cur = g.db.cursor()
    cur.execute("SELECT * FROM POSTS")
    posts = [dict(title=row[0], post=row[1]) for row in
             cur.fetchall()]
    cur.close()
    g.db.close()
    return render_template("main.html", posts=posts)


@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    post = request.form["post"]
    if not title or not post:
        flash("All fields are required")
        return redirect(url_for("main"))
    else:
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute("insert into posts (title, post) values (:1,:2)", [request.form['title'], request.form['post']])
        cur.close()
        g.db.commit()
        g.db.close()
        flash('New entry was successfully posted!')
        return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(debug=True)
