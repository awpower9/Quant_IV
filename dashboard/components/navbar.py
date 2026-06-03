"""
navbar.py — Navigation bar component.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_navbar() -> dbc.Navbar:
    """Create the main navigation bar."""
    return dbc.Navbar(
        dbc.Container([
            html.A(
                html.Img(src="/assets/logo1.png", style={"height": "60px", "width": "200px"}, className="logo_png"),
                href="/",
                style={"textDecoration": "none"}
            ),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Intro", href="/intro")),
                dbc.NavItem(dbc.NavLink("Live", href="/live")),
                dbc.NavItem(dbc.NavLink("Compare", href="/compare")),
                dbc.NavItem(dbc.NavLink("Models", href="/models")),
                dbc.NavItem(dbc.NavLink("Compare Models", href="/comparison")),
                dbc.NavItem(dbc.NavLink("Greeks", href="/greeks")),
                dbc.NavItem(dbc.NavLink("Vol Surface", href="/surface")),
                dbc.NavItem(dbc.NavLink("Strategy", href="/strategy")),
                
                # --- NEW PAGES ADDED HERE ---
                dbc.NavItem(dbc.NavLink("Plans", href="/subscription", style={'color': '#fbbf24', 'fontWeight': 'bold'})),
                dbc.NavItem(dbc.NavLink("Profile", href="/portfolio",style={'margin-left': '10vw',"margin-right":"10px"})),
                
            ], navbar=True,style={"marginLeft": "10vw"}),
        ], fluid=True,style={"fontSize":"20px"}),
        dark=True,
        sticky="top",
        className="mt-4 mx-3 glass-nav border-radius-60px",
    )