"""
navbar.py — Navigation bar component.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_navbar() -> dbc.Navbar:
    """Create the main navigation bar."""
    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("⚡ Quantiv", href="/", className="ms-2"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Intro", href="/intro")),
                dbc.NavItem(dbc.NavLink("Live", href="/live")),
                dbc.NavItem(dbc.NavLink("Models", href="/models")),
                dbc.NavItem(dbc.NavLink("Greeks", href="/greeks")),
                dbc.NavItem(dbc.NavLink("Vol Surface", href="/surface")),
                dbc.NavItem(dbc.NavLink("Strategy", href="/strategy")),
            ], navbar=True),
        ], fluid=True),
        color="dark",
        dark=True,
        sticky="top",
    )
