import os
from collections import defaultdict
from pathlib import Path
from typing import Collection, Mapping

from attr import frozen

from .funky import none
from .result import Fail, Result
from .solvers import (
    PdmSolver,
    PipenvSolver,
    PoetrySolver,
    PyprojectSolver,
    RequirementsSolver,
    SolutionImpossible,
    Solver,
    SpecificationType,
)


@frozen
class Project:
    name: str
    root: Path

    def solve(self) -> Collection[Result[Collection[str]]]:
        results = []

        try:
            solvers = self._solvers()
        except SolutionImpossible as si:
            results.append(Fail(si))
            return results

        for solver in solvers:
            results.append(solver.solve())

        return results

    def _solvers(self) -> Collection[Solver]:
        checks = defaultdict(list)
        for root, dirs, files in os.walk(self.root):
            for file in files:
                path = Path(root, file)
                match file:
                    case "pdm.lock":
                        checks[SpecificationType.PDM].append(PdmSolver(path))
                    case "poetry.lock":
                        checks[SpecificationType.POETRY].append(PoetrySolver(path))
                    case "Pipfile.lock":
                        checks[SpecificationType.PIPENV].append(PipenvSolver(path))
                    case "Pipfile":
                        # TODO: replace eventually with PipfileSolver
                        checks[SpecificationType.PIPFILE].append(PipenvSolver(path))
                    case "pyproject.toml":
                        checks[SpecificationType.PYPROJECT].append(
                            PyprojectSolver(path)
                        )
                    case "requirements.txt" | "requirements-dev.txt" | "test-requirements.txt":
                        checks[SpecificationType.REQUIREMENTS].append(
                            RequirementsSolver(path)
                        )
            break

        return self._rank_choice(checks)

    def _rank_choice(
        self, solvers: Mapping[SpecificationType, Collection[Solver]]
    ) -> Collection[Solver]:
        # rule 1: if no solvers were found, raise
        if none(solvers.values()):
            raise SolutionImpossible(
                f"Could not determine how dependencies are managed for {self.name}"
            )
        # rule 2: if more than one of PDM, Poetry, Pipenv, and requirements.txt are
        #         being used at the same time, raise an error
        if (
            solvers[SpecificationType.PDM]
            and solvers[SpecificationType.POETRY]
            and solvers[SpecificationType.PIPFILE]
            and solvers[SpecificationType.REQUIREMENTS]
        ):
            raise SolutionImpossible(
                f"Dependency management strategy is ambiguous for {self.name}. "
                "Multiple possible tools found."
            )

        # note on match:
        # [] matches a list of exactly 0 elements
        # [_] matches a list of exactly 1 element
        # [*_] matches a list of 0 or more elements
        # [_, *_] matches a list of 1 or more elements
        # [_, _] matches a list of exactly 2 elements
        # etc
        match solvers:
            case {
                SpecificationType.PDM: [_],
            }:
                return solvers[SpecificationType.PDM]
            case {SpecificationType.POETRY: [_]}:
                return solvers[SpecificationType.POETRY]
            case {
                SpecificationType.PDM: [],
                SpecificationType.POETRY: [],
                SpecificationType.PYPROJECT: [_],
            }:
                # rule 3: only use pyproject if there's no corresponding lockfile
                #         for whichever tool is being used
                return solvers[SpecificationType.PYPROJECT]
            case {SpecificationType.PIPENV: [_]}:
                return solvers[SpecificationType.PIPENV]
            case {SpecificationType.PIPENV: [], SpecificationType.PIPFILE: [_]}:
                # rule 4: only use Pipfile if there is no corresponding lockfile
                return solvers[SpecificationType.PIPFILE]
            case {SpecificationType.REQUIREMENTS: [_, *_]}:
                return solvers[SpecificationType.REQUIREMENTS]
            case _:
                raise SolutionImpossible(
                    f"Could not determine how dependencies are managed for {self.name}"
                )
