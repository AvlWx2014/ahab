import tomllib
from typing import Any, Collection, Mapping

from packaging.requirements import Requirement

from ..result import Conditional, Fail, Result
from .base import Solver, solution_impossible


class BadPyproject(Exception):
    pass


class PyprojectSolver(Solver):
    def solve(self) -> Result[Collection[str]]:
        if not self.path.exists():
            return solution_impossible(f"Path {self.path} does not exist.")

        if self.path.name != "pyproject.toml":
            return solution_impossible(
                f"Path {self.path} does not appear to be a Pyproject file."
            )

        with self.path.open("rb") as in_:
            try:
                toml = tomllib.load(in_)
            except Exception as e:
                return Fail(e)

        dependencies = list(self._get_project_dependencies(toml))

        tools = toml.get("tool", {})
        if not tools:
            # returning OK here, as it's possible to have project deps
            # without using a tool like PDM or Poetry
            # there's no way to tell if PDM was used at this point, so assume
            msg = f"Can't determine which tool might have authored pyproject.toml for {self.path.parent.name}."
            return Conditional(result=dependencies, message=msg)

        if "poetry" in tools and "pdm" in tools:
            return Fail(
                BadPyproject(
                    "Ambiguous tools usage: Pyproject contains configuration for multiple tools"
                )
            )

        if "poetry" in tools:
            dependencies.extend(self._get_poetry_dependencies(tools["poetry"]))

        if "pdm" in tools:
            dependencies.extend(self._get_pdm_dependencies(tools["pdm"]))

        msg = f"Using pyproject for {self.path.parent.name} over preferred tool-specific lockfile (e.g. pdm.lock, poetry.lock)."
        return Conditional(result=dependencies, message=msg)

    def _get_project_dependencies(self, toml: Mapping[str, Any]) -> Collection[str]:
        # collect [project.dependencies]
        if "project" not in toml:
            # not an error, Poetry does not utilize canonical pyproject
            # metadata fields
            return []

        project = toml["project"]
        deps = project.get("dependencies", [])
        # collect [project.optional-dependencies]
        optional = project.get("optional-dependencies", [])
        deps.extend(optional)
        return deps

    def _get_poetry_dependencies(
        self, poetry_config: Mapping[str, Any]
    ) -> Collection[str]:
        # collect [tool.poetry.dependencies]
        # which is the root dependency group
        project_deps = poetry_config.get("dependencies", {})
        deps = list(project_deps.keys())

        # collect [tool.poetry.dev-dependencies]
        # for pre poetry < 1.2.0
        dev_dependencies = poetry_config.get("dev-dependencies", {})
        deps.extend(dev_dependencies.keys())

        # collect other dependency groups
        # this will include dev dependencies in poetry >= 1.2.0
        # where it's called [tool.poetry.group.dev]
        groups = poetry_config.get("group", {})
        if not groups:
            return deps

        for _, group in groups.items():
            group_deps = group.get("dependencies", {})
            deps.extend(group_deps.keys())

        return deps

    def _get_pdm_dependencies(self, pdm_config: Mapping[str, Any]) -> Collection[str]:
        # collect [tool.pdm.dev-dependencies]
        # which can include multiple groups denoted by the group
        # name as a key in the dev-dependencies object
        dev_dependencies = pdm_config.get("dev-dependencies", {})
        if not dev_dependencies:
            return []

        deps = []
        for _, dependencies in dev_dependencies.items():
            # PDM groups are a mapping from
            # group name -> array of requirement specifiers
            reqs = map(Requirement, dependencies)
            deps.extend(r.name for r in reqs)

        return deps
