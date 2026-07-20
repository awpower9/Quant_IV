"""
model_compare_callbacks.py — Callbacks for the multi-model comparison page.

Connects dcc.Interval → LiveMarketService → Pricer (all selected models)
→ overlay charts + comparison table.
"""

import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import time as _time

from quantiv.data.live_service import LiveMarketService, DataStatus
from quantiv.pricing import Pricer
from quantiv.utils.formatting import format_price

from dashboard.layouts.model_compare_page import MODEL_COLORS, MODEL_LABELS


# ── Module-level singletons ──────────────────────────────────────────────────

_service = LiveMarketService()
_pricer = Pricer()


# ── Toggle auto-refresh ─────────────────────────────────────────────────────

@dash.callback(
    Output("mc-interval", "disabled"),
    Input("mc-auto-refresh-toggle", "value"),
)
def toggle_mc_auto_refresh(toggle_value):
    """Enable/disable the dcc.Interval."""
    return "on" not in (toggle_value or [])


# ── Main refresh callback ───────────────────────────────────────────────────

@dash.callback(
    Output("mc-quote-content", "children"),
    Output("mc-comparison-table", "children"),
    Output("mc-price-overlay-chart", "figure"),
    Output("mc-spot-chart", "figure"),
    Output("mc-spread-chart", "figure"),
    Output("mc-strike-curve-chart", "figure"),
    Output("mc-status-badge", "children"),
    Output("mc-model-history", "data"),
    Output("mc-spot-history", "data"),
    Input("mc-interval", "n_intervals"),
    Input("mc-track-btn", "n_clicks"),
    State("mc-symbol-input", "value"),
    State("mc-model-selector", "value"),
    State("mc-strike", "value"),
    State("mc-expiry", "value"),
    State("mc-option-type", "value"),
    State("mc-tree-steps", "value"),
    State("mc-num-paths", "value"),
    State("mc-seed", "value"),
    State("mc-model-history", "data"),
    State("mc-spot-history", "data"),
)
def refresh_model_compare(
    n_intervals, n_clicks, symbol, selected_models,
    strike, expiry, option_type,
    tree_steps, num_paths, seed,
    model_history, spot_history,
):
    """
    Main refresh — price with all selected models, build overlay charts.
    """
    empty = _empty_figure("Enter a symbol and click Track")
    default_out = (
        html.P("Enter a symbol and click 'Track' to start."),
        html.P("—"),
        empty, empty, empty, empty,
        _status_badge(DataStatus.OFFLINE, "No symbol"),
        {}, [],
    )

    if not symbol or not symbol.strip():
        return default_out

    symbol = symbol.strip().upper()
    selected_models = selected_models or ["bsm"]

    # Require explicit Track click to start
    if symbol not in _service.tracked_symbols:
        triggered = dash.callback_context.triggered
        is_track = any(
            t.get("prop_id", "") == "mc-track-btn.n_clicks"
            for t in triggered
        ) if triggered else False

        if not is_track and n_clicks == 0:
            empty_fig = _empty_figure("Click Track to begin")
            return (
                html.P("Click 'Track' to start live data."),
                html.P("—"),
                empty_fig, empty_fig, empty_fig, empty_fig,
                _status_badge(DataStatus.OFFLINE, "Not tracking"),
                model_history or {}, spot_history or [],
            )

        try:
            _service.start(symbol)
        except Exception:
            pass

    try:
        # ── Fetch live data ──────────────────────────────────────────
        quote = _service.get_live_quote(symbol)
        status = _service.status
        now_str = datetime.now().strftime("%H:%M:%S")

        # ── Price with each selected model ───────────────────────────
        results = {}
        timings = {}
        for model_key in selected_models:
            t0 = _time.perf_counter()
            try:
                res = _pricer.price(
                    model=model_key,
                    spot=quote.spot,
                    strike=strike,
                    vol=quote.vol,
                    rate=quote.rate,
                    expiry=expiry,
                    option_type=option_type,
                    steps=tree_steps or 100,
                    num_paths=num_paths or 100000,
                    seed=seed or 42,
                )
                results[model_key] = res
            except Exception as e:
                results[model_key] = None
            elapsed = (_time.perf_counter() - t0) * 1000  # ms
            timings[model_key] = elapsed

        # ── Update price history ─────────────────────────────────────
        if model_history is None:
            model_history = {}
        if spot_history is None:
            spot_history = []

        for mk, res in results.items():
            if mk not in model_history:
                model_history[mk] = []
            if res is not None:
                model_history[mk].append({
                    "time": now_str,
                    "price": res.price,
                })
            # Keep last 60 points
            model_history[mk] = model_history[mk][-60:]

        spot_history.append({"time": now_str, "spot": quote.spot})
        spot_history = spot_history[-60:]

        # ── Build quote card ─────────────────────────────────────────
        quote_div = html.Div([
            html.H3(symbol, className="mc-symbol"),
            html.H2(format_price(quote.spot, 2), className="mc-spot-price"),
            html.P(
                f"Vol: {quote.vol:.1%}  |  Rate: {quote.rate:.2%}",
                className="text-muted",
            ),
            html.Small(
                f"Updated: {now_str}",
                className="text-muted",
            ),
        ])

        # ── Build comparison table ───────────────────────────────────
        comp_table = _build_comparison_table(results, timings)

        # ── Build overlay chart ──────────────────────────────────────
        overlay_fig = _build_overlay_chart(model_history, symbol, option_type)

        # ── Build spot chart ─────────────────────────────────────────
        spot_fig = _build_spot_chart(spot_history, symbol)

        # ── Build spread chart ───────────────────────────────────────
        spread_fig = _build_spread_chart(model_history)

        # ── Build strike curve chart ─────────────────────────────────
        strike_fig = _build_strike_curves(
            quote, selected_models, expiry, option_type,
            tree_steps or 100, num_paths or 100000, seed or 42,
        )

        return (
            quote_div, comp_table,
            overlay_fig, spot_fig, spread_fig, strike_fig,
            _status_badge(status, symbol),
            model_history, spot_history,
        )

    except Exception as e:
        err_fig = _empty_figure(f"Error: {e}")
        return (
            html.P(f"Error: {e}", className="text-danger"),
            html.P("—"),
            err_fig, err_fig, err_fig, err_fig,
            _status_badge(DataStatus.OFFLINE, str(e)),
            model_history or {}, spot_history or [],
        )


