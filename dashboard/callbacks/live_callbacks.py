"""
live_callbacks.py — Callbacks for the live market data page.

Connects dcc.Interval → LiveMarketService → Pricer → UI updates.
Never calls the market API or _quantiv_engine directly.
"""

import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
from datetime import datetime

from quantiv.data.live_service import LiveMarketService, DataStatus
from quantiv.pricing import Pricer
from quantiv.utils.formatting import format_price

# ── Module-level singletons ──────────────────────────────────────────────────

_service = LiveMarketService()
_pricer = Pricer()


# ── Toggle auto-refresh ─────────────────────────────────────────────────────

@dash.callback(
    Output("live-interval", "disabled"),
    Input("live-auto-refresh-toggle", "value"),
)
def toggle_auto_refresh(toggle_value):
    """Enable/disable the dcc.Interval based on the toggle switch."""
    return "on" not in (toggle_value or [])


# ── Main interval-driven refresh (single callback for all live outputs) ─────

@dash.callback(
    Output("live-quote-content", "children"),
    Output("live-greeks-content", "children"),
    Output("live-price-chart", "figure"),
    Output("live-greeks-chart", "figure"),
    Output("live-status-badge", "children"),
    Output("live-price-history", "data"),
    Input("live-interval", "n_intervals"),
    Input("live-track-btn", "n_clicks"),
    State("live-symbol-input", "value"),
    State("live-strike", "value"),
    State("live-expiry", "value"),
    State("live-option-type", "value"),
    State("live-price-history", "data"),
)
def refresh_live_data(n_intervals, n_clicks, symbol, strike, expiry,
                      option_type, price_history):
    """
    Main refresh callback — triggered every 5s by dcc.Interval
    or when the Track button is clicked.

    Flow: LiveMarketService → Pricer → format results → update UI.
    """
    if not symbol or not symbol.strip():
        empty_fig = _empty_figure("Enter a symbol and click Track")
        return (
            html.P("Enter a symbol and click 'Track' to start."),
            html.P("—"),
            empty_fig, empty_fig,
            _status_badge(DataStatus.OFFLINE, "No symbol"),
            [],
        )

    symbol = symbol.strip().upper()

    # If Track was clicked or not yet tracking, start the service
    if symbol not in _service.tracked_symbols:
        triggered = dash.callback_context.triggered
        is_track_click = any(
            t.get("prop_id", "") == "live-track-btn.n_clicks"
            for t in triggered
        ) if triggered else False

        if not is_track_click and n_clicks == 0:
            # Don't auto-start until user clicks Track
            empty_fig = _empty_figure("Click Track to begin")
            return (
                html.P("Click 'Track' to start live data for this symbol."),
                html.P("—"),
                empty_fig, empty_fig,
                _status_badge(DataStatus.OFFLINE, "Not tracking"),
                price_history or [],
            )

        try:
            _service.start(symbol)
        except Exception:
            pass

    try:
        # ── Fetch live data through the service ──────────────────────
        quote = _service.get_live_quote(symbol)
        status = _service.status

        # ── Price the option using the C++ engine ────────────────────
        result = _pricer.price(
            model="bsm",
            spot=quote.spot,
            strike=strike,
            vol=quote.vol,
            rate=quote.rate,
            expiry=expiry,
            option_type=option_type,
        )

        # ── Format quote card ────────────────────────────────────────
        quote_div = html.Div([
            html.H3(f"{symbol}", className="text-primary"),
            html.H2(format_price(quote.spot, 2), className="text-success"),
            html.P(f"Vol: {quote.vol:.1%}  |  Rate: {quote.rate:.2%}",
                   className="text-muted"),
            html.P(
                f"Option Price ({option_type.capitalize()}): "
                f"{format_price(result.price)}",
                className="fw-bold",
            ),
            html.Small(
                f"Updated: {datetime.now().strftime('%H:%M:%S')}",
                className="text-muted",
            ),
        ])

        # ── Format Greeks table ──────────────────────────────────────
        greeks_div = html.Div([
            html.Table([
                html.Thead(html.Tr([html.Th("Greek"), html.Th("Value")])),
                html.Tbody([
                    html.Tr([
                        html.Td(name.capitalize()),
                        html.Td(f"{val:.6f}"),
                    ])
                    for name, val in result.greeks.items()
                ]),
            ], className="table table-sm table-dark"),
        ]) if result.greeks else html.P("No Greeks available.")

        # ── Update / Seed price history ──────────────────────────────
        
        # Check if we need to seed history (Track button clicked OR history empty)
        triggered = dash.callback_context.triggered
        is_track_click = any(
            t.get("prop_id", "") == "live-track-btn.n_clicks"
            for t in triggered
        ) if triggered else False

        if is_track_click or not price_history:
            price_history = []
            try:
                # Fetch 500 historical points
                hist_points = _service.get_live_intraday_history(symbol, points=500)
                for pt in hist_points:
                    hist_spot = pt["spot"]
                    # Evaluate historical option price using constant vol/rate
                    hist_res = _pricer.price(
                        model="bsm",
                        spot=hist_spot,
                        strike=strike,
                        vol=quote.vol,
                        rate=quote.rate,
                        expiry=expiry,
                        option_type=option_type,
                    )
                    price_history.append({
                        "time": pt["time"],
                        "spot": hist_spot,
                        "option_price": hist_res.price,
                    })
            except Exception as e:
                # If historical fetch fails, just start empty and we append live
                pass
            
        # Append the new live tick
        price_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "spot": quote.spot,
            "option_price": result.price,
        })
        
        # Keep last 500 data points globally (supports both history and live polling)
        price_history = price_history[-500:]

        # ── Price time series chart ──────────────────────────────────
        times = [p["time"] for p in price_history]
        spots = [p["spot"] for p in price_history]

        # Calculate dynamic y-axis range to prevent 'tozeroy' fill from flattening the graph
        min_spot = min(spots) if spots else 0
        max_spot = max(spots) if spots else 0
        y_padding = (max_spot - min_spot) * 0.2
        if y_padding == 0:
            y_padding = min_spot * 0.005
            
        y_min = max(0, min_spot - y_padding)
        y_max = max_spot + y_padding

        # Set up categorical tick marks so we don't display the huge dates on every tick, 
        # but the underlying strings stay unique to avoid looping.
        tick_indices = list(range(0, len(times), max(1, len(times)//15)))
        tick_vals = [times[i] for i in tick_indices]
        tick_text = [t[11:16] for t in tick_vals] # extract just HH:MM

        price_fig = go.Figure()
        
        # Add a subtle gradient fill below the line
        price_fig.add_trace(go.Scatter(
            x=times, y=spots,
            mode="lines",
            name="Spot Price",
            line=dict(color="#00E676", width=2.5, shape="spline", smoothing=1.3),
            fill="tozeroy",
            fillcolor="rgba(0, 230, 118, 0.05)",
            hovertemplate="Time: %{x}<br>Spot: $%{y:.2f}<extra></extra>",
        ))

        # Modern, minimalistic layout
        price_fig.update_layout(
            title=dict(text=f"{symbol} Live Spot", font=dict(size=16, color="#E0E0E0")),
            xaxis=dict(
                type="category",
                categoryorder="trace",
                tickvals=tick_vals,
                ticktext=tick_text,
                showgrid=False, 
                zeroline=False, 
                showticklabels=True,
                showline=False,
                tickfont=dict(color="#666666"),
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor="rgba(255,255,255,0.05)",
                zeroline=False,
                showticklabels=True,
                tickprefix="$",
                tickformat=".2f",
                tickfont=dict(color="#888888"),
                side="right",
                fixedrange=False,
                range=[y_min, y_max],
            ),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=10, r=40, t=40, b=20),
            hovermode="x unified",
            showlegend=False,
        )

        # ── Greeks vs spot chart ─────────────────────────────────────
        greeks_fig = _build_greeks_chart(
            quote, strike, expiry, option_type
        )

        return (
            quote_div, greeks_div,
            price_fig, greeks_fig,
            _status_badge(status, symbol),
            price_history,
        )

    except Exception as e:
        empty_fig = _empty_figure(f"Error: {e}")
        return (
            html.P(f"Error: {e}", className="text-danger"),
            html.P("—"),
            empty_fig, empty_fig,
            _status_badge(DataStatus.OFFLINE, str(e)),
            price_history or [],
        )


# ── Helper Functions ─────────────────────────────────────────────────────────

def _status_badge(status: DataStatus, detail: str = "") -> html.Span:
    """Create a colored status badge."""
    colors = {
        DataStatus.LIVE: ("🟢", "success"),
        DataStatus.STALE: ("🟡", "warning"),
        DataStatus.OFFLINE: ("🔴", "danger"),
    }
    icon, color = colors.get(status, ("⚪", "secondary"))
    return html.Span([
        html.Span(f"{icon} {status.value.upper()} ",
                  className=f"badge bg-{color} me-2"),
        html.Small(detail, className="text-muted"),
    ])


def _empty_figure(message: str = "") -> go.Figure:
    """Create an empty placeholder figure."""
    fig = go.Figure()
    if message:
        fig.add_annotation(text=message, showarrow=False,
                           font=dict(size=14, color="#8b949e"))
    fig.update_layout(template="plotly_dark", height=350)
    return fig


def _build_greeks_chart(quote, strike, expiry, option_type) -> go.Figure:
    """Build a Delta + Gamma vs Spot chart using live market data."""
    import numpy as np

    spots = np.linspace(quote.spot * 0.7, quote.spot * 1.3, 30)
    deltas = []
    gammas = []

    for s in spots:
        r = _pricer.price(
            model="bsm", spot=float(s), strike=strike,
            vol=quote.vol, rate=quote.rate, expiry=expiry,
            option_type=option_type,
        )
        deltas.append(r.greeks.get("delta", 0))
        gammas.append(r.greeks.get("gamma", 0))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spots, y=deltas, mode="lines",
        name="Delta", line=dict(color="#00d4ff", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=spots, y=gammas, mode="lines",
        name="Gamma", line=dict(color="#f59e0b", width=2),
        yaxis="y2",
    ))
    fig.add_vline(x=quote.spot, line_dash="dash", line_color="yellow",
                  annotation_text="Live Spot")

    fig.update_layout(
        title="Live Greeks vs Spot",
        xaxis_title="Spot ($)",
        yaxis=dict(title="Delta", side="left"),
        yaxis2=dict(title="Gamma", side="right", overlaying="y"),
        template="plotly_dark",
        height=350,
        legend=dict(x=0.01, y=0.99),
    )
    return fig
