from app import create_app
from app.core.extensions import db
from app.seed import seed_if_empty

app = create_app()

with app.app_context():
    db.create_all()
    seed_if_empty()
