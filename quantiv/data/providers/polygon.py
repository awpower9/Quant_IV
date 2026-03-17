"""
polygon.py — Polygon.io market data provider (stub).

This provider requires a Polygon API key. It is provided as a
skeleton for future implementation.
"""

from __future__ import annotations

from quantiv.data.providers.base import MarketDataProvider
from quantiv.data.option_chain import OptionChain


class PolygonProvider(MarketDataProvider):
    """
    Polygon.io market data provider (stub).

    Requires:
        pip install polygon-api-client

    Usage:
        provider = PolygonProvider(api_key="your_key")
    """

    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "Polygon.io"

    def get_spot_price(self, symbol: str) -> float:
        raise NotImplementedError(
            "PolygonProvider is a stub. Set api_key and implement."
        )

    def get_option_chain(self, symbol: str) -> OptionChain:
        raise NotImplementedError(
            "PolygonProvider is a stub. Set api_key and implement."
        )

    def get_risk_free_rate(self) -> float:
        raise NotImplementedError(
            "PolygonProvider is a stub. Set api_key and implement."
        )

    def get_historical_volatility(
        self, symbol: str, period: str = "1y", window: int = 30
    ) -> float:
        raise NotImplementedError(
            "PolygonProvider is a stub. Set api_key and implement."
        )
