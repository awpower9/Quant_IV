import dash
from dash import dcc, html, callback, Input, Output, State, no_update
from quantiv import _quantiv_engine


print("[Quantiv Dash] Booting Subscription Page Engine...")
engine = _quantiv_engine.QuantivPortfolioEngine()

# ── Layout ─────────────────────────────────────────────────────────────────────
# All styles live in /assets/quantiv.css — Dash auto-loads it on startup.
def subscription_layout():
   return html.Div(
    
    className='fade-up',
    children=[
        # ---> FIX: Deleted the duplicate dcc.Store(id='session-user') from here! <---
        
        html.Div(className='subs-page-wrapper', children=[

            # ── Page Header ────────────────────────────────────────────────
            html.Div(style={'textAlign': 'center', 'marginBottom': '52px'}, children=[
                html.H1("Choose Your Plan", className='text-neon')
            ]),

            # ── Status Banner ──────────────────────────────────────────────
            html.Div(id='current-status-banner', className='status-banner'),

            # ── Plan Cards ─────────────────────────────────────────────────
            html.Div(style={'display': 'flex', 'gap': '20px', 'alignItems': 'stretch'},
                     children=[

                # ── Basic ──────────────────────────────────────────────────
                html.Div(className='plan-card', style={'display': 'flex', 'flexDirection': 'column'},
                         children=[
                    html.P("BASIC", className='plan-tier-label',
                           style={'color': '#6b6b8a'}),
                    html.Div(style={'marginBottom': '6px'}, children=[
                        html.Span("Free", className='plan-price'),
                    ]),
                    html.P("Get started with basic portfolio tracking.",
                           className='plan-desc'),
                    html.Div(style={'marginBottom': '28px', 'flex': '1'}, children=[
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("10 model calculations"),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("Basic portfolio tracking"),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✗", className='feature-check-no'),
                            html.Span("Live market data"),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✗", className='feature-check-no'),
                            html.Span("Advanced analytics"),
                        ]),
                    ]),
                    html.Button("Current Plan", disabled=True,
                                className='btn-upgrade btn-upgrade-disabled'),
                ]),

                # ── Plus ───────────────────────────────────────────────────
                html.Div(className='plan-card plan-card-featured',
                         style={'display': 'flex', 'flexDirection': 'column'}, children=[
                    html.Div("MOST POPULAR", className='plan-badge'),
                    html.P("PLUS", className='plan-tier-label',
                           style={'color': '#00d4aa'}),
                    html.Div(style={'display': 'flex', 'alignItems': 'baseline', 'gap': '4px',
                                    'marginBottom': '6px'}, children=[
                        html.Span("$1", className='plan-price'),
                        html.Span("/mo", className='plan-price-unit'),
                    ]),
                    html.P("Ideal for active traders needing real-time data.",
                           className='plan-desc'),
                    html.Div(style={'marginBottom': '28px', 'flex': '1'}, children=[
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("50 model calculations",
                                      className='feature-item-highlighted'),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("Basic portfolio tracking"),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("Live market fetching",
                                      className='feature-item-highlighted'),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("Priority execution",
                                      className='feature-item-highlighted'),
                        ]),
                    ]),
                    html.Button("Upgrade to Plus →", id='btn-up-plus',
                                className='btn-upgrade btn-upgrade-plus'),
                ]),

                # ── Pro ────────────────────────────────────────────────────
                html.Div(className='plan-card plan-card-pro',
                         style={'display': 'flex', 'flexDirection': 'column'}, children=[
                    html.P("PRO", className='plan-tier-label',
                           style={'color': '#f5c542'}),
                    html.Div(style={'display': 'flex', 'alignItems': 'baseline', 'gap': '4px',
                                    'marginBottom': '6px'}, children=[
                        html.Span("$2", className='plan-price'),
                        html.Span("/mo", className='plan-price-unit'),
                    ]),
                    html.P("For quant teams requiring the full institutional suite.",
                           className='plan-desc'),
                    html.Div(style={'marginBottom': '28px', 'flex': '1'}, children=[
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("100 model calculations",
                                      className='feature-item-highlighted'),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("Live market fetching"),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("Advanced Greeks & options",
                                      className='feature-item-highlighted'),
                        ]),
                        html.Div(className='feature-item', children=[
                            html.Span("✓", className='feature-check-yes'),
                            html.Span("Institutional data feeds",
                                      className='feature-item-highlighted'),
                        ]),
                    ]),
                    html.Button("Upgrade to Pro →", id='btn-up-pro',
                                className='btn-upgrade btn-upgrade-pro'),
                ]),
            ]),

            # ── Feedback Message ───────────────────────────────────────────
            html.Div(id='upgrade-msg',
                     style={'textAlign': 'center', 'marginTop': '32px',
                            'minHeight': '24px', 'fontSize': '14px',
                            'fontFamily': "'DM Mono', monospace"}),

            html.P(
                "All plans include 256-bit encryption and SOC 2 compliant infrastructure.",
                className='subs-footer-note'
            ),
        ])
    ]
)


