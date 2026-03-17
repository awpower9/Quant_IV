"""
live_page.py — Live market data pricing page layout.

Displays real-time spot prices, Greeks, and a live price time series,
auto-refreshing via dcc.Interval.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def live_layout() -> html.Div:
    """Create the live pricing page layout."""
    return html.Div([
        html.H2("Live Market Pricing", className="mb-4"),

        # ── Symbol Input + Status ────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText("Symbol"),
                    dbc.Input(
                        id="live-symbol-input",
                        value="AAPL",
                        placeholder="Enter ticker...",
                        type="text",
                    ),
                    dbc.Button(
                        "Track", id="live-track-btn",
                        color="primary", n_clicks=0,
                    ),
                ]),
            ], md=5),
            dbc.Col([
                html.Div(id="live-status-badge", className="mt-2"),
            ], md=3),
            dbc.Col([
                dbc.Checklist(
                    id="live-auto-refresh-toggle",
                    options=[{"label": "  Auto-refresh (5s)", "value": "on"}],
                    value=["on"],
                    switch=True,
                ),
            ], md=4),
        ], className="mb-4"),

        # ── Auto-refresh interval ────────────────────────────────────────
        dcc.Interval(
            id="live-interval",
            interval=5000,  # 5 seconds
            n_intervals=0,
            disabled=False,
        ),

        # ── Main content ─────────────────────────────────────────────────
        dbc.Row([
            # ── Left: Live quote card ────────────────────────────────────
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Live Quote", className="card-title"),
                    html.Hr(),
                    html.Div(id="live-quote-content", children=[
                        html.P("Click 'Track' to start fetching live data."),
                    ]),
                ]), className="shadow-sm mb-3"),

                dbc.Card(dbc.CardBody([
                    html.H5("Live Greeks (BSM)", className="card-title"),
                    html.Hr(),
                    html.Label("Strike Price"),
                    dcc.Slider(
                        id="live-strike", min=50, max=300,
                        value=175, step=1, marks=None,
                        tooltip={"placement": "bottom"},
                    ),
                    html.Label("Expiry (years)", className="mt-2"),
                    dcc.Slider(
                        id="live-expiry", min=0.1, max=3.0,
                        value=0.5, step=0.1, marks=None,
                        tooltip={"placement": "bottom"},
                    ),
                    html.Label("Option Type", className="mt-2"),
                    dbc.RadioItems(
                        id="live-option-type",
                        options=[
                            {"label": "Call", "value": "call"},
                            {"label": "Put", "value": "put"},
                        ],
                        value="call",
                        inline=True,
                    ),
                    html.Hr(),
                    html.Div(id="live-greeks-content"),
                ]), className="shadow-sm"),
            ], md=4),

            # ── Right: Live charts ───────────────────────────────────────
            dbc.Col([
                dcc.Graph(id="live-price-chart"),
                dcc.Graph(id="live-greeks-chart"),

                # Hidden store for price history
                dcc.Store(id="live-price-history", data=[]),
            ], md=8),
        ]),
    ])
