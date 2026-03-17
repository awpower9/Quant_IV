"""
validators.py — Input validation for pricing parameters.

Raises descriptive ValueError for any invalid input before it hits C++.
"""


def validate_inputs(
    spot: float,
    strike: float,
    vol: float,
    rate: float,
    expiry: float,
) -> None:
    """
    Validate common pricing inputs.

    Raises:
        ValueError: If any input is out of valid range.
    """
    if spot <= 0:
        raise ValueError(f"Spot price must be positive, got {spot}")
    if strike <= 0:
        raise ValueError(f"Strike price must be positive, got {strike}")
    if vol <= 0:
        raise ValueError(f"Volatility must be positive, got {vol}")
    if vol > 10.0:
        raise ValueError(
            f"Volatility {vol} (={vol*100}%) seems unreasonably high. "
            "Maximum allowed is 10.0 (1000%)."
        )
    if expiry <= 0:
        raise ValueError(f"Time to expiry must be positive, got {expiry}")
    if expiry > 100.0:
        raise ValueError(
            f"Time to expiry {expiry} years seems unreasonable. "
            "Maximum allowed is 100 years."
        )
    # Rate can be negative (e.g., EUR rates), no lower bound check.
