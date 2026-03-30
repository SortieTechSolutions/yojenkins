---
name: yojenkins-test-scaffold
description: Generates properly structured pytest test files for yojenkins modules. Use when asked to "add tests", "test this module", or "write tests for" any yojenkins module.
---

# yojenkins Test Scaffold

Generate pytest test files following yojenkins project conventions.

## Steps

1. **Read the target module** to identify all public methods/functions
2. **Check conftest.py** (`tests/conftest.py`) for existing fixtures
3. **Generate the test file** at `tests/test_<module_name>.py`
4. **Update conftest.py** with any new shared fixtures needed

## Test File Structure

```python
"""Tests for yojenkins/<module_path>."""
import pytest
from unittest.mock import MagicMock, patch

# Import the module under test
from yojenkins.<module_path> import <Class/function>


class Test<ClassName>:
    """Tests for <ClassName>."""

    @pytest.fixture
    def instance(self, mock_rest):
        """Create instance with mocked dependencies."""
        return <ClassName>(rest=mock_rest)

    def test_<method>_success(self, instance):
        """Test <method> with valid input."""
        ...

    def test_<method>_error(self, instance):
        """Test <method> with error response."""
        ...

    @pytest.mark.parametrize('input_val,expected', [
        ('valid', True),
        ('invalid', False),
    ])
    def test_<method>_variations(self, instance, input_val, expected):
        ...
```

## Required Fixtures (add to conftest.py if missing)

```python
@pytest.fixture
def mock_rest():
    """Mock Rest object with mocked FuturesSession."""
    rest = MagicMock()
    rest.server_url = 'http://localhost:8080'
    rest.request = MagicMock()
    return rest

@pytest.fixture
def mock_auth():
    """Mock Auth object with pre-set credentials."""
    auth = MagicMock()
    auth.username = 'testuser'
    auth.api_token = 'test-token'
    return auth

@pytest.fixture
def jenkins_response():
    """Factory for Jenkins JSON API responses."""
    def _response(data, status_code=200):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = data
        resp.text = str(data)
        return resp
    return _response
```

## Module-Specific Guidance

- **utility.py**: Test pure functions directly (no mocks needed for most)
- **rest.py**: Mock requests.Session and FuturesSession
- **auth.py**: Mock file I/O (tmp_path fixture), REST calls, getpass
- **build.py/job.py/folder.py**: Mock REST responses with Jenkins JSON fixtures
- **credential.py**: Mock REST, test XML parsing with sample XML strings
- **CLI modules**: Use `click.testing.CliRunner` with `invoke()`
- **monitor_utility.py**: Test drawing calculations, skip curses calls

## Naming Convention

- Test files: `test_<source_module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<method>_<scenario>`
- Scenarios: `success`, `error`, `empty`, `invalid_input`, `not_found`, `timeout`
