"""
conftest.py — Pytest fixtures for Python tests.
"""

import pytest


@pytest.fixture
def sample_params():
    """Standard ATM test parameters."""
    return {
        "spot": 100.0,
        "strike": 100.0,
        "vol": 0.2,
        "rate": 0.05,
        "expiry": 1.0,
        "option_type": "call",
    }


@pytest.fixture
def expected_bsm_price():
    """Known BSM price for ATM call: S=100, K=100, σ=0.2, r=0.05, T=1."""
    return 10.4506
