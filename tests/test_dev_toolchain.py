"""Verify dev toolchain is installed and runnable.

Catches the case where documented commands (ruff, pytest, etc.)
silently stop working due to missing installs or broken environments.
"""

import shutil
import subprocess
import sys

import pytest

import yojenkins


@pytest.mark.cli
class TestDevToolchain:
    """Ensure documented dev tools are available and functional."""

    def test_ruff_available(self):
        """ruff must be importable as a module."""
        assert shutil.which('ruff') or self._module_runnable('ruff'), 'ruff not found. Install with: pip install ruff'

    def test_ruff_check_runs(self):
        """ruff check must exit cleanly (no config errors)."""
        result = subprocess.run(
            [sys.executable, '-m', 'ruff', 'check', '--select', 'E', '--quiet', 'yojenkins/__init__.py'],
            capture_output=True,
            timeout=30,
            check=False,
        )
        assert result.returncode in (0, 1), f'ruff check failed unexpectedly: {result.stderr.decode()}'

    def test_ruff_format_runs(self):
        """ruff format --check must exit cleanly (no config errors)."""
        result = subprocess.run(
            [sys.executable, '-m', 'ruff', 'format', '--check', 'yojenkins/__init__.py'],
            capture_output=True,
            timeout=30,
            check=False,
        )
        assert result.returncode in (0, 1), f'ruff format failed unexpectedly: {result.stderr.decode()}'

    def test_yojenkins_importable(self):
        """The yojenkins package must be importable."""
        assert hasattr(yojenkins, '__version__')

    def _module_runnable(self, module: str) -> bool:
        result = subprocess.run(
            [sys.executable, '-m', module, '--version'],
            capture_output=True,
            timeout=10,
            check=False,
        )
        return result.returncode == 0
