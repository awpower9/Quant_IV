"""
parameter_panel.py — Reusable input slider/control panel component.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_parameter_panel(
    id_prefix: str = "param",
    show_model: bool = True,
    show_steps: bool = True,
    default_model: str = "bsm",
) -> dbc.Card:
    """
    Create a reusable parameter input panel.

    Args:
        id_prefix:  Prefix for component IDs to avoid conflicts.
        show_model: Whether to show the model selector.
        show_steps: Whether to show tree steps / MC paths inputs.
        default_model: Which model to pre-select.
    """
    children = []

    if show_model:
        children.append(dbc.Row([
            dbc.Col([
                html.Label("Model"),
                dcc.Dropdown(
                    id=f"{id_prefix}-model",
                    options=[
                        {"label": "Black-Scholes", "value": "bsm"},
                        {"label": "Binomial Tree", "value": "binomial"},
                        {"label": "Trinomial Tree", "value": "trinomial"},
                        {"label": "Monte Carlo", "value": "monte_carlo"},
                        {"label": "Heston (Pro) 🔒", "value": "heston"},
                        {"label": "Merton (Pro) 🔒", "value": "merton"},
                    ],
                    value=default_model,
                    clearable=False,
                ),
            ]),
        ], className="mb-3"))

    sliders = [
        ("Spot Price", f"{id_prefix}-spot", 50, 200, 100, 1),
        ("Strike Price", f"{id_prefix}-strike", 50, 200, 100, 1),
        ("Volatility (%)", f"{id_prefix}-vol", 5, 100, 20, 1),
        ("Risk-Free Rate (%)", f"{id_prefix}-rate", 0, 20, 5, 0.5),
        ("Time to Expiry (years)", f"{id_prefix}-expiry", 0.1, 5.0, 1.0, 0.1),
    ]

    for label, slider_id, min_val, max_val, value, step in sliders:
        children.append(dbc.Row([
            dbc.Col([
                html.Label(f"{label}: ", id=f"{slider_id}-label"),
                html.Span(str(value), id=f"{slider_id}-value",
                          className="fw-bold ms-1"),
                dcc.Slider(
                    id=slider_id,
                    min=min_val, max=max_val, value=value, step=step,
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ]),
        ], className="mb-2"))

    children.append(dbc.Row([
        dbc.Col([
            html.Label("Option Type"),
            dbc.RadioItems(
                id=f"{id_prefix}-option-type",
                options=[
                    {"label": "Call", "value": "call"},
                    {"label": "Put", "value": "put"},
                ],
                value="call",
                inline=True,
            ),
        ]),
    ], className="mb-3"))

    # Container for dynamically injected Pro sliders (Heston/Merton)
    children.append(html.Div(id="advanced-sliders-container"))

    return dbc.Card(dbc.CardBody(children), className="shadow-sm")
