"""
yahoo.py — Yahoo Finance market data provider using yfinance.

This is the primary provider for the Quantiv platform. It fetches:
- Real-time spot prices
- Full option chains with bid/ask/IV/OI
- Risk-free rate (proxied by ^IRX — 13-week T-bill)
- Historical volatility from daily close prices
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np

from quantiv.data.providers.base import MarketDataProvider
from quantiv.data.option_chain import OptionChain, OptionContract

logger = logging.getLogger(__name__)


class YahooFinanceProvider(MarketDataProvider):
    """
    Market data provider backed by Yahoo Finance (yfinance).

    Usage:
        provider = YahooFinanceProvider()
        spot = provider.get_spot_price("AAPL")
        chain = provider.get_option_chain("AAPL")
        vol = provider.get_historical_volatility("AAPL")
    """

    @property
    def name(self) -> str:
        return "Yahoo Finance"

    # ── Spot Price ───────────────────────────────────────────────────────

    def get_spot_price(self, symbol: str) -> float:
        """Fetch the latest spot price via yfinance."""
        import yfinance as yf

        symbol = symbol.upper()
        ticker = yf.Ticker(symbol)

        try:
            # fast_info is the fastest way to get the current price
            price = ticker.fast_info.get("lastPrice")
            if price is None:
                price = ticker.fast_info.get("regularMarketPrice")
            if price is None:
                # Fallback: get the last close from history
                hist = ticker.history(period="1d")
                if hist.empty:
                    raise ValueError(f"No price data for symbol '{symbol}'")
                price = float(hist["Close"].iloc[-1])
            return float(price)

        except Exception as e:
            logger.error(f"Failed to fetch spot price for {symbol}: {e}")
            raise ConnectionError(
                f"Cannot fetch spot price for '{symbol}': {e}"
            ) from e

    # ── Option Chain ─────────────────────────────────────────────────────

    def get_option_chain(self, symbol: str) -> OptionChain:
        """Fetch the full option chain with all available expirations."""
        import yfinance as yf

        symbol = symbol.upper()
        ticker = yf.Ticker(symbol)

        try:
            expirations = ticker.options
            if not expirations:
                raise ValueError(f"No options data for '{symbol}'")

            contracts: list[OptionContract] = []
            now = datetime.now()

            for exp_str in expirations:
                # Parse expiration date and convert to years
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
                years_to_expiry = max(
                    (exp_date - now).days / 365.25, 0.001
                )

                chain = ticker.option_chain(exp_str)

                # Process calls
                for _, row in chain.calls.iterrows():
                    contracts.append(self._row_to_contract(
                        row, years_to_expiry, "call"
                    ))

                # Process puts
                for _, row in chain.puts.iterrows():
                    contracts.append(self._row_to_contract(
                        row, years_to_expiry, "put"
                    ))

            return OptionChain(symbol=symbol, contracts=contracts)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch option chain for {symbol}: {e}")
            raise ConnectionError(
                f"Cannot fetch option chain for '{symbol}': {e}"
            ) from e

    # ── Risk-Free Rate ───────────────────────────────────────────────────

    def get_risk_free_rate(self) -> float:
        """
        Fetch the risk-free rate proxied by the 13-week T-bill yield (^IRX).

        Falls back to a hardcoded 5% if the fetch fails.
        """
        import yfinance as yf

        try:
            irx = yf.Ticker("^IRX")
            hist = irx.history(period="5d")
            if hist.empty:
                logger.warning("No ^IRX data, using fallback rate 0.05")
                return 0.05
            # ^IRX is quoted as a percentage, convert to decimal
            rate = float(hist["Close"].iloc[-1]) / 100.0
            return rate

        except Exception as e:
            logger.warning(f"Failed to fetch risk-free rate: {e}. Using 0.05")
            return 0.05

    # ── Historical Volatility ────────────────────────────────────────────

    def get_historical_volatility(
        self, symbol: str, period: str = "1y", window: int = 30
    ) -> float:
        """
        Compute annualized historical volatility from daily log returns.

        Uses a rolling window of `window` trading days over the given period.
        """
        import yfinance as yf

        symbol = symbol.upper()

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty or len(hist) < window:
                raise ValueError(
                    f"Insufficient history for '{symbol}' "
                    f"(need {window} days, got {len(hist)})"
                )

            # Daily log returns
            closes = hist["Close"].values
            log_returns = np.log(closes[1:] / closes[:-1])

            # Rolling standard deviation (use last `window` days)
            recent_returns = log_returns[-window:]
            daily_vol = float(np.std(recent_returns, ddof=1))

            # Annualize: multiply by sqrt(252 trading days)
            annualized_vol = daily_vol * np.sqrt(252)
            return annualized_vol

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to compute hist vol for {symbol}: {e}")
            raise ConnectionError(
                f"Cannot compute historical vol for '{symbol}': {e}"
            ) from e

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_contract(
        row, years_to_expiry: float, option_type: str
    ) -> OptionContract:
        """Convert a yfinance DataFrame row to an OptionContract."""
        return OptionContract(
            strike=float(row.get("strike", 0)),
            expiry=years_to_expiry,
            option_type=option_type,
            bid=float(row.get("bid", 0)),
            ask=float(row.get("ask", 0)),
            last=float(row.get("lastPrice", 0)),
            volume=int(row.get("volume", 0) or 0),
            open_interest=int(row.get("openInterest", 0) or 0),
            implied_vol=float(row.get("impliedVolatility", 0) or 0),
        )
