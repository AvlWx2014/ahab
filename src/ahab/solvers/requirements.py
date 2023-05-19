import re
from functools import partial
from typing import Collection

from packaging.requirements import Requirement

from ..result import Conditional, Ok, Result
from .base import Solver, solution_impossible

REQUIREMENTS_FILE_REGEX = re.compile(f".*requirements.*\.txt")


class RequirementsSolver(Solver):
    def solve(self) -> Result[Collection[str]]:
        if not self.path.exists():
            return solution_impossible(f"Path {self.path} does not exist.")

        if not REQUIREMENTS_FILE_REGEX.match(self.path.name):
            return solution_impossible(
                f"Path {self.path} does not appear to be a requirements file."
            )

        packages = []
        factory = Ok
        with self.path.open("r") as in_:
            for line in in_:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                first, *rest = line.split()
                match first:
                    case "-e":
                        packages.extend(rest)
                    case "-i" | "--index-url" | "--extra-index-url" | "-f" | "--find-links":
                        factory = partial(
                            Conditional,
                            message=(
                                f"Packages from {self.path} have been downloaded "
                                f"from an index other than PyPI @ {rest[0] if rest else '????'}"
                            ),
                        )
                    case _:
                        if first.startswith("-"):
                            continue
                        req = Requirement(line)
                        # using str(req) would be too verbose for these purposes
                        # but using a package from somewhere other than PyPI should be highlighted
                        identifier = req.name
                        if req.url:
                            identifier += f"@ {req.url}"
                        packages.append(identifier)

        return factory(result=packages)
