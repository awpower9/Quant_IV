"""
quantiv — Quantitative Options Pricing Platform

This is the top-level package. Import pricing and analytics from here.

Usage:
    from quantiv.pricing import Pricer
    pricer = Pricer()
    result = pricer.price(model="bsm", spot=100, strike=100, vol=0.2,
                          rate=0.05, expiry=1.0, option_type="call")
"""

__version__ = "1.0.0"
