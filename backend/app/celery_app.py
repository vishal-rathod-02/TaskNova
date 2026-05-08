from celery import Celery

from .config import Config


def make_celery():
    celery = Celery("tasknova")
    celery.conf.broker_url = Config.CELERY_BROKER_URL
    celery.conf.result_backend = Config.CELERY_RESULT_BACKEND
    celery.conf.timezone = "UTC"
    return celery


celery = make_celery()
