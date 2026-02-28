import uuid
from datetime import datetime
from app.core.extensions import db

class Trace(db.Model):
    __tablename__ = "traces"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)
    response_time_ms = db.Column(db.Integer, nullable=False)