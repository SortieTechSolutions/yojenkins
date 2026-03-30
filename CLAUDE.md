# CLAUDE.md - yojenkins

## Project Overview
yojenkins is a Python CLI tool for managing Jenkins servers from the command line.
It wraps the Jenkins REST API and python-jenkins SDK with a Click-based CLI,
curses-based terminal monitors, and Docker container management.

## Quick Reference
- **Language**: Python 3.9+ (target-version in ruff config)
- **CLI Framework**: Click 8.x with click-help-colors
- **Jenkins SDK**: python-jenkins 1.8.2
- **Async HTTP**: requests-futures (FuturesSession, 16 workers)
- **Linter/Formatter**: ruff (line-length 119, single quotes)
- **Tests**: pytest (currently placeholder only)
- **Package Manager**: pipenv (Pipfile + Pipfile.lock)
- **CI**: GitHub Actions (pull-request-check.yml, test-build-publish.yml)

## Architecture

### Three-Layer CLI Pattern
1. `yojenkins/cli_sub_commands/*.py` - Click decorators, arguments, options, wiring
2. `yojenkins/cli/cli_*.py` - CLI logic (auth setup, output formatting, history)
3. `yojenkins/yo_jenkins/*.py` - Business logic (no Click dependency)

### Key Modules
- `yo_jenkins/yojenkins.py` - Composite root class, wires all modules together
- `yo_jenkins/rest.py` - REST layer (FuturesSession + HTTPBasicAuth)
- `yo_jenkins/auth.py` - Authentication, profile management, token generation
- `yo_jenkins/job.py` - Job operations (largest module)
- `yo_jenkins/build.py` - Build operations
- `yo_jenkins/folder.py` - Folder traversal with recursive search
- `utility/utility.py` - Shared utilities (large, needs refactoring)
- `monitor/*.py` - Curses-based terminal monitors
- `docker_container/docker_jenkins_server.py` - Docker Jenkins management

### Entry Point
`yojenkins/__main__.py` -> Click groups: auth, server, node, account,
credential, folder, job, build, stage, step, tools

## Development Commands
```bash
# Install dependencies
pipenv install --dev

# Run the tool
pipenv run yojenkins --help

# Lint
ruff check .
ruff check --fix .

# Format
ruff format .

# Run tests
pipenv run pytest

# Pre-commit (includes gitleaks, ruff, trailing whitespace)
pre-commit run --all-files

# Build package
python setup.py install
```

## Code Conventions

### CLI Commands
- Apply decorators in order: @debug, @format_output, @profile
- Use `translate_kwargs()` before passing kwargs to business logic
- Use `click.secho()` for colored output
- Show `ctx.get_help()` when required arguments are missing
- Wrap CLI handlers with `@log_to_history`

### Business Logic
- All API classes accept a `rest` object in __init__
- Use `logger.debug()` for operational logging
- Use `utility.fail_out()` for fatal errors
- Use `utility.print2()` for user-facing output from business logic

### Output Formatting
- `cli_utility.standard_out()` handles --pretty, --yaml, --xml, --toml flags
- `translate_kwargs()` renames reserved words: yaml->opt_yaml, json->opt_json

### Ruff Configuration
- Line length: 119
- Quote style: single
- Key rule sets: E, W, F, I, B, C4, UP, C90, PL, RUF
- Several files have per-file complexity suppressions (technical debt)

## Known Issues and Technical Debt
1. Test coverage is effectively zero (only placeholder tests exist)
2. API tokens stored in cleartext at ~/.yojenkins/credentials
3. utility/utility.py is oversized and should be split into focused modules
4. Multiple files suppress C901/PLR0912 (cyclomatic complexity)
5. Windows support is broken (commented out in CI matrix)
6. Monitor modules use bare except clauses (E722 suppressed)
7. DockerJenkinsServer defaults to password='password'

## Do Not
- Do not import Click in yo_jenkins/ business logic layer
- Do not store credentials in code or tests
- Do not use print() directly; use click.secho() in CLI layer, utility.print2() in business logic
- Do not add dependencies without updating both requirements.txt and Pipfile
