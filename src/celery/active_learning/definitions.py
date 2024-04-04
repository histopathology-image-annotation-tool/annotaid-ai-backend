from celery import Task


class PollingException(Exception):
    pass


class PollingTask(Task):
    autoretry_for = (PollingException,)
    retry_kwargs = {'max_retries': 100, 'countdown': 5}
    retry_backoff = True
