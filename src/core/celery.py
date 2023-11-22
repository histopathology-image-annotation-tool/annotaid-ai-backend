from celery import Celery
from src.core.config import settings

celery_app = Celery(
    __name__,
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_BACKEND_URL),
)
celery_app.conf.event_serializer = 'pickle'
celery_app.conf.task_serializer = 'pickle'
celery_app.conf.result_serializer = 'pickle'
celery_app.conf.accept_content = ['application/json', 'application/x-python-serialize']

celery_app.autodiscover_tasks([
    'src.celery.nuclick',
    'src.celery.mc',
    'src.celery.np',
    'src.celery.sam'
])
