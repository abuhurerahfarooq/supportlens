from app import create_app
from app.core.extensions import db
from app.seed import seed_if_empty
from dotenv import load_dotenv
load_dotenv()

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_if_empty()
    app.run(host="0.0.0.0", port=5000)