# ── Chart builders ───────────────────────────────────────────────────────────

def _build_overlay_chart(model_history, symbol, option_type):
    """Overlay time-series of option prices from all tracked models."""
    fig = go.Figure()

    for mk, history in model_history.items():
        if not history:
            continue
        times = [p["time"] for p in history]
        prices = [p["price"] for p in history]
        color = MODEL_COLORS.get(mk, "#ffffff")
        label = MODEL_LABELS.get(mk, mk)
        dash_style = "dot" if mk == "monte_carlo" else "solid"

        fig.add_trace(go.Scatter(
            x=times, y=prices,
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2.5, dash=dash_style),
            marker=dict(size=4),
        ))

    fig.update_layout(
        title=f"{symbol} — Option Price ({option_type.capitalize()}) by Model",
        xaxis_title="Time",
        yaxis_title="Option Price (₹)",
        template="plotly_dark",
        height=420,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(size=12),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
    )
    return fig


def _build_spot_chart(spot_history, symbol):
    """Live spot price time series."""
    fig = go.Figure()
    if spot_history:
        times = [p["time"] for p in spot_history]
        spots = [p["spot"] for p in spot_history]
        fig.add_trace(go.Scatter(
            x=times, y=spots,
            mode="lines+markers",
            name="Spot Price",
            line=dict(color="#00d4ff", width=2),
            marker=dict(size=4),
            fill="tozeroy",
            fillcolor="rgba(0, 212, 255, 0.08)",
        ))

    fig.update_layout(
        title=f"{symbol} — Spot Price",
        xaxis_title="Time",
        yaxis_title="Price (₹)",
        template="plotly_dark",
        height=320,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _build_spread_chart(model_history):
    """Show price spread of each model relative to BSM."""
    fig = go.Figure()
    bsm_data = model_history.get("bsm", [])

    if not bsm_data:
        fig.add_annotation(
            text="BSM not selected — enable it to see spreads",
            showarrow=False, font=dict(size=13, color="#8b949e"),
        )
        fig.update_layout(template="plotly_dark", height=320,
                          plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)")
        return fig

    bsm_times = [p["time"] for p in bsm_data]
    bsm_prices = [p["price"] for p in bsm_data]

    for mk, history in model_history.items():
        if mk == "bsm" or not history:
            continue
        color = MODEL_COLORS.get(mk, "#ffffff")
        label = MODEL_LABELS.get(mk, mk)

        # Align by time (take last N that match)
        n = min(len(history), len(bsm_data))
        spreads = [
            history[-(n - i)]["price"] - bsm_prices[-(n - i)]
            for i in range(n)
        ]
        times = bsm_times[-n:]

        fig.add_trace(go.Bar(
            x=times, y=spreads,
            name=f"{label} − BSM",
            marker_color=color,
            opacity=0.8,
        ))

    fig.update_layout(
        title="Price Spread vs Black-Scholes",
        xaxis_title="Time",
        yaxis_title="Spread (₹)",
        template="plotly_dark",
        height=320,
        barmode="group",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
        ),
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#8b949e", opacity=0.5)
    return fig


def _build_strike_curves(quote, selected_models, expiry, option_type,
                          steps, num_paths, seed):
    """
    Option price vs strike for all selected models at the current spot.
    A static cross-sectional snapshot — not time-series.
    """
    fig = go.Figure()

    strikes = np.linspace(quote.spot * 0.7, quote.spot * 1.3, 40)

    for mk in selected_models:
        prices = []
        color = MODEL_COLORS.get(mk, "#ffffff")
        label = MODEL_LABELS.get(mk, mk)
        dash_style = "dot" if mk == "monte_carlo" else "solid"

        for k in strikes:
            try:
                res = _pricer.price(
                    model=mk,
                    spot=quote.spot,
                    strike=float(k),
                    vol=quote.vol,
                    rate=quote.rate,
                    expiry=expiry,
                    option_type=option_type,
                    steps=steps,
                    num_paths=num_paths,
                    seed=seed,
                )
                prices.append(res.price)
            except Exception:
                prices.append(None)

        fig.add_trace(go.Scatter(
            x=strikes, y=prices,
            mode="lines",
            name=label,
            line=dict(color=color, width=2.5, dash=dash_style),
        ))

    # Mark current strike
    fig.add_vline(
        x=quote.spot, line_dash="dash", line_color="#f59e0b",
        opacity=0.6,
        annotation_text="Spot",
        annotation_font_color="#f59e0b",
    )

    fig.update_layout(
        title=f"Option Price vs Strike ({option_type.capitalize()})",
        xaxis_title="Strike (₹)",
        yaxis_title="Option Price (₹)",
        template="plotly_dark",
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
        ),
        hovermode="x unified",
    )
    return fig


