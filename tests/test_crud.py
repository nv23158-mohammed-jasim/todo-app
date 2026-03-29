from app import create_app, db
from app.models import Task


def setup_test_app():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    return app


def test_create_task():
    # Arrange
    app = setup_test_app()

    # Act
    with app.test_client() as client:
        resp = client.post(
            "/task/create",
            data={"title": "Buy milk"},
            follow_redirects=True
        )

        # Assert
        assert resp.status_code == 200
        page = resp.get_data(as_text=True)
        assert "Buy milk" in page

        with app.app_context():
            task = Task.query.filter_by(title="Buy milk").first()
            assert task is not None


def test_update_task():
    # Arrange
    app = setup_test_app()

    with app.app_context():
        task = Task(title="Old title")
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    # Act
    with app.test_client() as client:
        resp = client.post(
            f"/task/{task_id}/edit",
            data={"title": "New title"},
            follow_redirects=True
        )

        # Assert
        assert resp.status_code == 200
        page = resp.get_data(as_text=True)
        assert "New title" in page
        assert "Old title" not in page

        with app.app_context():
            updated_task = Task.query.get(task_id)
            assert updated_task.title == "New title"


def test_delete_task():
    # Arrange
    app = setup_test_app()

    with app.app_context():
        task = Task(title="To be deleted")
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    # Act
    with app.test_client() as client:
        resp = client.post(f"/task/{task_id}/delete", follow_redirects=True)

        # Assert
        assert resp.status_code == 200
        page = resp.get_data(as_text=True)
        assert "To be deleted" not in page

        with app.app_context():
            deleted_task = Task.query.get(task_id)
            assert deleted_task is None