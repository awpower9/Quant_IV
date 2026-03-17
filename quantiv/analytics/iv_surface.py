"""
iv_surface.py — Implied Volatility surface builder.

Constructs a 3D IV surface over a grid of strikes × maturities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from quantiv import _quantiv_engine as engine
except ImportError:
    engine = None  # type: ignore


class IVSurfaceBuilder:
    """Builds implied volatility surfaces from market prices or synthetic data."""

    def build_surface(
        self,
        spot: float,
        rate: float,
        strikes: list[float] | np.ndarray,
        expiries: list[float] | np.ndarray,
        market_prices: np.ndarray | None = None,
        option_type: str = "call",
    ) -> pd.DataFrame:
        """
        Build an IV surface.

        Args:
            spot:          Current underlying price.
            rate:          Risk-free rate.
            strikes:       Array of strike prices.
            expiries:      Array of expiry times (years).
            market_prices: 2D array (len(expiries) × len(strikes)) of market prices.
                           If None, generates a synthetic flat-vol surface.
            option_type:   "call" or "put".

        Returns:
            DataFrame with columns: strike, expiry, iv.
        """
        if engine is None:
            raise ImportError("C++ engine not built.")

        solver = engine.ImpliedVolSolver()
        opt_type = (engine.OptionType.Call
                    if option_type.lower() == "call"
                    else engine.OptionType.Put)

        rows = []
        for i, T in enumerate(expiries):
            for j, K in enumerate(strikes):
                option = engine.Option(float(K), float(T), opt_type)
                market = engine.MarketData(spot, 0.2, rate)  # initial guess vol

                if market_prices is not None:
                    target = float(market_prices[i, j])
                else:
                    # Synthetic: use BSM to generate a price, then solve back
                    bsm = engine.BlackScholes()
                    synthetic_market = engine.MarketData(
                        spot, 0.2 + 0.05 * abs(K / spot - 1.0), rate
                    )
                    target = bsm.price(option, synthetic_market).price

                iv = solver.solve(option, market, target)
                rows.append({
                    "strike": float(K),
                    "expiry": float(T),
                    "iv": iv if iv > 0 else float("nan"),
                })

        return pd.DataFrame(rows)
