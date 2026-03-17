"""
pricer.py — Unified pricing facade.

All C++ engine access goes through this module. The Dash UI and analytics
layer should ONLY call Pricer, never _quantiv_engine directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantiv.pricing.validators import validate_inputs

# This import will work once the C++ extension is built.
# During development without the extension, calls will raise ImportError.
try:
    from quantiv import _quantiv_engine as engine
except ImportError:
    engine = None  # type: ignore


# ── Pythonic result wrapper ──────────────────────────────────────────────────

@dataclass
class PricingResult:
    """Python-friendly wrapper around the C++ PricingResult."""
    price: float = 0.0
    greeks: dict[str, float] = field(default_factory=dict)
    tree: list[list[float]] = field(default_factory=list)
    path_prices: list[float] = field(default_factory=list)
    model: str = ""

    @classmethod
    def from_cpp(cls, cpp_result: Any, model: str = "") -> "PricingResult":
        """Convert a C++ PricingResult to a Python PricingResult."""
        return cls(
            price=cpp_result.price,
            greeks=dict(cpp_result.greeks),
            tree=[list(row) for row in cpp_result.tree],
            path_prices=list(cpp_result.path_prices),
            model=model,
        )


# ── Model registry ──────────────────────────────────────────────────────────

_MODEL_MAP = {
    "bsm": "BlackScholes",
    "black_scholes": "BlackScholes",
    "binomial": "Binomial",
    "bopm": "Binomial",
    "trinomial": "Trinomial",
    "monte_carlo": "MonteCarlo",
    "mc": "MonteCarlo",
}


# ── Pricer facade ────────────────────────────────────────────────────────────

class Pricer:
    """
    Unified pricing interface.

    Example:
        pricer = Pricer()
        result = pricer.price(
            model="bsm",
            spot=100, strike=100, vol=0.2,
            rate=0.05, expiry=1.0, option_type="call"
        )
        print(result.price, result.greeks)
    """

    def price(
        self,
        model: str,
        spot: float,
        strike: float,
        vol: float,
        rate: float,
        expiry: float,
        option_type: str = "call",
        dividend: float = 0.0,
        exercise_style: str = "european",
        steps: int = 100,
        num_paths: int = 100_000,
        seed: int = 42,
    ) -> PricingResult:
        """
        Price an option using the specified model.

        Args:
            model:          One of "bsm", "binomial", "trinomial", "monte_carlo"
            spot:           Current underlying price
            strike:         Option strike price
            vol:            Annualized volatility (e.g., 0.2 for 20%)
            rate:           Risk-free rate (e.g., 0.05 for 5%)
            expiry:         Time to expiration in years
            option_type:    "call" or "put"
            dividend:       Continuous dividend yield (default 0)
            exercise_style: "european" or "american"
            steps:          Number of tree steps (binomial/trinomial)
            num_paths:      Number of MC simulation paths
            seed:           Random seed for MC

        Returns:
            PricingResult with price, greeks, and model-specific data.
        """
        if engine is None:
            raise ImportError(
                "C++ engine not built. Run 'pip install -e .' to build."
            )

        # ── Validate inputs ──────────────────────────────────────────────
        validate_inputs(
            spot=spot, strike=strike, vol=vol,
            rate=rate, expiry=expiry
        )

        # ── Build C++ objects ────────────────────────────────────────────
        opt_type = (engine.OptionType.Call
                    if option_type.lower() == "call"
                    else engine.OptionType.Put)
        ex_style = (engine.ExerciseStyle.American
                    if exercise_style.lower() == "american"
                    else engine.ExerciseStyle.European)

        option = engine.Option(strike, expiry, opt_type, ex_style)
        market = engine.MarketData(spot, vol, rate, dividend)

        # ── Dispatch to model ────────────────────────────────────────────
        model_key = model.lower().replace("-", "_")
        if model_key not in _MODEL_MAP:
            raise ValueError(
                f"Unknown model '{model}'. "
                f"Choose from: {', '.join(_MODEL_MAP.keys())}"
            )

        model_name = _MODEL_MAP[model_key]

        if model_name == "BlackScholes":
            pricer = engine.BlackScholes()
        elif model_name == "Binomial":
            pricer = engine.Binomial(steps)
        elif model_name == "Trinomial":
            pricer = engine.Trinomial(steps)
        elif model_name == "MonteCarlo":
            pricer = engine.MonteCarlo(num_paths, seed)
        else:
            raise ValueError(f"Model '{model_name}' not implemented.")

        cpp_result = pricer.price(option, market)

        return PricingResult.from_cpp(cpp_result, model=model_name)
