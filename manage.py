import os
from app import create_app, db 
from app.models import Agent, Document, Conversation, Message
from flask_migrate import Migrate
from app.extensions import celery
from config import Config 

app = create_app()

migrate = Migrate(app, db) 


celery.config_from_object(Config, namespace='CELERY') 

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

from app import tasks 

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Agent': Agent, 'Document': Document, 'Conversation': Conversation, 'Message': Message}

# If you have custom Flask commands, add them here
# @app.cli.command()
# def custom_command():
#     """A custom command."""
#     print("Hello from custom command!")