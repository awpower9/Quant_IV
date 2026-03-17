"""
scheduler.py — Background refresh scheduler for live market data.

Uses threading.Timer to periodically refresh cached data
without blocking the Dash event loop.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable

logger = logging.getLogger(__name__)


class BackgroundRefresher:
    """
    Periodically runs a refresh function in a background thread.

    Usage:
        def refresh():
            cache.set("AAPL:spot", provider.get_spot_price("AAPL"))

        refresher = BackgroundRefresher(interval=15.0, callback=refresh)
        refresher.start()
        # ... later ...
        refresher.stop()
    """

    def __init__(
        self,
        interval: float,
        callback: Callable[[], None],
        name: str = "refresher",
    ) -> None:
        """
        Args:
            interval: Refresh interval in seconds.
            callback: Function to call on each tick.
            name:     Name for the timer thread (for debugging).
        """
        self._interval = interval
        self._callback = callback
        self._name = name
        self._timer: threading.Timer | None = None
        self._running = False
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the background refresh loop."""
        with self._lock:
            if self._running:
                return
            self._running = True
        logger.info(f"BackgroundRefresher '{self._name}' started "
                    f"(interval={self._interval}s)")
        self._schedule_next()

    def stop(self) -> None:
        """Stop the background refresh loop."""
        with self._lock:
            self._running = False
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        logger.info(f"BackgroundRefresher '{self._name}' stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    def _schedule_next(self) -> None:
        """Schedule the next tick."""
        if not self._running:
            return
        self._timer = threading.Timer(self._interval, self._tick)
        self._timer.daemon = True  # won't prevent program exit
        self._timer.name = f"quantiv-{self._name}"
        self._timer.start()

    def _tick(self) -> None:
        """Execute the callback and schedule the next run."""
        if not self._running:
            return
        try:
            self._callback()
        except Exception as e:
            logger.warning(
                f"BackgroundRefresher '{self._name}' callback failed: {e}"
            )
        # Schedule next tick regardless of success/failure
        self._schedule_next()
