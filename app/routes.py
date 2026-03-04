from flask import current_app as app, render_template, request, redirect, url_for, flash
from . import db
from .models import Task


@app.route("/")
def index():
    tasks = Task.query.order_by(Task.id.desc()).all()
    return render_template("index.html", tasks=tasks)


@app.route("/task/create", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        title = request.form.get("title")
        if not title:
            flash("Title is required.")
        else:
            task = Task(title=title)
            db.session.add(task)
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("task_form.html")


@app.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == "POST":
        title = request.form.get("title")
        if not title:
            flash("Title is required.")
        else:
            task.title = title
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("task_form.html", task=task)


@app.route("/task/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))
