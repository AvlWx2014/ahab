import json
import tomllib
from pathlib import Path
from typing import Collection

from ..result import Conditional, Ok, Result
from .base import Solver, solution_impossible


class PipenvSolver(Solver):
    def solve(self) -> Result[Collection[str]]:
        if not self.path.exists():
            return solution_impossible(f"Path{self.path} does not exist.")

        if self.path.name not in ("Pipfile", "Pipfile.lock"):
            return solution_impossible(
                f"Path {self.path} does not appear to be a Pipenv file."
            )

        match self.path.name:
            case "Pipfile.lock":
                packages = self._parse_pipenv_lockfile(self.path)
                return Ok(packages)
            case "Pipfile":
                packages = self._parse_pipfile(self.path)
                return Conditional(
                    result=packages,
                    message=(
                        f"Pipfile was used for {self.path.parent} instead of a more authoritative "
                        "Pipfile.lock. Transitive dependency, version, and index information may "
                        "be missing."
                    ),
                )

    def _parse_pipfile(self, path: Path) -> Collection[str]:
        with path.open("rb") as in_:
            toml = tomllib.load(in_)

        dependencies = []
        default = toml.get("packages", [])
        dependencies.extend(default.keys())
        dev = toml.get("dev-packages", [])
        dependencies.extend(dev.keys())

        return dependencies

    def _parse_pipenv_lockfile(self, path: Path) -> Collection[str]:
        with path.open("r") as in_:
            lockfile = json.load(in_)

        dependencies = []
        default = lockfile.get("default", {})
        develop = lockfile.get("develop", {})

        dependencies.extend(default.keys())
        dependencies.extend(develop.keys())

        return dependencies
