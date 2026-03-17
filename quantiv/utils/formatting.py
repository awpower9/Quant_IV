"""
formatting.py — Number formatting utilities for display.
"""


def format_price(value: float, decimals: int = 4) -> str:
    """Format a price value with appropriate precision."""
    return f"${value:,.{decimals}f}"


def format_pct(value: float, decimals: int = 2) -> str:
    """Format a decimal as a percentage string."""
    return f"{value * 100:.{decimals}f}%"


def format_greeks(greeks: dict[str, float], decimals: int = 6) -> dict[str, str]:
    """Format a Greeks dictionary for display."""
    formatted = {}
    for name, val in greeks.items():
        if name in ("delta", "gamma"):
            formatted[name] = f"{val:.{decimals}f}"
        elif name in ("vega", "theta", "rho"):
            formatted[name] = f"{val:.{decimals}f}"
        else:
            formatted[name] = f"{val:.{decimals}f}"
    return formatted
