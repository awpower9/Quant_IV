"""
surface_callbacks.py — Callbacks for the 3D volatility surface page.
"""

import dash
from dash import Input, Output, State
import numpy as np
import plotly.graph_objects as go

from quantiv.analytics.iv_surface import IVSurfaceBuilder
from quantiv.portfolio_engine import QuantivPortfolioEngine

builder = IVSurfaceBuilder()
engine = QuantivPortfolioEngine()


@dash.callback(
    Output("surface-3d-chart", "figure"),
    Input("surface-build-btn", "n_clicks"),
    State("surface-spot", "value"),
    State("surface-rate", "value"),
    State("surface-strike-range", "value"),
    State("surface-expiry-range", "value"),
    State("session-user", "data"), # ---> NEW: Session
    prevent_initial_call=True,
)
def build_surface(n_clicks, spot, rate_pct, strike_range, expiry_range, username):
    """Build and display the 3D implied volatility surface."""
    
    fig = go.Figure()
    
    # Login & Credit Checks
    if not username:
        fig.add_annotation(text="🔒 Please log in via the Portfolio tab to view 3D Surface.", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#ff4f6d"))
        fig.update_layout(template="plotly_dark", height=600, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig
        
    if not engine.use_advanced_feature(username):
        fig.add_annotation(text="⚡ Out of credits! Please upgrade your plan to view 3D Surface.", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#f5c542"))
        fig.update_layout(template="plotly_dark", height=600, xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig

    try:
        rate = rate_pct / 100.0
        strikes = np.linspace(strike_range[0], strike_range[1], 20)
        expiries = np.linspace(expiry_range[0], expiry_range[1], 15)

        df = builder.build_surface(
            spot=spot, rate=rate,
            strikes=strikes.tolist(),
            expiries=expiries.tolist(),
        )

        pivot = df.pivot(index="expiry", columns="strike", values="iv")

        fig.add_trace(go.Surface(
            z=pivot.values * 100, x=pivot.columns, y=pivot.index,
            colorscale="Viridis", colorbar=dict(title="IV (%)"),
        ))

        fig.update_layout(
            title="Implied Volatility Surface",
            scene=dict(xaxis_title="Strike ($)", yaxis_title="Expiry (years)", zaxis_title="Implied Vol (%)"),
            template="plotly_dark", height=600,
        )
        return fig

    except Exception as e:
        fig.add_annotation(text=f"Error: {e}", showarrow=False)
        fig.update_layout(template="plotly_dark")
        return fig
