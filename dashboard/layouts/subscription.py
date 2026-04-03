import dash
from dash import dcc, html, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from quantiv import _quantiv_engine

print("[Quantiv Dash] Booting Subscription Page Engine...")
engine = _quantiv_engine.QuantivPortfolioEngine()

# ── Layout ─────────────────────────────────────────────────────────────────────
def subscription_layout():
    return html.Div(className='fade-up animate-page', children=[
        html.Div(className='subs-page-wrapper', children=[

            # ── Page Header ────────────────────────────────────────────────
            html.Div(style={'textAlign': 'center', 'marginBottom': '40px'}, children=[
                html.H1("Premium Terminal Access", className='text-neon')
            ]),

            # ── Status Banner ──────────────────────────────────────────────
            html.Div(id='current-status-banner', className='status-banner glass-card', 
                     style={'marginBottom': '30px', 'padding': '15px'}),

            # ── Section 1: Credit Top-Ups ──────────────────────────────────
            html.Div(style={'marginBottom': '50px'}, children=[
                html.H3("Instant Credit Top-Up", className='text-info mb-4', 
                        style={'textAlign': 'center', 'fontFamily': "'DM Mono', monospace"}),
                dbc.Row([
                    _credit_bundle_card("Starter Pack", "50", "1.00", "btn-buy-50"),
                    _credit_bundle_card("Pro Pack", "200", "3.00", "btn-buy-200"),
                    _credit_bundle_card("Whale Pack", "400", "5.00", "btn-buy-400"),
                ], className="g-4 justify-content-center"),
            ]),

            # ── Section 2: Subscription Plans ──────────────────────────────
            html.H3("Monthly Memberships", className='text-info mb-4', 
                    style={'textAlign': 'center', 'fontFamily': "'DM Mono', monospace"}),
            html.Div(style={'display': 'flex', 'gap': '20px', 'alignItems': 'stretch'}, children=[

                # ── Basic ──────────────────────────────────────────────────
                html.Div(className='plan-card glass-card', style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}, children=[
                    html.P("BASIC", className='plan-tier-label', style={'color': '#6b6b8a'}),
                    html.Div(children=[html.Span("Free", className='plan-price')]),
                    html.P("Basic tracking and limited models.", className='plan-desc'),
                    html.Div(style={'flex': '1'}, children=[
                        _feature_item("10 daily model credits", True),
                        _feature_item("Standard Portfolio tracking", True),
                        _feature_item("Live market data", False),
                        _feature_item("Advanced Visuals", False),
                    ]),
                    html.Button("Current Plan", disabled=True, className='btn-upgrade btn-upgrade-disabled'),
                ]),

                # ── Plus ───────────────────────────────────────────────────
                html.Div(className='plan-card glass-card plan-card-featured', style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}, children=[
                    html.Div("MOST POPULAR", className='plan-badge'),
                    html.P("PLUS", className='plan-tier-label', style={'color': '#00d4aa'}),
                    html.Div(style={'display': 'flex', 'alignItems': 'baseline', 'gap': '4px'}, children=[
                        html.Span("$9", className='plan-price'),
                        html.Span("/mo", className='plan-price-unit'),
                    ]),
                    html.P("Active trading with high daily limits.", className='plan-desc'),
                    html.Div(style={'flex': '1'}, children=[
                        _feature_item("100 daily credits", True, True),
                        _feature_item("Live market fetching", True, True),
                        _feature_item("Priority execution", True),
                        _feature_item("Advanced Visuals (Locked)", True),
                    ]),
                    html.Button("Upgrade to Plus →", id='btn-up-plus', className='btn-upgrade btn-upgrade-plus'),
                ]),

                # ── Pro ────────────────────────────────────────────────────
                html.Div(className='plan-card glass-card plan-card-pro', style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}, children=[
                    html.P("PRO", className='plan-tier-label', style={'color': '#f5c542'}),
                    html.Div(style={'display': 'flex', 'alignItems': 'baseline', 'gap': '4px'}, children=[
                        html.Span("$15", className='plan-price'),
                        html.Span("/mo", className='plan-price-unit'),
                    ]),
                    html.P("Unlimited power for quant teams.", className='plan-desc'),
                    html.Div(style={'flex': '1'}, children=[
                        _feature_item("Unlimited credits", True, True),
                        _feature_item("Visual Locks Removed", True, True),
                        _feature_item("Advanced Greeks Engine", True, True),
                        _feature_item("Institutional Analytics", True, True),
                    ]),
                    html.Button("Upgrade to Pro →", id='btn-up-pro', className='btn-upgrade btn-upgrade-pro'),
                ]),
            ]),

            # ── Feedback Message ───────────────────────────────────────────
            html.Div(id='upgrade-msg', style={'textAlign': 'center', 'marginTop': '32px', 'minHeight': '24px'}),

            html.P("Secure 256-bit encrypted transactions.", className='subs-footer-note', style={'textAlign': 'center', 'marginTop': '20px', 'color': '#555'}),
        ])
    ])

