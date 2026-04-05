from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Task
from datetime import datetime, timedelta

bp = Blueprint("main", __name__)


def _parse_due_date(raw_value):
    if not raw_value:
        return None

    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(raw_value, fmt)
            if fmt == "%Y-%m-%d":
                return parsed.replace(hour=23, minute=59)
            return parsed
        except ValueError:
            continue

    return None


def _sanitize_priority(value, fallback=1):
    try:
        priority = int(value)
    except (TypeError, ValueError):
        priority = fallback
    return max(0, min(priority, 3))


@bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    sort_by = request.args.get("sort_by", "created_at")
    view = request.args.get("view", "today")
    now = datetime.now()

    query = Task.query

    # search
    if q:
        query = query.filter(
            (Task.title.ilike(f"%{q}%")) |
            (Task.description.ilike(f"%{q}%"))
        )

    # filter
    if status_filter in {"todo", "doing", "done"}:
        query = query.filter(Task.status == status_filter)

    if view == "today":
        start_of_today = datetime(now.year, now.month, now.day)
        start_of_tomorrow = start_of_today + timedelta(days=1)
        query = query.filter(
            Task.due_date.isnot(None),
            Task.due_date >= start_of_today,
            Task.due_date < start_of_tomorrow,
        )
    elif view == "pending":
        query = query.filter(Task.status != "done")
    elif view == "overdue":
        query = query.filter(Task.status != "done", Task.due_date.isnot(None), Task.due_date < now)

    # sorting
    if sort_by == "priority":
        query = query.order_by(Task.priority.desc())
    elif sort_by == "due_date":
        query = query.order_by(Task.due_date.asc())
    else:
        query = query.order_by(Task.created_at.desc())

    tasks = query.all()

    due_soon_tasks = (
        Task.query
        .filter(
            Task.status != "done",
            Task.due_date.isnot(None),
            Task.due_date >= now,
            Task.due_date <= now + timedelta(hours=24),
        )
        .order_by(Task.due_date.asc())
        .all()
    )

    week_start = (now - timedelta(days=6)).date()
    per_day_counts = {week_start + timedelta(days=i): 0 for i in range(7)}
    done_tasks = (
        Task.query
        .filter(
            Task.status == "done",
            Task.updated_at.isnot(None),
            Task.updated_at >= datetime.combine(week_start, datetime.min.time()),
        )
        .all()
    )
    for task in done_tasks:
        completed_day = task.updated_at.date()
        if completed_day in per_day_counts:
            per_day_counts[completed_day] += 1

    weekly_labels = [(week_start + timedelta(days=i)).strftime("%a") for i in range(7)]
    weekly_data = [per_day_counts[week_start + timedelta(days=i)] for i in range(7)]

    due_notifications = [
        {
            "title": task.title,
            "due_date": task.due_date.strftime("%Y-%m-%d %H:%M"),
            "storage_key": f"task-due-notified-{task.id}-{task.due_date.isoformat()}",
        }
        for task in due_soon_tasks
    ]

    return render_template(
        "index.html",
        tasks=tasks,
        q=q,
        status_filter=status_filter,
        sort_by=sort_by,
        view=view,
        due_soon_tasks=due_soon_tasks,
        weekly_labels=weekly_labels,
        weekly_data=weekly_data,
        due_notifications=due_notifications,
    )


@bp.route("/task/create", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = request.form.get("description")
        priority = _sanitize_priority(request.form.get("priority"), fallback=1)
        due_date_str = request.form.get("due_date")
        due_date = _parse_due_date(due_date_str)
        status = request.form.get("status") if request.form.get("status") in {"todo", "doing", "done"} else "todo"

        if not title:
            flash("Title is required.")
        elif not due_date:
            flash("Deadline date and time are required.")
        else:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                status=status
            )
            db.session.add(task)
            db.session.commit()
            return redirect(url_for("main.index"))

    return render_template("task_form.html")


@bp.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == "POST":
        task.title = (request.form.get("title") or "").strip()
        task.description = request.form.get("description")
        task.priority = _sanitize_priority(request.form.get("priority"), fallback=task.priority)

        due_date_str = request.form.get("due_date")
        parsed_due_date = _parse_due_date(due_date_str)
        if not parsed_due_date:
            flash("Deadline date and time are required.")
            return render_template("task_form.html", task=task)
        task.due_date = parsed_due_date

        task.status = request.form.get("status") if request.form.get("status") in {"todo", "doing", "done"} else task.status

        if not task.title:
            flash("Title is required.")
            return render_template("task_form.html", task=task)

        db.session.commit()
        return redirect(url_for("main.index"))

    return render_template("task_form.html", task=task)


@bp.route("/task/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main.index"))
# trigger CI
