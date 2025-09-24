from flask import Flask
from config import Config
from app.extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    # Main blueprint (HTML pages) has no prefix
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # All API blueprints are registered under the /api prefix
    from .agents import agents_bp
    app.register_blueprint(agents_bp, url_prefix='/api')

    from .chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api')

    from .documents import documents_bp
    app.register_blueprint(documents_bp, url_prefix='/api')

    return app

from . import models

