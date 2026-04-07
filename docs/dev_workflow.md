# Development Workflow

This project is developed on Windows using the repository-local virtual environment in `.venv`.

## Activate The Environment

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Use `python` after activation. Do not use `py -3.11` in normal project commands.

## Install Or Refresh Editable Dependencies

Install the package and development dependencies:

```powershell
python -m pip install -e .[dev]
```

Run this again after package metadata or dependency declarations change in `pyproject.toml`.

## Run Tests

```powershell
python -m pytest
```

## Run The CLI

Module entry:

```powershell
python -m rnr_mapgen
```

Console script entry:

```powershell
rnr-mapgen
```

## Python Version

The project supports Python 3.11 and newer. The current local development workflow is working on Python 3.14.

## Deactivate The Environment

When finished:

```powershell
deactivate
```
