from flask import Flask
from config import Config
from app.extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # --- THIS IS THE CRITICAL SECTION ---
    # Register all the blueprints with the app
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.agents import agents_bp
    app.register_blueprint(agents_bp)

    from app.chat import chat_bp
    app.register_blueprint(chat_bp)

    from app.documents import documents_bp
    app.register_blueprint(documents_bp)
    # ------------------------------------

    return app

from app import models



# from flask import Flask
# from config import Config
# from app.extensions import db, migrate

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     # Initialize Flask extensions
#     db.init_app(app)
#     migrate.init_app(app, db)

#     # Register blueprints
#     from app.main import main as main_blueprint
#     app.register_blueprint(main_blueprint)
    
#     from app.agents import agents_bp
#     app.register_blueprint(agents_bp)

#     from app.chat import chat_bp
#     app.register_blueprint(chat_bp)

#     from app.documents import documents_bp
#     app.register_blueprint(documents_bp)

#     return app

# from app import models