# ── Callbacks (identical logic) ────────────────────────────────────────────────

@callback(
    Output('current-status-banner', 'children'),
    Input('session-user', 'data'),
)
def load_status(username):
    if not username:
        return html.Span(
            "Please log in via the Portfolio tab to view your plan.",
            style={'color': '#6b6b8a', 'fontFamily': "'DM Mono', monospace",
                   'fontSize': '12px'}
        )
    tier = engine.get_subscription_tier(username)
    uses = engine.get_remaining_uses(username)

    tier_color = (
        '#f5c542' if tier == 'Pro'  else
        '#00d4aa' if tier == 'Plus' else
        '#6b6b8a'
    )

    return [
        html.Span("●", style={'color': '#00d4aa', 'fontSize': '10px'}),
        html.Span(f"{username}", style={'color': '#9090b0'}),
        html.Span("·", style={'color': '#3d3d6b', 'margin': '0 4px'}),
        html.Span("Plan: "),
        html.Strong(tier, style={'color': tier_color}),
        html.Span("·", style={'color': '#3d3d6b', 'margin': '0 8px'}),
        html.Span("⚡"),
        html.Strong(f" {uses} credits remaining", style={'color': '#4f8eff'}),
    ]


@callback(
    [Output('upgrade-msg', 'children'),
     Output('current-status-banner', 'children', allow_duplicate=True),
     Output('session-user', 'data', allow_duplicate=True)],
    [Input('btn-up-plus', 'n_clicks'), Input('btn-up-pro', 'n_clicks')],
    State('session-user', 'data'),
    prevent_initial_call=True,
)
def handle_upgrade(plus_clicks, pro_clicks, username):
    print(f"\n[DEBUG] Upgrade button clicked by user: '{username}'")

    if not username:
        print("[DEBUG] Blocked: No user logged in.")
        return (
            html.Span("⚠ Please log in via the Portfolio tab first.",
                      style={'color': '#f5c542'}),
            no_update,
            no_update # <-- Added 3rd output
        )

    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update # <-- Added 3rd output

    btn_id   = ctx.triggered[0]['prop_id'].split('.')[0]
    new_tier = "Plus" if btn_id == 'btn-up-plus' else "Pro"
    print(f"[DEBUG] Attempting to upgrade to {new_tier}...")

    try:
        success = engine.upgrade_subscription(username, new_tier)
        print(f"[DEBUG] C++ engine returned: {success}")

        if success:
            uses       = engine.get_remaining_uses(username)
            tier_color = '#00d4aa' if new_tier == 'Plus' else '#f5c542'

            new_banner = [
                html.Span("●", style={'color': '#00d4aa', 'fontSize': '10px'}),
                html.Span(f"{username}", style={'color': '#9090b0'}),
                html.Span("·", style={'color': '#3d3d6b', 'margin': '0 4px'}),
                html.Span("Plan: "),
                html.Strong(new_tier, style={'color': tier_color}),
                html.Span("·", style={'color': '#3d3d6b', 'margin': '0 8px'}),
                html.Span("⚡"),
                html.Strong(f" {uses} credits remaining", style={'color': '#4f8eff'}),
            ]
            return (
                html.Span(f"✓ Successfully upgraded to {new_tier}!",
                          style={'color': '#00d4aa'}),
                new_banner,
                no_update # <-- Added 3rd output
            )
        else:
            return (
                html.Span("Engine rejected the upgrade request.",
                          style={'color': '#ff4f6d'}),
                no_update,
                no_update # <-- Added 3rd output
            )

    except AttributeError as e:
        print(f"[DEBUG] CRITICAL AttributeError: {e}")
        return (
            html.Span("Python couldn't find the C++ upgrade function. Did you recompile?",
                      style={'color': '#ff4f6d'}),
            no_update,
            no_update # <-- Added 3rd output
        )
    except Exception as e:
        print(f"[DEBUG] DATABASE CRASH: {e}")
        return (
            html.Span(f"DB Error: {str(e)}", style={'color': '#ff4f6d'}),
            no_update,
            no_update # <-- Added 3rd output
        )
