"""
live_service.py — Unified facade for live market data.

This is the single entry point that the analytics layer and Dash callbacks
use to access market data. It routes through the cache and provider,
with automatic fallback to MockMarketSource on failure.

Usage:
    from quantiv.data.live_service import LiveMarketService

    service = LiveMarketService()
    service.start("AAPL")

    quote = service.get_live_quote("AAPL")   # MarketQuote
    chain = service.get_live_chain("AAPL")   # OptionChain
    spot  = service.get_live_spot("AAPL")    # float

    service.stop()
"""

from __future__ import annotations

import logging
import time
from enum import Enum

from quantiv.data.cache import DataCache
from quantiv.data.market_source import MarketQuote, MockMarketSource
from quantiv.data.option_chain import OptionChain
from quantiv.data.providers.base import MarketDataProvider
from quantiv.data.providers.yahoo import YahooFinanceProvider
from quantiv.data.scheduler import BackgroundRefresher

logger = logging.getLogger(__name__)


class DataStatus(Enum):
    """Status of the live data feed."""
    LIVE = "live"       # Fresh data from the API
    STALE = "stale"     # Cached data, not recently refreshed
    OFFLINE = "offline" # Using mock fallback


class LiveMarketService:
    """
    Unified live market data service.

    Manages provider selection, caching, background refresh,
    and graceful fallback to mock data.
    """

    # Cache TTLs (seconds)
    SPOT_TTL = 30.0
    CHAIN_TTL = 60.0
    RATE_TTL = 3600.0
    VOL_TTL = 300.0

    # Background refresh interval
    REFRESH_INTERVAL = 15.0

    # Error tracking
    MAX_CONSECUTIVE_FAILURES = 3
    COOLDOWN_SECONDS = 60.0

    def __init__(
        self,
        provider: MarketDataProvider | None = None,
    ) -> None:
        """
        Args:
            provider: Market data provider. Defaults to YahooFinanceProvider.
        """
        self._provider = provider or YahooFinanceProvider()
        self._cache = DataCache(default_ttl=self.SPOT_TTL)
        self._mock = MockMarketSource()
        self._refreshers: dict[str, BackgroundRefresher] = {}
        self._status = DataStatus.OFFLINE
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._tracked_symbols: set[str] = set()

    # ── Lifecycle ────────────────────────────────────────────────────────

    def start(self, symbol: str) -> None:
        """
        Start tracking a symbol with background refresh.

        Args:
            symbol: Ticker symbol to track (e.g., 'AAPL').
        """
        symbol = symbol.upper()
        if symbol in self._tracked_symbols:
            return

        self._tracked_symbols.add(symbol)

        # Initial fetch
        self._refresh_symbol(symbol)

        # Start background refresher
        refresher = BackgroundRefresher(
            interval=self.REFRESH_INTERVAL,
            callback=lambda s=symbol: self._refresh_symbol(s),
            name=f"spot-{symbol}",
        )
        self._refreshers[symbol] = refresher
        refresher.start()

        logger.info(f"LiveMarketService: tracking '{symbol}'")

    def stop(self, symbol: str | None = None) -> None:
        """
        Stop tracking a symbol (or all symbols if None).

        Args:
            symbol: Specific symbol to stop, or None for all.
        """
        if symbol is None:
            for s in list(self._tracked_symbols):
                self.stop(s)
            return

        symbol = symbol.upper()
        if symbol in self._refreshers:
            self._refreshers[symbol].stop()
            del self._refreshers[symbol]
        self._tracked_symbols.discard(symbol)
        logger.info(f"LiveMarketService: stopped tracking '{symbol}'")

    # ── Data Access ──────────────────────────────────────────────────────

    def get_live_spot(self, symbol: str) -> float:
        """Get the latest spot price (cached or fetched)."""
        symbol = symbol.upper()
        key = f"{symbol}:spot"

        cached = self._cache.get(key)
        if cached is not None:
            return cached

        # Not in cache — fetch now
        return self._fetch_spot(symbol)

    def get_live_quote(self, symbol: str) -> MarketQuote:
        """
        Get a full MarketQuote with live spot, vol, and rate.

        Returns the existing MarketQuote type used by the analytics layer.
        """
        symbol = symbol.upper()
        spot = self.get_live_spot(symbol)
        vol = self.get_live_vol(symbol)
        rate = self.get_live_rate()

        return MarketQuote(
            symbol=symbol,
            spot=spot,
            vol=vol,
            rate=rate,
            dividend=0.0,
        )

    def get_live_chain(self, symbol: str) -> OptionChain | None:
        """Get the option chain (cached or fetched)."""
        symbol = symbol.upper()
        key = f"{symbol}:chain"

        cached = self._cache.get(key)
        if cached is not None:
            return cached

        return self._fetch_chain(symbol)

    def get_live_vol(self, symbol: str) -> float:
        """Get historical volatility (cached or computed)."""
        symbol = symbol.upper()
        key = f"{symbol}:vol"

        cached = self._cache.get(key)
        if cached is not None:
            return cached

        return self._fetch_vol(symbol)

    def get_live_rate(self) -> float:
        """Get the risk-free rate (cached or fetched)."""
        key = "rate"
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        return self._fetch_rate()

    @property
    def status(self) -> DataStatus:
        """Current data feed status."""
        return self._status

    @property
    def tracked_symbols(self) -> set[str]:
        """Set of currently tracked symbols."""
        return self._tracked_symbols.copy()

    # ── Internal Fetch Methods ───────────────────────────────────────────

    def _refresh_symbol(self, symbol: str) -> None:
        """Refresh all data for a symbol (called by background refresher)."""
        self._fetch_spot(symbol)

    def _fetch_spot(self, symbol: str) -> float:
        """Fetch spot price with error handling and fallback."""
        if self._in_cooldown():
            return self._fallback_spot(symbol)

        try:
            price = self._provider.get_spot_price(symbol)
            self._cache.set(f"{symbol}:spot", price, ttl=self.SPOT_TTL)
            self._status = DataStatus.LIVE
            self._failure_count = 0
            return price
        except Exception as e:
            return self._handle_failure(f"spot:{symbol}", e,
                                        lambda: self._fallback_spot(symbol))

    def _fetch_chain(self, symbol: str) -> OptionChain | None:
        """Fetch option chain with error handling."""
        if self._in_cooldown():
            return None

        try:
            chain = self._provider.get_option_chain(symbol)
            self._cache.set(f"{symbol}:chain", chain, ttl=self.CHAIN_TTL)
            return chain
        except Exception as e:
            logger.warning(f"Failed to fetch chain for {symbol}: {e}")
            return None

    def _fetch_vol(self, symbol: str) -> float:
        """Fetch historical vol with fallback."""
        try:
            vol = self._provider.get_historical_volatility(symbol)
            self._cache.set(f"{symbol}:vol", vol, ttl=self.VOL_TTL)
            return vol
        except Exception:
            return 0.20  # fallback default vol

    def _fetch_rate(self) -> float:
        """Fetch risk-free rate with fallback."""
        try:
            rate = self._provider.get_risk_free_rate()
            self._cache.set("rate", rate, ttl=self.RATE_TTL)
            return rate
        except Exception:
            return 0.05  # fallback

    # ── Error Handling ───────────────────────────────────────────────────

    def _handle_failure(self, context: str, error: Exception,
                        fallback_fn) -> float:
        """Handle a provider failure with circuit-breaker logic."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        logger.warning(
            f"Provider failure ({self._failure_count}/{self.MAX_CONSECUTIVE_FAILURES}) "
            f"for {context}: {error}"
        )

        if self._failure_count >= self.MAX_CONSECUTIVE_FAILURES:
            self._status = DataStatus.OFFLINE
            logger.error(
                f"Circuit breaker activated. Falling back to mock data "
                f"for {self.COOLDOWN_SECONDS}s."
            )
        else:
            self._status = DataStatus.STALE

        return fallback_fn()

    def _in_cooldown(self) -> bool:
        """Check if we're in a cooldown period after too many failures."""
        if self._failure_count < self.MAX_CONSECUTIVE_FAILURES:
            return False
        elapsed = time.time() - self._last_failure_time
        if elapsed > self.COOLDOWN_SECONDS:
            # Cooldown expired — reset and allow retries
            self._failure_count = 0
            self._status = DataStatus.STALE
            return False
        return True

    def _fallback_spot(self, symbol: str) -> float:
        """Get spot price from mock data as fallback."""
        try:
            return self._mock.get_quote(symbol).spot
        except KeyError:
            return 100.0  # ultimate fallback
