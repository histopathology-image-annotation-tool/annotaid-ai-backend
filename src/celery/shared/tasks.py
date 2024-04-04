from typing import Any, Iterable

from celery.canvas import Signature

from celery import group, shared_task, subtask


@shared_task(bind=True)
def dmap(self, iterable: Iterable[Signature], callback: Signature) -> Signature:
    # Map a callback over an iterator and return as a group
    callback = subtask(callback)
    sig = group(callback.clone([arg,]) for arg in iterable)

    return self.replace(sig)


@shared_task(bind=True)
def expand_args(self, args: Any, func: Signature) -> Signature:
    func = subtask(func)

    sig = func.clone([*args])

    return self.replace(sig)


@shared_task
def noop(arg: Any) -> Any:
    return arg


@shared_task(bind=True)
def residual(self, residual: Any, func: Signature) -> Signature:
    func = subtask(func)

    sig = group([
        noop.s(residual),
        func.clone([residual,])
    ])

    return self.replace(sig)
