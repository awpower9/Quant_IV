"""
test_pricer.py — Tests for the Python Pricer facade.
"""

import pytest
from quantiv.pricing.validators import validate_inputs


class TestValidators:
    """Tests for input validation."""

    def test_valid_inputs(self):
        """Should not raise for valid inputs."""
        validate_inputs(spot=100, strike=100, vol=0.2, rate=0.05, expiry=1.0)

    def test_negative_spot(self):
        with pytest.raises(ValueError, match="Spot price must be positive"):
            validate_inputs(spot=-10, strike=100, vol=0.2, rate=0.05, expiry=1.0)

    def test_zero_strike(self):
        with pytest.raises(ValueError, match="Strike price must be positive"):
            validate_inputs(spot=100, strike=0, vol=0.2, rate=0.05, expiry=1.0)

    def test_negative_vol(self):
        with pytest.raises(ValueError, match="Volatility must be positive"):
            validate_inputs(spot=100, strike=100, vol=-0.1, rate=0.05, expiry=1.0)

    def test_unreasonable_vol(self):
        with pytest.raises(ValueError, match="unreasonably high"):
            validate_inputs(spot=100, strike=100, vol=11.0, rate=0.05, expiry=1.0)

    def test_zero_expiry(self):
        with pytest.raises(ValueError, match="Time to expiry must be positive"):
            validate_inputs(spot=100, strike=100, vol=0.2, rate=0.05, expiry=0)

    def test_negative_rate_allowed(self):
        """Negative rates should be allowed (e.g., EUR rates)."""
        validate_inputs(spot=100, strike=100, vol=0.2, rate=-0.01, expiry=1.0)


# Integration tests below require the C++ extension to be built.
# They will be skipped if the extension is not available.

try:
    from quantiv.pricing import Pricer
    HAS_ENGINE = True
except ImportError:
    HAS_ENGINE = False


@pytest.mark.skipif(not HAS_ENGINE, reason="C++ engine not built")
class TestPricerIntegration:
    """Integration tests that require the compiled C++ engine."""

    def setup_method(self):
        self.pricer = Pricer()

    def test_bsm_atm_call(self, sample_params, expected_bsm_price):
        result = self.pricer.price(model="bsm", **sample_params)
        assert abs(result.price - expected_bsm_price) < 0.01

    def test_binomial_converges(self, sample_params, expected_bsm_price):
        result = self.pricer.price(model="binomial", steps=500, **sample_params)
        assert abs(result.price - expected_bsm_price) < 0.1

    def test_monte_carlo_converges(self, sample_params, expected_bsm_price):
        result = self.pricer.price(
            model="monte_carlo", num_paths=500000, seed=42, **sample_params
        )
        assert abs(result.price - expected_bsm_price) < 0.2

    def test_unknown_model(self, sample_params):
        with pytest.raises(ValueError, match="Unknown model"):
            self.pricer.price(model="nonexistent", **sample_params)

    def test_bsm_greeks_present(self, sample_params):
        result = self.pricer.price(model="bsm", **sample_params)
        assert "delta" in result.greeks
        assert "gamma" in result.greeks
        assert "vega" in result.greeks