# ── Helper UI Components ──────────────────────────────────────────────────────

def _credit_bundle_card(name, credits, price, btn_id):
    return dbc.Col(md=3, children=[
        html.Div(className="glass-card p-4 text-center h-100", children=[
            html.H5(name, className="text-muted small"),
            html.H2(f"{credits} credits", className="text-neon",style={"font-size":"20px"}),
            html.H4(f"${price}", className="text-white"),
            dbc.Button(f"Buy Bundle", id=btn_id, color="success", className="w-100 mt-2 fw-bold")
        ])
    ])

def _feature_item(text, available=True, highlight=False):
    icon = "✓" if available else "✗"
    color = "feature-check-yes" if available else "feature-check-no"
    text_class = "feature-item-highlighted" if highlight else ""
    return html.Div(className='feature-item', children=[
        html.Span(icon, className=color),
        html.Span(text, className=text_class),
    ])

# ── Callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output('current-status-banner', 'children'),
    Input('session-user', 'data'),
)
def load_status(username):
    if not username:
        return html.Span("Please log in to manage your subscription.", style={'color': '#6b6b8a'})
    
    tier = engine.get_subscription_tier(username)
    uses = engine.get_remaining_uses(username)
    display_uses = "Unlimited" if uses == -1 else f"{uses} credits remaining"
    
    tier_color = '#f5c542' if tier == 'Pro' else '#00d4aa' if tier == 'Plus' else '#6b6b8a'

    return [
        html.Span(f"User: {username}", style={'color': '#9090b0', 'marginRight': '15px'}),
        html.Span(f"Plan: "),
        html.Strong(tier, style={'color': tier_color}),
        html.Span(" | ", style={'margin': '0 10px', 'color': '#333'}),
        html.Strong(display_uses, style={'color': '#4f8eff'}),
    ]

@callback(
    Output('upgrade-msg', 'children'),
    Output('current-status-banner', 'children', allow_duplicate=True),
    [Input('btn-up-plus', 'n_clicks'), Input('btn-up-pro', 'n_clicks'),
     Input('btn-buy-50', 'n_clicks'), Input('btn-buy-200', 'n_clicks'), Input('btn-buy-400', 'n_clicks')],
    State('session-user', 'data'),
    prevent_initial_call=True,
)
def handle_purchases(plus, pro, b50, b200, b400, username):
    if not username:
        return html.Span("Login required.", style={'color': "#ff4f6d"}), no_update

    ctx = dash.callback_context
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    success = False
    msg = ""

    # Handle Subscriptions
    if btn_id in ['btn-up-plus', 'btn-up-pro']:
        new_tier = "Plus" if btn_id == 'btn-up-plus' else "Pro"
        success = engine.upgrade_subscription(username, new_tier)
        msg = f"Upgraded to {new_tier}!"

    # Handle Credit Bundles
    elif btn_id == 'btn-buy-50':
        success = engine.buy_credit_bundle(username, 1)
        msg = "Added 50 credits!"
    elif btn_id == 'btn-buy-200':
        success = engine.buy_credit_bundle(username, 3)
        msg = "Added 200 credits!"
    elif btn_id == 'btn-buy-400':
        success = engine.buy_credit_bundle(username, 5)
        msg = "Added 400 credits!"

    if success:
        # Refresh status banner
        return html.Span(f"✓ {msg}", style={'color': '#00d4aa'}), load_status(username)
    else:
        return html.Span("Transaction failed. Check balance.", style={'color': '#ff4f6d'}), no_update