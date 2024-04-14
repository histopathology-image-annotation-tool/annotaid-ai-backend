from collections.abc import Iterable
from typing import Any

from celery import Task, group, shared_task, subtask
from celery.canvas import Signature


@shared_task(bind=True, ignore_result=True)
def dmap(self: Task, iterable: Iterable[Signature], callback: Signature) -> Signature:
    """Map a callback over an iterable of tasks and return as a group.

    Args:
        iterable (Iterable[Signature]): The iterable of tasks.
        callback (Signature): The callback to map over the tasks.

    Returns:
        Signature: The group of tasks.
    """

    # Map a callback over an iterator and return as a group
    callback = subtask(callback)
    sig = group(callback.clone([arg,]) for arg in iterable)

    return self.replace(sig)


@shared_task(bind=True, ignore_result=True)
def expand_args(self: Task, args: Any, func: Signature) -> Signature:
    """Expand arguments and call a function.

    Args:
        args (Any): The arguments to expand.
        func (Signature): The function to call.

    Returns:
        Signature: The expanded function.
    """
    print(self.request)

    func = subtask(func)

    sig = func.clone([*args])

    return self.replace(sig)


@shared_task(ignore_result=True)
def noop(arg: Any) -> Any:
    """No operation task.

    Args:
        arg (Any): The argument to return.

    Returns:
        Any: The argument.
    """
    return arg


@shared_task(bind=True, ignore_result=True)
def residual(self: Task, residual: Any, func: Signature) -> Signature:
    """Pass a residual to a function
    and return the result of the function along with the residual.

    Args:
        residual (Any): The residual to pass.
        func (Signature): The function to call.

    Returns:
        Signature: The function with the residual.
    """
    func = subtask(func)

    sig = group([
        noop.s(residual),
        func.clone([residual,])
    ])

    return self.replace(sig)
