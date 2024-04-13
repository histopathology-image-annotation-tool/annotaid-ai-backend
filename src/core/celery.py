from typing import Any

from celery import Celery, current_app
from celery.signals import before_task_publish
from src.core.config import settings
from src.schemas.celery import AsyncResultStatus

celery_app = Celery(
    __name__,
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_BACKEND_URL),
)
celery_app.conf.event_serializer = 'pickle'
celery_app.conf.task_serializer = 'pickle'
celery_app.conf.result_serializer = 'pickle'
celery_app.conf.accept_content = ['application/json', 'application/x-python-serialize']
celery_app.conf.result_extended = True
celery_app.conf.broker_transport_options = {
    'queue_order_strategy': 'priority',
    'sep': ":",
    'priority_steps': list(range(5))
}

celery_app.autodiscover_tasks([
    'src.celery.nuclick',
    'src.celery.mc',
    'src.celery.np',
    'src.celery.sam',
    'src.celery.active_learning'
])


@before_task_publish.connect
def create_result_key_in_backend(
    sender: str | None = None,
    headers: dict[str, Any] | None = None,
    body: str | None = None,
    **kwargs: Any
) -> None:
    """Create a result key in the backend when a task is published to be able
    to detect if the task with given id exists in the backend.
    """
    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend

    if headers is not None:
        backend.store_result(headers['id'], None, AsyncResultStatus.pending)