# ── UI helpers ───────────────────────────────────────────────────────────────

def _build_comparison_table(results, timings):
    """Build a rich comparison table of model prices."""
    rows = []
    for mk in results:
        res = results[mk]
        label = MODEL_LABELS.get(mk, mk)
        color = MODEL_COLORS.get(mk, "#ffffff")
        elapsed = timings.get(mk, 0)

        if res is not None:
            price_text = format_price(res.price)
            delta = res.greeks.get("delta", None)
            gamma = res.greeks.get("gamma", None)
            delta_text = f"{delta:.4f}" if delta is not None else "—"
            gamma_text = f"{gamma:.6f}" if gamma is not None else "—"
        else:
            price_text = "Error"
            delta_text = "—"
            gamma_text = "—"

        rows.append(html.Tr([
            html.Td(
                html.Span([
                    html.Span("●  ",
                              style={"color": color, "fontSize": "1.2em"}),
                    label,
                ]),
            ),
            html.Td(price_text, className="fw-bold"),
            html.Td(delta_text),
            html.Td(gamma_text),
            html.Td(f"{elapsed:.1f} ms", className="text-muted"),
        ]))

    return html.Table([
        html.Thead(html.Tr([
            html.Th("Model"),
            html.Th("Price"),
            html.Th("Delta"),
            html.Th("Gamma"),
            html.Th("Compute"),
        ])),
        html.Tbody(rows),
    ], className="table table-sm table-dark mc-table")


def _status_badge(status: DataStatus, detail: str = "") -> html.Span:
    """Colored status badge."""
    colors = {
        DataStatus.LIVE: ("*", "success"),
        DataStatus.STALE: ("*", "warning"),
        DataStatus.OFFLINE: ("*", "danger"),
    }
    _, color = colors.get(status, ("*", "secondary"))
    return html.Span([
        html.Span(
            f" {status.value.upper()} ",
            className=f"badge bg-{color} me-2",
        ),
        html.Small(detail, className="text-muted"),
    ])


def _empty_figure(message: str = "") -> go.Figure:
    """Create an empty placeholder figure."""
    fig = go.Figure()
    if message:
        fig.add_annotation(
            text=message, showarrow=False,
            font=dict(size=14, color="#8b949e"),
        )
    fig.update_layout(
        template="plotly_dark", height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
