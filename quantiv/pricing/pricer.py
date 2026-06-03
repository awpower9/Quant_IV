"""
pricer.py — Unified pricing facade via gRPC.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from quantiv.pricing.validators import validate_inputs
from dashboard.grpc_client import QuantivGrpcClient

grpc_client = QuantivGrpcClient()

@dataclass
class PricingResult:
    """Python-friendly wrapper around the protobuf PricingResponse."""
    price: float = 0.0
    greeks: dict[str, float] = field(default_factory=dict)
    tree: list[list[float]] = field(default_factory=list)
    path_prices: list[float] = field(default_factory=list)
    model: str = ""

    @classmethod
    def from_proto(cls, proto_result: Any, model: str = "") -> "PricingResult":
        greeks = {}
        if proto_result.HasField("greeks"):
            greeks = {
                "delta": proto_result.greeks.delta,
                "gamma": proto_result.greeks.gamma,
                "vega": proto_result.greeks.vega,
                "theta": proto_result.greeks.theta,
                "rho": proto_result.greeks.rho
            }
        return cls(
            price=proto_result.price,
            greeks=greeks,
            model=model,
        )

_MODEL_MAP = {
    "bsm": "BlackScholes",
    "black_scholes": "BlackScholes",
    "binomial": "Binomial",
    "bopm": "Binomial",
    "trinomial": "Trinomial",
    "monte_carlo": "MonteCarlo",
    "mc": "MonteCarlo",
}

class Pricer:
    """Unified pricing interface."""
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
        validate_inputs(spot=spot, strike=strike, vol=vol, rate=rate, expiry=expiry)
        
        is_call = option_type.lower() == "call"
        model_key = model.lower().replace("-", "_")
        if model_key not in _MODEL_MAP:
            raise ValueError(f"Unknown model '{model}'. Choose from: {', '.join(_MODEL_MAP.keys())}")
            
        model_name = _MODEL_MAP[model_key]

        try:
            if model_name == "BlackScholes":
                res = grpc_client.price_black_scholes(spot, strike, vol, rate, expiry, is_call)
            elif model_name == "Binomial":
                res = grpc_client.price_binomial(spot, strike, vol, rate, expiry, is_call, steps)
            elif model_name == "Trinomial":
                res = grpc_client.price_trinomial(spot, strike, vol, rate, expiry, is_call, steps)
            elif model_name == "MonteCarlo":
                res = grpc_client.price_monte_carlo(spot, strike, vol, rate, expiry, is_call, num_paths)
            else:
                raise ValueError(f"Model '{model_name}' not implemented.")
            return PricingResult.from_proto(res, model=model_name)
        except Exception as e:
            raise RuntimeError(f"gRPC Error: {e}")
