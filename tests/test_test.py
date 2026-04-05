"""Smoke test to verify pytest runs."""

import logging

logger = logging.getLogger(__name__)


def test_smoke():
    """Verify pytest infrastructure works."""
    logger.info("Smoke test passed")
    assert True
