"""
result_card.py — Result display card component.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_result_card(card_id: str = "result-card") -> dbc.Card:
    """Create a results display card."""
    return dbc.Card(
        dbc.CardBody([
            html.H4("Pricing Result", className="card-title"),
            html.Hr(),
            html.Div(id=f"{card_id}-content", children=[
                html.P("Adjust parameters and click Price to see results."),
            ]),
        ]),
        className="shadow-sm",
    )
