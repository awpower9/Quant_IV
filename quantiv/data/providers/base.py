"""
base.py — Abstract MarketDataProvider interface.

All market data providers (Yahoo, Polygon, Alpha Vantage, etc.)
must implement this interface. The LiveMarketService consumes
providers through this ABC, never directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from quantiv.data.market_source import MarketQuote
from quantiv.data.option_chain import OptionChain


class MarketDataProvider(ABC):
    """
    Abstract base class for real-time market data providers.

    Subclasses must implement all four data-fetching methods.
    Each method should raise ``ConnectionError`` on network failures
    and ``ValueError`` on invalid symbols.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name (e.g., 'Yahoo Finance')."""
        ...

    # ── Core Data Methods ────────────────────────────────────────────────

    @abstractmethod
    def get_spot_price(self, symbol: str) -> float:
        """
        Fetch the current spot price for a symbol.

        Args:
            symbol: Ticker symbol (e.g., 'AAPL').

        Returns:
            Current market price as a float.

        Raises:
            ValueError: If the symbol is invalid or not found.
            ConnectionError: If the API is unreachable.
        """
        ...

    @abstractmethod
    def get_option_chain(self, symbol: str) -> OptionChain:
        """
        Fetch the full option chain for a symbol.

        Args:
            symbol: Ticker symbol.

        Returns:
            OptionChain with all available contracts.

        Raises:
            ValueError: If no options data is available.
            ConnectionError: If the API is unreachable.
        """
        ...

    @abstractmethod
    def get_risk_free_rate(self) -> float:
        """
        Fetch the current risk-free rate.

        Typically proxied by the 3-month US Treasury yield.

        Returns:
            Annualized rate as a decimal (e.g., 0.05 for 5%).
        """
        ...

    @abstractmethod
    def get_historical_volatility(
        self, symbol: str, period: str = "1y", window: int = 30
    ) -> float:
        """
        Compute annualized historical volatility from daily returns.

        Args:
            symbol: Ticker symbol.
            period: Lookback period (e.g., '1y', '6mo', '3mo').
            window: Rolling window in trading days for vol calculation.

        Returns:
            Annualized historical volatility as a decimal.
        """
        ...

    # ── Convenience ──────────────────────────────────────────────────────

    def get_quote(self, symbol: str) -> MarketQuote:
        """
        Build a complete MarketQuote from individual data methods.

        This is a convenience method that combines spot, vol, and rate
        into the existing MarketQuote data structure used by the analytics layer.
        """
        return MarketQuote(
            symbol=symbol.upper(),
            spot=self.get_spot_price(symbol),
            vol=self.get_historical_volatility(symbol),
            rate=self.get_risk_free_rate(),
            dividend=0.0,
        )
