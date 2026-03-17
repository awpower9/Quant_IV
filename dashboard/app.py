"""
app.py — Dash application entry point.

Registers all pages, callbacks, and starts the server.
"""

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

from dashboard.layouts.home import home_layout
from dashboard.layouts.pricer_page import pricer_layout
from dashboard.layouts.greeks_page import greeks_layout
from dashboard.layouts.surface_page import surface_layout
from dashboard.layouts.strategy_page import strategy_layout
from dashboard.layouts.live_page import live_layout
from dashboard.components.navbar import create_navbar

# ── App Initialization ───────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
    title="Quantiv — Options Pricing Platform",
    meta_tags=[
        {"name": "description",
         "content": "Quantitative options pricing with C++ performance"},
        {"name": "viewport",
         "content": "width=device-width, initial-scale=1"},
    ],
)

server = app.server

# ── Layout ───────────────────────────────────────────────────────────────────

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    create_navbar(),
    html.Div(id="page-content", className="container-fluid mt-4"),
])


# ── Page Routing ─────────────────────────────────────────────────────────────

from dashboard.layouts.models_menu import models_menu_layout

from dashboard.layouts.intro_page import intro_layout

@app.callback(
    dash.Output("page-content", "children"),
    dash.Input("url", "pathname"),
    dash.Input("url", "search"),
)
def display_page(pathname: str, search: str = ""):
    """Route to the correct page layout."""
    if pathname == "/intro":
        return intro_layout()
    elif pathname == "/pricer":
        model = "bsm"
        if search and "?model=" in search:
            model = search.split("?model=")[1].split("&")[0]
        return pricer_layout(model=model)
    elif pathname == "/models":
        return models_menu_layout()
    elif pathname == "/greeks":
        return greeks_layout()
    elif pathname == "/surface":
        return surface_layout()
    elif pathname == "/strategy":
        return strategy_layout()
    elif pathname == "/live":
        return live_layout()
    else:
        return home_layout()


# ── Register Callbacks ──────────────────────────────────────────────────────
# Importing the callback modules registers them with the app.

import dashboard.callbacks.pricer_callbacks   # noqa: F401, E402
import dashboard.callbacks.greeks_callbacks   # noqa: F401, E402
import dashboard.callbacks.surface_callbacks  # noqa: F401, E402
import dashboard.callbacks.strategy_callbacks # noqa: F401, E402
import dashboard.callbacks.live_callbacks     # noqa: F401, E402


if __name__ == "__main__":
    app.run(debug=True, port=8050)
