from app import create_app
from app.extensions import celery

# Create a Flask app instance using the factory
# This is necessary for the Celery tasks to have application context
flask_app = create_app()

# This line is crucial for making sure tasks can access Flask's context
celery.conf.update(flask_app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask