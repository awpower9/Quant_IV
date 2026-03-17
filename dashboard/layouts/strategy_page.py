"""
strategy_page.py — Option strategy builder page layout.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def strategy_layout() -> html.Div:
    """Create the strategy builder page layout."""
    return html.Div([
        html.H2("Option Strategy Builder", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.Label("Strategy"),
                    dcc.Dropdown(
                        id="strategy-selector",
                        options=[
                            {"label": "Long Straddle", "value": "straddle"},
                            {"label": "Bull Call Spread", "value": "bull_call"},
                            {"label": "Bear Put Spread", "value": "bear_put"},
                            {"label": "Iron Condor", "value": "iron_condor"},
                            {"label": "Custom", "value": "custom"},
                        ],
                        value="straddle",
                        clearable=False,
                    ),
                    html.Hr(),
                    html.Label("Spot Price"),
                    dcc.Slider(id="strategy-spot", min=50, max=200,
                               value=100, step=1, marks=None,
                               tooltip={"placement": "bottom"}),
                    html.Label("Strike 1"),
                    dcc.Slider(id="strategy-strike1", min=50, max=200,
                               value=100, step=1, marks=None,
                               tooltip={"placement": "bottom"}),
                    html.Label("Strike 2"),
                    dcc.Slider(id="strategy-strike2", min=50, max=200,
                               value=110, step=1, marks=None,
                               tooltip={"placement": "bottom"}),
                    html.Label("Expiry (years)"),
                    dcc.Slider(id="strategy-expiry", min=0.1, max=3.0,
                               value=0.5, step=0.1, marks=None,
                               tooltip={"placement": "bottom"}),
                ]), className="shadow-sm"),
            ], md=3),

            dbc.Col([
                dcc.Graph(id="strategy-payoff-chart"),
                html.Div(id="strategy-summary", className="mt-3"),
            ], md=9),
        ]),

        # ── Bottom: Strategy Description ──────────────────────────────
        html.Hr(className="my-5"),
        dbc.Row([
            dbc.Col([
                html.Div(id="strategy-description-output")
            ], md=12)
        ]),
    ])
