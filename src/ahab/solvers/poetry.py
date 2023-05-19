import tomllib
from typing import Collection

from ..result import Fail, Ok, Result
from .base import Solver, solution_impossible


class PoetrySolver(Solver):
    def solve(self) -> Result[Collection[str]]:
        if not self.path.exists():
            return solution_impossible(f"Path {self.path} does not exist.")

        if self.path.name != "poetry.lock":
            return solution_impossible(
                f"Path {self.path} does not appear to be a Poetry lock file."
            )

        with self.path.open("rb") as in_:
            try:
                toml = tomllib.load(in_)
            except Exception as e:
                return Fail(e)

        try:
            packages = map(lambda p: p["name"], toml["package"])
        except Exception as e:
            return Fail(e)

        return Ok(list(packages))
