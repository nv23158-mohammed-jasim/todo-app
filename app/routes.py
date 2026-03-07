from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Task
from datetime import datetime

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("index.html", tasks=tasks)

@bp.route("/task/create", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority", type=int, default=1)
        due_date_str = request.form.get("due_date")
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
        status = request.form.get("status") or "todo"

        if not title:
            flash("Title is required.")
        else:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                status=status,
            )
            db.session.add(task)
            db.session.commit()
            return redirect(url_for("main.index"))

    return render_template("task_form.html")

@bp.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        task.priority = request.form.get("priority", type=int, default=task.priority)
        due_date_str = request.form.get("due_date")
        task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d") if due_date_str else None
        task.status = request.form.get("status") or task.status

        db.session.commit()
        return redirect(url_for("main.index"))

    return render_template("task_form.html", task=task)

@bp.route("/task/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main.index"))