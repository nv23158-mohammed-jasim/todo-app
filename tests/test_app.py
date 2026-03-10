from app import create_app, db


def test_app_import():
    app = create_app()
    assert app is not None


def test_app_responds():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    with app.test_client() as c:
        rv = c.get("/")

    assert rv.status_code in [200, 302]