from . import db
from datetime import datetime
from enum import Enum

class PriorityEnum(Enum):
    low = 0
    medium = 1
    high = 2

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    
    # NEW FIELDS
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.Integer, default=PriorityEnum.medium.value)
    due_date = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default="todo")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)