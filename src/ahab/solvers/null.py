from typing import Collection

from ..result import Result
from .base import Solver, solution_impossible


class NullSolver(Solver):
    def solve(self) -> Result[Collection[str]]:
        return solution_impossible(
            f"Could not determine how dependencies are managed for {self.path}"
        )
