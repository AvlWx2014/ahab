from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Mapping, MutableMapping, Tuple

from ..result import Fail, Result


class SpecificationType(Enum):
    NONE = 0
    REQUIREMENTS = 1
    PYPROJECT = 2
    PDM = 3
    POETRY = 4
    PIPENV = 5
    PIPFILE = 6


class SolutionImpossible(Exception):
    pass


class Solver(ABC):
    
    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self):
        return self._path

    @abstractmethod
    def solve(self) -> Result[Collection[str]]:
        ...


def solution_impossible(reason: str) -> Fail:
    return Fail(SolutionImpossible(reason))
