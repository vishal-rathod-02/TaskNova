from app import create_app
from app.celery_app import celery

# Importing this module creates the Flask application before Celery executes a task.
flask_app = create_app()
