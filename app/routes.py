@bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    sort_by = request.args.get("sort_by", "created_at")

    query = Task.query

    # search
    if q:
        query = query.filter(
            (Task.title.ilike(f"%{q}%")) |
            (Task.description.ilike(f"%{q}%"))
        )

    # filter
    if status_filter:
        query = query.filter(Task.status == status_filter)

    # sorting
    if sort_by == "priority":
        query = query.order_by(Task.priority.desc())
    elif sort_by == "due_date":
        query = query.order_by(Task.due_date.asc())
    else:
        query = query.order_by(Task.created_at.desc())

    tasks = query.all()

    return render_template("index.html", tasks=tasks, q=q)