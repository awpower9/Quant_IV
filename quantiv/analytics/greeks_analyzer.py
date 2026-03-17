"""
greeks_analyzer.py — Greeks grid computation for visualization.

Computes Greeks over a range of spot prices or volatilities,
returning DataFrames suitable for Plotly charts.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class GreeksAnalyzer:
    """Computes Greeks grids over parameter ranges."""

    def __init__(self) -> None:
        from quantiv.pricing import Pricer
        self._pricer = Pricer()

    def greeks_vs_spot(
        self,
        spot_range: tuple[float, float],
        strike: float,
        vol: float,
        rate: float,
        expiry: float,
        option_type: str = "call",
        model: str = "bsm",
        num_points: int = 50,
    ) -> pd.DataFrame:
        """
        Compute all Greeks as a function of spot price.

        Returns:
            DataFrame with columns: spot, delta, gamma, vega, theta, rho.
        """
        spots = np.linspace(spot_range[0], spot_range[1], num_points)
        rows = []

        for s in spots:
            result = self._pricer.price(
                model=model, spot=float(s), strike=strike,
                vol=vol, rate=rate, expiry=expiry,
                option_type=option_type,
            )
            row = {"spot": float(s), "price": result.price}
            row.update(result.greeks)
            rows.append(row)

        return pd.DataFrame(rows)

    def greeks_vs_expiry(
        self,
        expiry_range: tuple[float, float],
        spot: float,
        strike: float,
        vol: float,
        rate: float,
        option_type: str = "call",
        model: str = "bsm",
        num_points: int = 50,
    ) -> pd.DataFrame:
        """Compute all Greeks as a function of time to expiry."""
        expiries = np.linspace(
            max(expiry_range[0], 0.001), expiry_range[1], num_points
        )
        rows = []

        for t in expiries:
            result = self._pricer.price(
                model=model, spot=spot, strike=strike,
                vol=vol, rate=rate, expiry=float(t),
                option_type=option_type,
            )
            row = {"expiry": float(t), "price": result.price}
            row.update(result.greeks)
            rows.append(row)

        return pd.DataFrame(rows)
