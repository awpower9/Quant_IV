"""
greeks_page.py — Greeks visualization page layout.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from dashboard.components.parameter_panel import create_parameter_panel


def greeks_layout() -> html.Div:
    """Create the Greeks page layout."""
    return html.Div([
        html.H2("Greeks Dashboard", className="mb-4"),

        dbc.Row([
            dbc.Col([
                create_parameter_panel(id_prefix="greeks", show_model=False),
            ], md=3),

            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(label="Delta", tab_id="delta-tab"),
                    dbc.Tab(label="Gamma", tab_id="gamma-tab"),
                    dbc.Tab(label="Vega", tab_id="vega-tab"),
                    dbc.Tab(label="Theta", tab_id="theta-tab"),
                    dbc.Tab(label="Rho", tab_id="rho-tab"),
                ], id="greeks-tabs", active_tab="delta-tab"),
                dcc.Graph(id="greeks-chart"),
            ], md=9),
        ]),

        # ── Bottom: Greek Description ────────────────────────────────
        html.Hr(className="my-5"),
        dbc.Row([
            dbc.Col([
                html.Div(id="greeks-description-output")
            ], md=12)
        ]),
    ])
