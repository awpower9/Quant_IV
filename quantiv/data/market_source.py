"""
market_source.py — Abstract market data interface.

Provides a MockMarketSource for development and a base class
for future real API integrations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MarketQuote:
    """A snapshot of market data for an underlying."""
    symbol: str
    spot: float
    vol: float           # implied or historical vol
    rate: float          # risk-free rate
    dividend: float = 0.0


class MarketSource(ABC):
    """Abstract interface for market data providers."""

    @abstractmethod
    def get_quote(self, symbol: str) -> MarketQuote:
        """Fetch current market data for a symbol."""
        ...

    @abstractmethod
    def get_risk_free_rate(self) -> float:
        """Fetch current risk-free rate."""
        ...


class MockMarketSource(MarketSource):
    """Mock market data for development and testing."""

    _MOCK_DATA: dict[str, MarketQuote] = {
        "AAPL": MarketQuote("AAPL", 175.0, 0.25, 0.05, 0.006),
        "SPY":  MarketQuote("SPY",  450.0, 0.18, 0.05, 0.013),
        "TSLA": MarketQuote("TSLA", 250.0, 0.55, 0.05, 0.0),
        "GOOG": MarketQuote("GOOG", 140.0, 0.28, 0.05, 0.0),
    }

    def get_quote(self, symbol: str) -> MarketQuote:
        symbol = symbol.upper()
        if symbol not in self._MOCK_DATA:
            raise KeyError(f"No mock data for symbol '{symbol}'")
        return self._MOCK_DATA[symbol]

    def get_risk_free_rate(self) -> float:
        return 0.05
