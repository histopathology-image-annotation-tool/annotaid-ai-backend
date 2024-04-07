from collections.abc import Iterable
from typing import Any

from celery import Task, group, shared_task, subtask
from celery.canvas import Signature


@shared_task(bind=True, ignore_result=True)
def dmap(self: Task, iterable: Iterable[Signature], callback: Signature) -> Signature:
    # Map a callback over an iterator and return as a group
    callback = subtask(callback)
    sig = group(callback.clone([arg,]) for arg in iterable)

    return self.replace(sig)


@shared_task(bind=True, ignore_result=True)
def expand_args(self: Task, args: Any, func: Signature) -> Signature:
    func = subtask(func)

    sig = func.clone([*args])

    return self.replace(sig)


@shared_task(ignore_result=True)
def noop(arg: Any) -> Any:
    return arg


@shared_task(bind=True, ignore_result=True)
def residual(self: Task, residual: Any, func: Signature) -> Signature:
    func = subtask(func)

    sig = group([
        noop.s(residual),
        func.clone([residual,])
    ])

    return self.replace(sig)
