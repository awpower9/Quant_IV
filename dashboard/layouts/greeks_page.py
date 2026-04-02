"""
greeks_page.py — Greeks visualization page layout.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from dashboard.components.parameter_panel import create_parameter_panel


def greeks_layout() -> html.Div:
    return html.Div(className="container-fluid p-4 animate-page", children=[
        html.H2("Risk Sensitivity Terminal", className="text-neon mb-4 fw-bold"),
        dbc.Row([
            dbc.Col([
                html.Div(className="glass-card p-4", children=[
                    create_parameter_panel(id_prefix="greeks", show_model=False),
                    dbc.Button("Calculate Greek", id="btn-calculate-greeks", className="btn-calculate w-100 mt-4 py-3")
                ]),
            ], md=3),
            dbc.Col([
                html.Div(className="glass-card p-3", children=[
                    dbc.Tabs([
                        dbc.Tab(label="Delta", tab_id="delta-tab"),
                        dbc.Tab(label="Gamma", tab_id="gamma-tab"),
                        dbc.Tab(label="Vega", tab_id="vega-tab"),
                        dbc.Tab(label="Theta", tab_id="theta-tab"),
                        dbc.Tab(label="Rho", tab_id="rho-tab"),
                    ], id="greeks-tabs", active_tab="delta-tab", className="mb-3 custom-tabs"),
                    dcc.Graph(id="greeks-chart", config={'displayModeBar': False}),
                ]),
            ], md=9),
        ]),

        # ── Greeks Educational Content ──
        html.Hr(className="my-4"),
        dbc.Row([
            dbc.Col(md=12, children=[
                html.Div(className="glass-card p-4", children=[
                    html.H4("🏛️ The Greek Explained", className="text-info fw-bold mb-3"),
                    html.Div(id="greek-description-output")
                ])
            ])
        ])
    ])
