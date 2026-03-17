"""
test_integration.py — End-to-end C++ → Python integration tests.

These tests verify the complete pipeline from Python through pybind11 to C++.
Skipped if the C++ extension is not available.
"""

import pytest

try:
    from quantiv import _quantiv_engine as engine
    HAS_ENGINE = True
except ImportError:
    HAS_ENGINE = False


@pytest.mark.skipif(not HAS_ENGINE, reason="C++ engine not built")
class TestDirectEngineAccess:
    """Test raw _quantiv_engine bindings (for debugging, not recommended for production)."""

    def test_option_creation(self):
        opt = engine.Option(100.0, 1.0, engine.OptionType.Call)
        assert opt.strike == 100.0
        assert opt.expiry == 1.0

    def test_market_data_creation(self):
        mkt = engine.MarketData(100.0, 0.2, 0.05)
        assert mkt.spot == 100.0
        assert mkt.vol == 0.2

    def test_bsm_direct(self):
        opt = engine.Option(100.0, 1.0, engine.OptionType.Call)
        mkt = engine.MarketData(100.0, 0.2, 0.05)
        bsm = engine.BlackScholes()
        result = bsm.price(opt, mkt)
        assert result.price > 0

    def test_binomial_direct(self):
        opt = engine.Option(100.0, 1.0, engine.OptionType.Call)
        mkt = engine.MarketData(100.0, 0.2, 0.05)
        bin_model = engine.Binomial(100)
        result = bin_model.price(opt, mkt)
        assert result.price > 0
        assert len(result.tree) > 0

    def test_monte_carlo_direct(self):
        opt = engine.Option(100.0, 1.0, engine.OptionType.Call)
        mkt = engine.MarketData(100.0, 0.2, 0.05)
        mc = engine.MonteCarlo(10000, 42)
        result = mc.price(opt, mkt)
        assert result.price > 0
        assert len(result.path_prices) == 10000

    def test_greeks_engine(self):
        opt = engine.Option(100.0, 1.0, engine.OptionType.Call)
        mkt = engine.MarketData(100.0, 0.2, 0.05)
        ge = engine.GreeksEngine()
        greeks = ge.compute_bsm_greeks(opt, mkt)
        assert "delta" in greeks
        assert 0.0 < greeks["delta"] < 1.0

    def test_iv_solver(self):
        opt = engine.Option(100.0, 1.0, engine.OptionType.Call)
        mkt = engine.MarketData(100.0, 0.2, 0.05)
        bsm = engine.BlackScholes()
        target = bsm.price(opt, mkt).price

        solver = engine.ImpliedVolSolver()
        iv = solver.solve(opt, mkt, target)
        assert abs(iv - 0.2) < 0.001  # should recover the original vol
