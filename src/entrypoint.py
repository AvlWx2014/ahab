import os
import sys
import time
from argparse import ArgumentParser, Namespace
from datetime import timedelta
from pathlib import Path
from typing import Collection

from ahab.deforestation import configure_logging
from ahab.project import Project


def cli() -> ArgumentParser:
    parser = ArgumentParser(
        description="Hunt for Python packages. Do your best to find locked packages (e.g. from pdm.lock, poetry.lock, etc.)"
    )
    parser.add_argument("root", type=Path, help="The root directory to search in.")
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug logging. It's going to get crowded in here...",
    )
    return parser


def resolve_projects(root: Path) -> Collection[Project]:
    projects = []
    for root, dirs, files in os.walk(root):
        fs = set(files)
        if ".ahab" in fs:
            path = Path(root)
            projects.append(Project(path.name, Path(root)))
    return projects


def main(args: Namespace):
    root: Path = args.root
    if not (root.exists() and root.is_dir()):
        raise ValueError(
            f"root directory {args.root} does not exist or is not a directory."
        )

    projects = resolve_projects(root)
    LOG.debug("Found %d projects to search", len(projects))

    results = []
    for proj in resolve_projects(root):
        print(proj)
        results.extend(proj.solve())

    for result in results:
        print(result)


if __name__ == "__main__":
    parser = cli()
    args = parser.parse_args()

    LOG = configure_logging(enable_debug=args.debug)

    start = time.perf_counter()
    LOG.info("Running...")

    try:
        main(args)
    except Exception as e:
        LOG.exception("A fatal exception occurred")
        sys.exit(1)
    finally:
        end = time.perf_counter()
        LOG.info(f"Completed ({timedelta(seconds=end - start)})")
