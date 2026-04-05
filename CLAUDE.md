# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**yojenkins** is a CLI tool for managing Jenkins servers from the command line. Built with Click, it wraps the Jenkins REST API and `python-jenkins` SDK into a structured command hierarchy. Version 0.1.2, Python 3.7+ (targets 3.9+).

## Commands

All commands use `python3 -m` to invoke tools installed in the local environment. If `pipenv` is available, prefix with `pipenv run` instead.

### Setup
```bash
pip3 install -e .             # Editable install
pip3 install -r requirements.txt
```

### Lint & Format
```bash
python3 -m ruff check ./yojenkins              # Lint
python3 -m ruff check --fix ./yojenkins        # Lint with auto-fix
python3 -m ruff format --check ./yojenkins     # Format check
python3 -m ruff format ./yojenkins             # Auto-format
```

### Test
```bash
python3 -m pytest                                    # All tests
python3 -m pytest tests/test_test.py::test_smoke -v  # Single test
python3 -m pytest -m cli                             # CLI tests only (fast, no server)
python3 -m pytest -m integration                     # Integration tests (needs Docker Jenkins)
```

### Build
```bash
python3 setup.py sdist bdist_wheel                         # Package
python3 -m PyInstaller pyinstaller-onefile.spec -y --clean  # Binary
```

## Architecture

### Three-Layer Design
1. **CLI Layer** (`yojenkins/cli_sub_commands/`) - Click commands organized by domain (auth, server, job, build, folder, node, account, credential, stage, step, tools). Each module registers commands on groups defined in `__main__.py`.

2. **CLI Implementation** (`yojenkins/cli/`) - Bridge functions called by CLI commands. `cli_utility.py` handles output formatting (`standard_out`), error reporting (`fail_out`/`failures_out`), and config setup. `cli_decorators.py` provides reusable Click decorators (`@debug`, `@profile`, `@format_output`).

3. **Core Business Logic** (`yojenkins/yo_jenkins/`) - Domain classes (Auth, Rest, Build, Job, Folder, etc.) composed into the `YoJenkins` facade class (`yojenkins.py`). `Rest` wraps `requests` with `FuturesSession` (16 workers). `Auth` manages TOML credential profiles stored in `~/.yojenkins/credentials`.

### Other Key Modules
- **Monitor** (`yojenkins/monitor/`) - Curses-based TUI for real-time build/job monitoring with threaded data updates
- **Docker** (`yojenkins/docker_container/`) - Spins up local Jenkins servers via Docker for dev/testing

### Data Flow
CLI command -> `cli_sub_commands/*.py` -> `cli/*.py` (bridge) -> `yo_jenkins/*.py` (business logic) -> Jenkins REST API / SDK

## Code Conventions

- **Line length:** 119 characters
- **Quotes:** Single quotes (enforced by ruff formatter)
- **Imports:** Absolute imports, first-party package is `yojenkins`. `cli_utility.py` has an intentional isort skip (`I001`) for circular import avoidance.
- **Output:** All CLI output goes through `cli_utility.standard_out()` for format handling (JSON/YAML/XML/TOML/pretty). Errors through `fail_out()`/`failures_out()`.
- **Logging:** Module-level `logger = logging.getLogger()`, debug enabled via `--debug` flag.
- **`__main__.py` pattern:** Groups are defined first, then sub-command modules are imported below each group definition (unusual but intentional for Click registration).

## Ruff Configuration

Configured in `pyproject.toml`. Key rules: E/W, F, I, B, C4, UP, C90, PL, RUF. Several core modules have per-file complexity ignores (C901, PLR0912) because monitor UI and REST/auth logic is inherently complex. `__main__.py` is excluded from linting.

## Version Management

Version is defined in three places kept in sync by `bump2version`: `setup.py` (line 10), `yojenkins/__init__.py`, and `VERSION` file.
