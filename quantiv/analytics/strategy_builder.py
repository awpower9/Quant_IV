"""
strategy_builder.py — Multi-leg option strategy P&L engine.

Constructs standard strategies (straddle, strangle, spread, etc.)
and computes combined P&L profiles.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class OptionLeg:
    """A single leg of a multi-leg strategy."""
    strike: float
    expiry: float
    option_type: str       # "call" or "put"
    position: str          # "long" or "short"
    quantity: int = 1
    premium: float = 0.0   # price paid/received per contract


@dataclass
class Strategy:
    """A named multi-leg strategy."""
    name: str
    legs: list[OptionLeg] = field(default_factory=list)

    def add_leg(self, leg: OptionLeg) -> None:
        self.legs.append(leg)


class StrategyBuilder:
    """Builds option strategies and computes P&L profiles."""

    @staticmethod
    def long_straddle(strike: float, expiry: float,
                      call_premium: float, put_premium: float) -> Strategy:
        """Create a long straddle: long call + long put at same strike."""
        return Strategy(
            name="Long Straddle",
            legs=[
                OptionLeg(strike, expiry, "call", "long", 1, call_premium),
                OptionLeg(strike, expiry, "put", "long", 1, put_premium),
            ],
        )

    @staticmethod
    def bull_call_spread(lower_strike: float, upper_strike: float,
                         expiry: float, lower_premium: float,
                         upper_premium: float) -> Strategy:
        """Create a bull call spread: long lower-strike call + short upper-strike call."""
        return Strategy(
            name="Bull Call Spread",
            legs=[
                OptionLeg(lower_strike, expiry, "call", "long", 1, lower_premium),
                OptionLeg(upper_strike, expiry, "call", "short", 1, upper_premium),
            ],
        )
    @staticmethod
    def bear_put_spread(lower_strike: float, upper_strike: float,
                        expiry: float, lower_premium: float,
                        upper_premium: float) -> Strategy:
        """Create a bear put spread: long upper-strike put + short lower-strike put."""
        return Strategy(
            name="Bear Put Spread",
            legs=[
                OptionLeg(upper_strike, expiry, "put", "long", 1, upper_premium),
                OptionLeg(lower_strike, expiry, "put", "short", 1, lower_premium),
            ],
        )

    @staticmethod
    def compute_payoff(strategy: Strategy,
                       spot_range: tuple[float, float],
                       num_points: int = 200) -> pd.DataFrame:
        """
        Compute the P&L at expiry for a strategy over a range of spot prices.

        Returns:
            DataFrame with columns: spot, payoff, profit.
        """
        spots = np.linspace(spot_range[0], spot_range[1], num_points)
        payoffs = np.zeros(num_points)

        for leg in strategy.legs:
            sign = 1.0 if leg.position == "long" else -1.0

            if leg.option_type == "call":
                intrinsic = np.maximum(spots - leg.strike, 0.0)
            else:
                intrinsic = np.maximum(leg.strike - spots, 0.0)

            payoffs += sign * leg.quantity * (intrinsic - leg.premium)

        return pd.DataFrame({
            "spot": spots,
            "payoff": payoffs + sum(
                (1 if l.position == "long" else -1) * l.premium * l.quantity
                for l in strategy.legs
            ),
            "profit": payoffs,
        })
