"""
test_analytics.py — Tests for the analytics layer.

These tests verify the analytics module's data transformation logic.
"""

import pytest

from quantiv.analytics.strategy_builder import (
    OptionLeg, Strategy, StrategyBuilder,
)


class TestStrategyBuilder:
    """Test the multi-leg strategy P&L engine."""

    def test_long_straddle_creation(self):
        strategy = StrategyBuilder.long_straddle(100, 1.0, 5.0, 4.0)
        assert strategy.name == "Long Straddle"
        assert len(strategy.legs) == 2

    def test_bull_call_spread_creation(self):
        strategy = StrategyBuilder.bull_call_spread(90, 110, 1.0, 12.0, 3.0)
        assert strategy.name == "Bull Call Spread"
        assert len(strategy.legs) == 2
        assert strategy.legs[0].position == "long"
        assert strategy.legs[1].position == "short"

    def test_payoff_computation(self):
        strategy = StrategyBuilder.long_straddle(100, 1.0, 5.0, 4.0)
        df = StrategyBuilder.compute_payoff(strategy, (50, 150), 100)
        assert "spot" in df.columns
        assert "profit" in df.columns
        assert len(df) == 100

    def test_custom_strategy(self):
        strategy = Strategy(name="Custom")
        strategy.add_leg(OptionLeg(100, 1.0, "call", "long", 1, 5.0))
        strategy.add_leg(OptionLeg(110, 1.0, "call", "short", 1, 2.0))
        assert len(strategy.legs) == 2
