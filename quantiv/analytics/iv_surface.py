"""
iv_surface.py — Implied Volatility surface builder.

Constructs a 3D IV surface over a grid of strikes × maturities.
Since the C++ Pybind11 engine was removed in favor of gRPC, 
this module uses a synthetic numpy-based volatility smile generator 
until the IV solver is added to the gRPC microservice.
"""

from __future__ import annotations
import numpy as np
import pandas as pd

class IVSurfaceBuilder:
    """Builds implied volatility surfaces."""

    def build_surface(
        self,
        spot: float,
        rate: float,
        strikes: list[float] | np.ndarray,
        expiries: list[float] | np.ndarray,
        market_prices: np.ndarray | None = None,
        option_type: str = "call",
    ) -> pd.DataFrame:
        """
        Build an IV surface using a synthetic volatility smile model.
        """
        rows = []
        base_vol = 0.20
        
        # Smile parameters
        alpha = 0.15   # Curvature (smile depth)
        beta = -0.05   # Skew (downside puts are usually more expensive)
        
        for T in expiries:
            # Term structure effect (volatility term structure)
            time_effect = 0.05 * np.log(1.0 + T)
            
            for K in strikes:
                moneyness = K / spot
                log_moneyness = np.log(moneyness)
                
                # Parabolic smile: IV = base + term + skew + curvature
                synthetic_iv = base_vol + time_effect + (beta * log_moneyness) + (alpha * (log_moneyness ** 2))
                
                # Ensure IV doesn't go below a sensible floor
                iv = max(synthetic_iv, 0.05)
                
                rows.append({
                    "strike": float(K),
                    "expiry": float(T),
                    "iv": iv,
                })

        return pd.DataFrame(rows)
