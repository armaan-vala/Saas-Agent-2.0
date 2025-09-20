from app import create_app
from app.extensions import celery

# Create the Flask app instance
app = create_app()

# THIS IS THE OFFICIAL CELERY 5+ FIX
# It tells Celery to load its configuration directly from our Config object,
# and the 'namespace="CELERY"' part automatically handles the conversion
# from uppercase (CELERY_BROKER_URL) to lowercase (broker_url).
# This completely eliminates the "mixing keys" error.
celery.config_from_object('config:Config', namespace='CELERY')

# This ensures that tasks have access to the Flask application context
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask