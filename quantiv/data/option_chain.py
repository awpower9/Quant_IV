"""
option_chain.py — Option chain data structure.

Represents a set of options for a given underlying at various
strikes and expirations.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OptionContract:
    """A single option in a chain."""
    strike: float
    expiry: float          # in years
    option_type: str       # "call" or "put"
    bid: float = 0.0
    ask: float = 0.0
    last: float = 0.0
    volume: int = 0
    open_interest: int = 0
    implied_vol: float = 0.0

    @property
    def mid(self) -> float:
        """Mid-market price."""
        return (self.bid + self.ask) / 2.0


@dataclass
class OptionChain:
    """A collection of option contracts for an underlying."""
    symbol: str
    contracts: list[OptionContract] = field(default_factory=list)

    def calls(self) -> list[OptionContract]:
        """Filter to call options only."""
        return [c for c in self.contracts if c.option_type == "call"]

    def puts(self) -> list[OptionContract]:
        """Filter to put options only."""
        return [c for c in self.contracts if c.option_type == "put"]

    def at_strike(self, strike: float) -> list[OptionContract]:
        """Get all contracts at a specific strike."""
        return [c for c in self.contracts if c.strike == strike]
