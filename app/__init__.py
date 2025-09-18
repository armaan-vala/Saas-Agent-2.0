from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # <-- ADD THIS LINE
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate() # <-- AND ADD THIS LINE

def create_app(config_class=Config):
    """
    Creates and configures the Flask application.
    This is the application factory pattern.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db) # <-- AND ADD THIS LINE

    # Register blueprints
    from app.main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.agents import agents_bp
    app.register_blueprint(agents_bp)

    from app.chat import chat_bp
    app.register_blueprint(chat_bp)

    # A simple route to test the app is running
    @app.route('/test')
    def test_page():
        return "<h1>It's alive! The Flask application is running.</h1>"

    return app

from app import models