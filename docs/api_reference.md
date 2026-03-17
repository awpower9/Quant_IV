# API Reference

## Python API

### `quantiv.pricing.Pricer`

The main entry point for all pricing operations.

```python
from quantiv.pricing import Pricer

pricer = Pricer()
result = pricer.price(
    model="bsm",           # "bsm", "binomial", "trinomial", "monte_carlo"
    spot=100.0,             # Current underlying price
    strike=100.0,           # Strike price
    vol=0.2,                # Annualized volatility (decimal)
    rate=0.05,              # Risk-free rate (decimal)
    expiry=1.0,             # Time to expiry in years
    option_type="call",     # "call" or "put"
    dividend=0.0,           # Continuous dividend yield
    exercise_style="european",  # "european" or "american"
    steps=100,              # Tree steps (binomial/trinomial)
    num_paths=100000,       # MC simulation paths
    seed=42,                # MC random seed
)

print(result.price)    # float
print(result.greeks)   # dict[str, float]
print(result.tree)     # list[list[float]] (lattice models)
print(result.model)    # str
```

### `quantiv.analytics.GreeksAnalyzer`

Computes Greeks over parameter ranges for visualization.

### `quantiv.analytics.IVSurfaceBuilder`

Builds implied volatility surfaces over strike × expiry grids.

### `quantiv.analytics.StrategyBuilder`

Constructs multi-leg option strategies and computes P&L profiles.
