from typing import Callable, Collection, Iterable, List, Tuple, TypeVar

A = TypeVar("A")


def none(iterable: Iterable[A], predicate: Callable[[A], bool] = bool) -> bool:
    for item in iterable:
        if predicate(item):
            return False
    return True
