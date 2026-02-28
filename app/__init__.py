from flask import Flask
from app.core.config import Config
from app.core.extensions import db, cors
from app.api.routes import api_bp
from app.seed import seed_if_empty

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app)

    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        seed_if_empty()

    return app