from abc import ABC
from typing import Generic, Never, Optional, TypeVar

from attr import frozen

A = TypeVar("A")


class Result(ABC, Generic[A]):
    pass


@frozen
class Ok(Generic[A], Result[A]):
    result: A


@frozen
class Conditional(Generic[A], Result[A]):
    result: A
    message: str


@frozen
class Fail(Result[Never]):
    exception: Exception
