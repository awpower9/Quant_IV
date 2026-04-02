"""
model_compare_page.py — Multi-model live pricing comparison page.

Users select multiple pricing models (BSM, Binomial, Trinomial, Monte Carlo)
and see their option prices overlaid on a shared time-series chart,
updated in real time from live market data.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


# ── Model definitions ────────────────────────────────────────────────────────

MODELS = [
    {"label": "Black-Scholes", "value": "bsm"},
    {"label": "Binomial (CRR)", "value": "binomial"},
    {"label": "Trinomial", "value": "trinomial"},
    {"label": "Monte Carlo", "value": "monte_carlo"},
]

MODEL_COLORS = {
    "bsm":         "#00d4ff",   # cyan
    "binomial":    "#f59e0b",   # amber
    "trinomial":   "#a855f7",   # purple
    "monte_carlo": "#22c55e",   # green
}

MODEL_LABELS = {
    "bsm":         "Black-Scholes",
    "binomial":    "Binomial (CRR)",
    "trinomial":   "Trinomial",
    "monte_carlo": "Monte Carlo",
}


def model_compare_layout() -> html.Div:
    """Build the model comparison page layout."""
    return html.Div([
        html.H2("Multi-Model Live Pricing", className="mc-page-title"),
        html.P(
            "Compare option prices across models using real-time market data.",
            className="text-muted mb-4",
        ),

        # ── Row 1: Symbol input + status + auto-refresh ──────────────────
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText("Symbol"),
                    dbc.Input(
                        id="mc-symbol-input",
                        value="AAPL",
                        placeholder="Enter ticker...",
                        type="text",
                        className="mc-input",
                    ),
                    dbc.Button(
                        "Track", id="mc-track-btn",
                        className="mc-btn-track", n_clicks=0,
                    ),
                ]),
            ], md=5),
            dbc.Col([
                html.Div(id="mc-status-badge", className="mt-2"),
            ], md=3),
            dbc.Col([
                dbc.Checklist(
                    id="mc-auto-refresh-toggle",
                    options=[{"label": "  Auto-refresh (5s)", "value": "on"}],
                    value=["on"],
                    switch=True,
                ),
            ], md=4),
        ], className="mb-4"),

        # ── Interval timer ───────────────────────────────────────────────
        dcc.Interval(
            id="mc-interval",
            interval=5000,
            n_intervals=0,
            disabled=False,
        ),

        # ── Row 2: Controls ──────────────────────────────────────────────
        dbc.Row([
            # ── Model selector ───────────────────────────────────────────
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Select Models", className="mc-card-title"),
                    html.Hr(className="mc-hr"),
                    dbc.Checklist(
                        id="mc-model-selector",
                        options=MODELS,
                        value=["bsm", "binomial", "trinomial", "monte_carlo"],
                        className="mc-model-checklist",
                    ),
                ]), className="mc-card"),
            ], md=3),

            # ── Option parameters ────────────────────────────────────────
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Option Parameters", className="mc-card-title"),
                    html.Hr(className="mc-hr"),

                    html.Label("Strike Price ($)", className="mc-label"),
                    dcc.Slider(
                        id="mc-strike", min=50, max=300,
                        value=175, step=1, marks=None,
                        tooltip={"placement": "bottom"},
                    ),

                    html.Label("Expiry (years)", className="mc-label mt-2"),
                    dcc.Slider(
                        id="mc-expiry", min=0.1, max=3.0,
                        value=0.5, step=0.1, marks=None,
                        tooltip={"placement": "bottom"},
                    ),

                    html.Label("Option Type", className="mc-label mt-2"),
                    dbc.RadioItems(
                        id="mc-option-type",
                        options=[
                            {"label": "Call", "value": "call"},
                            {"label": "Put", "value": "put"},
                        ],
                        value="call",
                        inline=True,
                        className="mc-radio",
                    ),
                ]), className="mc-card"),
            ], md=4),

            # ── Model-specific parameters ────────────────────────────────
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Model Parameters", className="mc-card-title"),
                    html.Hr(className="mc-hr"),

                    html.Label("Tree Steps (Binomial/Trinomial)",
                               className="mc-label"),
                    dcc.Slider(
                        id="mc-tree-steps", min=10, max=500,
                        value=100, step=10, marks=None,
                        tooltip={"placement": "bottom"},
                    ),

                    html.Label("MC Paths", className="mc-label mt-2"),
                    dcc.Slider(
                        id="mc-num-paths",
                        min=10000, max=500000,
                        value=100000, step=10000,
                        marks=None,
                        tooltip={"placement": "bottom"},
                    ),

                    html.Label("MC Seed", className="mc-label mt-2"),
                    dbc.Input(
                        id="mc-seed", type="number",
                        value=42, min=1, max=999999,
                        className="mc-input",
                    ),
                ]), className="mc-card"),
            ], md=5),
        ], className="mb-4"),

        # ── Row 3: Live quote + comparison table ─────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Live Quote", className="mc-card-title"),
                    html.Hr(className="mc-hr"),
                    html.Div(id="mc-quote-content", children=[
                        html.P("Click 'Track' to start fetching live data."),
                    ]),
                ]), className="mc-card"),
            ], md=4),

            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Model Price Comparison", className="mc-card-title"),
                    html.Hr(className="mc-hr"),
                    html.Div(id="mc-comparison-table"),
                ]), className="mc-card"),
            ], md=8),
        ], className="mb-4"),

        # ── Row 4: Charts ────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Option Price — Model Overlay",
                             className="mc-card-title"),
                    dcc.Graph(id="mc-price-overlay-chart"),
                ]), className="mc-card"),
            ], md=12),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Spot Price", className="mc-card-title"),
                    dcc.Graph(id="mc-spot-chart"),
                ]), className="mc-card"),
            ], md=6),

            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Price Spread (Model − BSM)",
                             className="mc-card-title"),
                    dcc.Graph(id="mc-spread-chart"),
                ]), className="mc-card"),
            ], md=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Price vs Strike — All Models",
                             className="mc-card-title"),
                    dcc.Graph(id="mc-strike-curve-chart"),
                ]), className="mc-card"),
            ], md=12),
        ], className="mb-4"),

        # ── Hidden stores ────────────────────────────────────────────────
        dcc.Store(id="mc-model-history", data={}),
        dcc.Store(id="mc-spot-history", data=[]),
    ])
