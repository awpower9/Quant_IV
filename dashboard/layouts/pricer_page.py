"""
pricer_page.py — Model pricing page layout.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from dashboard.components.parameter_panel import create_parameter_panel


def pricer_layout(model: str = "bsm") -> html.Div:
    """Create the pricer page layout."""
    return html.Div([
        html.H2("Option Pricer", className="mb-4"),

        dbc.Row([
            # ── Left: Parameters ─────────────────────────────────────────
            dbc.Col([
                create_parameter_panel(id_prefix="pricer", default_model=model),
            ], md=4),

            # ── Right: Results ───────────────────────────────────────────
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H4("Price", className="text-center"),
                    html.H2(id="pricer-price-output",
                            className="text-center text-success"),
                    html.Hr(),
                    html.Div(id="pricer-greeks-output"),
                ]), className="shadow-sm mb-3"),

                dcc.Graph(id="pricer-convergence-chart"),
            ], md=8),
        ]),

        # ── Bottom: Model Description ────────────────────────────────
        html.Hr(className="my-5"),
        dbc.Row([
            dbc.Col([
                html.Div(id="model-description-output")
            ], md=12)
        ]),
    ])
