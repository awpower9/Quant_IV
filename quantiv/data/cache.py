"""
cache.py — Thread-safe TTL-based data cache.

Prevents excessive API calls by caching market data with
per-key time-to-live (TTL) expiration.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Any


@dataclass
class _CacheEntry:
    """A single cached value with its expiration timestamp."""
    value: Any
    expires_at: float  # time.time() + ttl


class DataCache:
    """
    Thread-safe in-memory cache with per-key TTL.

    Usage:
        cache = DataCache(default_ttl=30.0)
        cache.set("AAPL:spot", 175.50)
        price = cache.get("AAPL:spot")  # returns 175.50 if < 30s old

        # Custom TTL per key
        cache.set("rate", 0.05, ttl=3600)  # cache for 1 hour
    """

    def __init__(self, default_ttl: float = 30.0) -> None:
        """
        Args:
            default_ttl: Default time-to-live in seconds for cached entries.
        """
        self._default_ttl = default_ttl
        self._store: dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """
        Retrieve a cached value if it exists and has not expired.

        Args:
            key: Cache key (e.g., "AAPL:spot", "AAPL:chain").

        Returns:
            The cached value, or None if expired or missing.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if time.time() > entry.expires_at:
                # Expired — remove and return None
                del self._store[key]
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """
        Store a value in the cache.

        Args:
            key:   Cache key.
            value: Value to cache.
            ttl:   Time-to-live in seconds (uses default if None).
        """
        effective_ttl = ttl if ttl is not None else self._default_ttl
        with self._lock:
            self._store[key] = _CacheEntry(
                value=value,
                expires_at=time.time() + effective_ttl,
            )

    def invalidate(self, key: str) -> None:
        """Remove a specific key from the cache."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._store.clear()

    def is_fresh(self, key: str) -> bool:
        """Check if a key exists and has not expired."""
        return self.get(key) is not None

    @property
    def size(self) -> int:
        """Number of entries currently in the cache (including expired)."""
        return len(self._store)
