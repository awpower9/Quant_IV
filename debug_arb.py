import json
import plotly.graph_objects as go
from dash import html
from quantiv.pricing.pricer import Pricer
from scripts.calculate_iv import implied_volatility_educational

# Simulate the exact logic of the callback when arbitrage fails
target_price = 1.0  # Extremely low price for ITM call
spot = 100.0
strike = 50.0       # Intrinsic value is ~50
expiry = 1.0
rate = 0.05
is_call = True
option_type = "call"

try:
    iv, steps = implied_volatility_educational(target_price, spot, strike, expiry, rate, is_call)
    print("IV succeeded?")
except Exception as e:
    iv = 0.20
    iv_text = html.Span(f"IV Error (Using 20% Fallback Vol)", className="text-warning")
    print(f"Caught IV error: {e}")

pricer = Pricer()
models = ["bsm", "binomial", "trinomial", "monte_carlo"]
rows = []
for m in models:
    try:
        res = pricer.price(m, spot, strike, iv, rate, expiry, option_type, steps=100, num_paths=5000)
        diff = res.price - target_price
        color = "text-success" if abs(diff) < 0.1 else "text-warning"
        rows.append(html.Tr([
            html.Td(m.replace("_", " ").title()),
            html.Td(f"${res.price:.2f}"),
            html.Td(f"${diff:+.2f}", className=color)
        ]))
        print(f"Priced {m}: {res.price}")
    except Exception as e:
        print(f"Failed pricing {m}: {e}")
        rows.append(html.Tr([html.Td(m.replace("_", " ").title()), html.Td("Error"), html.Td("-")]))

import dash_bootstrap_components as dbc
comp_table = dbc.Table([
    html.Thead(html.Tr([html.Th("Model"), html.Th("Theoretical Price"), html.Th("Diff vs Market")])),
    html.Tbody(rows)
], bordered=True, color="dark", hover=True, size="sm")

print("Table successfully generated.")
