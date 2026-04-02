"""
surface_page.py — 3D Volatility Surface page layout.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def surface_layout() -> html.Div:
    """Create the volatility surface page layout."""
    return html.Div([
        html.H2("Implied Volatility Surface", className="text-neon mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.Label("Spot Price"),
                    dcc.Input(id="surface-spot", type="number",
                              value=100, className="form-control mb-3"),
                    html.Label("Risk-Free Rate (%)"),
                    dcc.Input(id="surface-rate", type="number",
                              value=5, step=0.5, className="form-control mb-3"),
                    html.Label("Strike Range"),
                    dcc.RangeSlider(id="surface-strike-range",
                                    min=50, max=200, value=[70, 130],
                                    marks=None, tooltip={"placement": "bottom"}),
                    html.Label("Expiry Range (years)", className="mt-3"),
                    dcc.RangeSlider(id="surface-expiry-range",
                                    min=0.1, max=3.0, step=0.1,
                                    value=[0.1, 2.0],
                                    marks=None, tooltip={"placement": "bottom"}),
                    dbc.Button("Build Surface", id="surface-build-btn",
                               color="primary", className="mt-3 w-100"),
                ]), className="glass-card"),
            ], md=3),

            dbc.Col([
                dcc.Graph(
                   id="surface-3d-chart", 
                   style={"height": "600px"}, 
                    responsive=True,className="glass-card"
                ),
            ], md=9),
        ]),

        # ── Bottom: Surface Description ──────────────────────────────
        html.Hr(className="my-5"),
        dbc.Row([
            dbc.Col([
                dcc.Markdown(r"""
### 🌊 Volatility Surface

The **Implied Volatility (IV) Surface** is a 3-dimensional plot that physically visualizes how expensive "fear" is across different **Strikes** (x-axis) and **Expiries** (y-axis). It perfectly proves that the real stock market is driven by human emotion, destroying the old Black-Scholes assumption that risk is totally constant!

**Key Intuitions:**
* **Volatility Smile/Smirk (The Crash Premium):** In a perfectly calm math world, a $150 strike and $100 strike have the exact same volatility. But in the real world, investors are absolutely terrified of sudden 2008-style market crashes. Because of this deep panic, they happily overpay massive premiums for far Out-Of-The-Money Puts (crash insurance). When you beautifully plot this fear out, it visually graphs as a heavy, lopsided "smirk" skewed entirely towards lower prices!
* **Term Structure (The Time Curve):** Volatility also violently changes depending on how far out into the future you look. If a company is reporting high-stakes earnings tomorrow, the short-term 1-week volatility explodes! But if you look 2 full years safely into the future, things smooth back out to a calm historical average.

**Mathematical Representation:**
The surface $\Sigma(K, T)$ structurally represents the implied volatility such that the Black-Scholes formula $C_{BS}$ perfectly matches the true observable market price $C_{Mkt}$:

$$
C_{BS}(S, K, T, r, \Sigma(K, T)) = C_{Mkt}
$$

* This 3D grid is fundamentally required by advanced local volatility models (like Dupire's formula).
* It correctly prices exotic derivatives that strictly rely on the entire probability distribution of the asset, not just an isolated volatility scalar.
                """, mathjax=True)
            ], md=12)
        ]),
    ])
