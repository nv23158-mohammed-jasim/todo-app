from datetime import datetime
from . import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"<Task {self.id} {self.title}>"
