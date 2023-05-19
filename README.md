# ahab
Gathers information on dependencies used by your Python projects whether you use requiremens.txt, PDM, Poetry, Pipenv, or just plain pyproject.toml.

## Usage
```text
usage: entrypoint.py [-h] [--debug] root

Hunt for Python packages. Do your best to find locked packages (e.g. from pdm.lock, poetry.lock, etc.)

positional arguments:
  root        The root directory to search in.

options:
  -h, --help  show this help message and exit
  --debug     Enable debug logging. It's going to get crowded in here...
```

## Targeting Projects
Ahab fixates on its mark. Add a `.ahab` file to a project's root directory in order to mark it so that Ahab will hunt there.

**Example:**
Run Ahab on a `repos` directory to check all of your VCS managed projects:
```shell
$ pwd
/home/AvlWx2014/repos
$ find . -maxdepth 1 -type d
./python-project1/
./python-project2/
./python-project3/
$ find . -maxdepth 1 -type d -exec touch {}/.ahab \;
$ tree -aL 2
.
|-- python-project1/
|   |-- .ahab
|-- python-project2/
|   |-- .ahab
|-- python-project3/
    |-- .ahab
```