"""
surface_callbacks.py — Callbacks for the 3D volatility surface page.
"""

import dash
from dash import Input, Output, State
import numpy as np
import plotly.graph_objects as go

from quantiv.analytics import IVSurfaceBuilder

builder = IVSurfaceBuilder()


@dash.callback(
    Output("surface-3d-chart", "figure"),
    Input("surface-build-btn", "n_clicks"),
    State("surface-spot", "value"),
    State("surface-rate", "value"),
    State("surface-strike-range", "value"),
    State("surface-expiry-range", "value"),
    prevent_initial_call=True,
)
def build_surface(n_clicks, spot, rate_pct, strike_range, expiry_range):
    """Build and display the 3D implied volatility surface."""
    try:
        rate = rate_pct / 100.0
        strikes = np.linspace(strike_range[0], strike_range[1], 20)
        expiries = np.linspace(expiry_range[0], expiry_range[1], 15)

        df = builder.build_surface(
            spot=spot, rate=rate,
            strikes=strikes.tolist(),
            expiries=expiries.tolist(),
        )

        # Pivot to grid for surface plot
        pivot = df.pivot(index="expiry", columns="strike", values="iv")

        fig = go.Figure(data=[go.Surface(
            z=pivot.values * 100,  # convert to percentage
            x=pivot.columns,       # strikes
            y=pivot.index,         # expiries
            colorscale="Viridis",
            colorbar=dict(title="IV (%)"),
        )])

        fig.update_layout(
            title="Implied Volatility Surface",
            scene=dict(
                xaxis_title="Strike ($)",
                yaxis_title="Expiry (years)",
                zaxis_title="Implied Vol (%)",
            ),
            template="plotly_dark",
            height=600,
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error: {e}", showarrow=False)
        fig.update_layout(template="plotly_dark")
        return fig
