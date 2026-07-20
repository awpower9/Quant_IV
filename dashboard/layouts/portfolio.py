import dash
from dash import dcc, html, callback, Input, Output, State, dash_table, no_update
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from quantiv.portfolio_engine import QuantivPortfolioEngine
from quantiv.pricing import Pricer

try:
    engine = QuantivPortfolioEngine()
except Exception as e:
    print(f"FAILED TO LOAD C++ ENGINE: {e}")

# Color Palette for premium terminal styling
C = {
    'green': '#10b981', 'red': '#ef4444', 'blue': '#3b82f6', 
    'gold': '#fbbf24', 'muted': '#94a3b8', 'text': '#f8fafc',
    'purple': '#a855f7', 'cyan': '#06b6d4'
}

def portfolio_layout():
    return html.Div([
        html.Div(id='main-content-container', style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '40px 20px'})
    ])

# ── 1. LOGIN SCREEN ──────────────────────────────────────────────────────────
def render_login_screen():
    return html.Div(className='animate-fade-up', style={
        'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center',
        'justifyContent': 'center', 'minHeight': '80vh'
    }, children=[
        html.Div(className='glass-card delay-1 animate-fade-up', style={'width': '400px', 'padding': '40px'}, children=[
            html.Div(style={'textAlign': 'center', 'marginBottom': '30px'}, children=[
                html.Div('', style={'fontSize': '40px', 'color': C['green'], 'animation': 'float 3s ease-in-out infinite'}),
                html.H2("QuantIV Terminal", style={'color': C['text'], 'margin': '10px 0 5px 0', 'fontWeight': '700'}),
                html.P("Secure Access Portal", style={'color': C['muted'], 'fontSize': '13px', 'letterSpacing': '1px', 'textTransform': 'uppercase'})
            ]),

            dcc.Input(id='auth-user', type='text', placeholder='Username', className='modern-input', style={'width': '100%', 'padding': '14px', 'marginBottom': '15px'}),
            dcc.Input(id='auth-pass', type='password', placeholder='Password', className='modern-input', style={'width': '100%', 'padding': '14px', 'marginBottom': '30px'}),

            html.Div(style={'display': 'flex', 'gap': '15px'}, children=[
                html.Button('Login', id='btn-login', className='btn-neon', style={'flex': '1', 'padding': '14px', 'cursor': 'pointer'}),
                html.Button('Register', id='btn-register', className='btn-secondary', style={'flex': '1', 'padding': '14px', 'borderRadius': '8px', 'cursor': 'pointer'})
            ]),

            html.Div(id='auth-msg', style={'marginTop': '20px', 'textAlign': 'center', 'height': '20px', 'fontSize': '13px'})
        ])
    ])

# ── 2. PORTFOLIO & RISK CALCULATOR ───────────────────────────────────────────
def get_portfolio_views(username):
    try:
        cash = engine.get_available_cash(username)
        raw_portfolio = engine.get_user_portfolio(username)
    except:
        cash, raw_portfolio = 0.0, []

    total_invested = 0.0
    live_portfolio_val = 0.0
    processed_portfolio = []

    # Portfolio-level Greeks
    portfolio_delta = 0.0
    portfolio_gamma = 0.0
    portfolio_vega = 0.0
    portfolio_theta = 0.0

    # Shocks for risk curve
    shocks = [-0.20, -0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15, 0.20]
    live_prices = {}

    if raw_portfolio:
        # Resolve unique underlying symbols to fetch their live spot prices
        symbols = list(set([p.symbol.split('_')[0] if '_' in p.symbol else p.symbol for p in raw_portfolio]))
        for sym in symbols:
            try:
                ticker = yf.Ticker(sym)
                price = ticker.fast_info['lastPrice']
                currency = ticker.fast_info['currency'] if 'currency' in ticker.fast_info else 'USD'
                
                # Auto-convert foreign underlying assets back to USD
                if currency != 'USD':
                    try:
                        fx_ticker = yf.Ticker(f"{currency}USD=X")
                        rate = fx_ticker.fast_info['lastPrice']
                        price = price * rate
                    except:
                        pass
                live_prices[sym] = price
            except:
                live_prices[sym] = None

        # Process each position and compute its Greeks dynamically
        for p in raw_portfolio:
            if "_" in p.symbol:
                # Option position: underlying_type_strike_expiry
                try:
                    underlying, opt_type_char, strike_str, expiry_str = p.symbol.split('_')
                    opt_type = "call" if opt_type_char.upper() == "C" else "put"
                    strike = float(strike_str)
                    expiry = float(expiry_str)
                except Exception as ex:
                    print(f"Error parsing option symbol {p.symbol}: {ex}")
                    continue

                invested = p.purchase_price * p.quantity * 100
                total_invested += invested
                
                cp = live_prices.get(underlying)
                if cp is not None:
                    try:
                        # Price option and get Greeks dynamically via BSM
                        res = Pricer().price(
                            model="bsm", spot=cp, strike=strike, vol=0.20,
                            rate=0.05, expiry=expiry, option_type=opt_type
                        )
                        live_val = res.price * p.quantity * 100
                        live_portfolio_val += live_val
                        pnl = live_val - invested
                        pnl_str = f"-₹{abs(pnl):,.2f}" if pnl < 0 else f"+₹{pnl:,.2f}"

                        # Accumulate weighted Greeks (contracts are 100 shares each multiplier)
                        portfolio_delta += res.greeks.get('delta', 0.0) * p.quantity * 100
                        portfolio_gamma += res.greeks.get('gamma', 0.0) * p.quantity * 100
                        portfolio_vega += res.greeks.get('vega', 0.0) * p.quantity * 100
                        portfolio_theta += res.greeks.get('theta', 0.0) * p.quantity * 100

                        processed_portfolio.append({
                            "Symbol": p.symbol, "Name": p.name, "Qty": p.quantity,
                            "Avg Cost": f"₹{p.purchase_price:,.2f}",
                            "Live Price": f"₹{res.price:,.2f}",
                            "Current Value": f"₹{live_val:,.2f}",
                            "PnL": pnl_str
                        })
                    except Exception as ex:
                        print(f"Error pricing option {p.symbol}: {ex}")
                        processed_portfolio.append({
                            "Symbol": p.symbol, "Name": p.name, "Qty": p.quantity,
                            "Avg Cost": f"₹{p.purchase_price:,.2f}", "Live Price": "Error",
                            "Current Value": "Error", "PnL": "Error"
                        })
                else:
                    processed_portfolio.append({
                        "Symbol": p.symbol, "Name": p.name, "Qty": p.quantity,
                        "Avg Cost": f"₹{p.purchase_price:,.2f}", "Live Price": "N/A",
                        "Current Value": "N/A", "PnL": "N/A"
                    })
            else:
                # Stock position
                invested = p.purchase_price * p.quantity
                total_invested += invested
                
                cp = live_prices.get(p.symbol)
                if cp is not None:
                    live_val = cp * p.quantity
                    live_portfolio_val += live_val
                    pnl = live_val - invested
                    pnl_str = f"-₹{abs(pnl):,.2f}" if pnl < 0 else f"+₹{pnl:,.2f}"
                    
                    portfolio_delta += p.quantity  # Delta = 1.0 per share
                    
                    processed_portfolio.append({
                        "Symbol": p.symbol, "Name": p.name, "Qty": p.quantity,
                        "Avg Cost": f"₹{p.purchase_price:,.2f}",
                        "Live Price": f"₹{cp:,.2f}",
                        "Current Value": f"₹{live_val:,.2f}",
                        "PnL": pnl_str
                    })
                else:
                    processed_portfolio.append({
                        "Symbol": p.symbol, "Name": p.name, "Qty": p.quantity,
                        "Avg Cost": f"₹{p.purchase_price:,.2f}", "Live Price": "N/A",
                        "Current Value": "N/A", "PnL": "N/A"
                    })

    live_equity = cash + live_portfolio_val

    # Create the Holdings Table UI
    if not raw_portfolio:
        table_ui = html.Div(className='glass-card animate-fade-up delay-4', style={'padding': '40px', 'textAlign': 'center'}, children=[
            html.P("Portfolio is empty.", style={'color': C['muted'], 'fontSize': '16px'}),
            html.P("Execute your first trade in the Trade Terminal to populate this terminal.", style={'color': C['muted'], 'fontSize': '13px', 'opacity': '0.7'})
        ])
    else:
        df = pd.DataFrame(processed_portfolio)
        table_ui = html.Div(className='animate-fade-up delay-4', children=[
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_header={'backgroundColor': 'rgba(0,0,0,0.4)', 'color': C['muted'], 'fontWeight': 'bold', 'border': 'none', 'padding': '15px'},
                style_cell={'backgroundColor': 'rgba(20,20,30,0.4)', 'color': C['text'], 'border': 'none', 'borderBottom': '1px solid rgba(255,255,255,0.05)', 'padding': '15px', 'textAlign': 'left', 'fontFamily': 'Inter'},
                style_data_conditional=[
                    {'if': {'column_id': 'Current Value'}, 'color': C['blue'], 'fontWeight': 'bold'},
                    {'if': {'column_id': 'PnL', 'filter_query': '{PnL} contains "-"' }, 'color': C['red']},
                    {'if': {'column_id': 'PnL', 'filter_query': '{PnL} contains "+"' }, 'color': C['green']}
                ],
            )
        ])

    stats_children = [
        html.Div(className='glass-card', style={'flex': '1', 'padding': '25px'}, children=[
            html.P("Buying Power", style={'color': C['muted'], 'fontSize': '13px', 'textTransform': 'uppercase', 'margin': '0 0 10px 0'}),
            html.H1(f"₹{cash:,.2f}", className='mono-text', style={'color': C['text'], 'margin': '0', 'fontSize': '30px'})
        ]),
        html.Div(className='glass-card', style={'flex': '1', 'padding': '25px'}, children=[
            html.P("Total Invested", style={'color': C['muted'], 'fontSize': '13px', 'textTransform': 'uppercase', 'margin': '0 0 10px 0'}),
            html.H1(f"₹{total_invested:,.2f}", className='mono-text', style={'color': C['gold'], 'margin': '0', 'fontSize': '30px'})
        ]),
        html.Div(className='glass-card', style={'flex': '1', 'padding': '25px'}, children=[
            html.P("Live Equity", style={'color': C['muted'], 'fontSize': '13px', 'textTransform': 'uppercase', 'margin': '0 0 10px 0'}),
            html.H1(f"₹{live_equity:,.2f}", className='mono-text', style={'color': C['green'], 'margin': '0', 'fontSize': '30px'})
        ])
    ]

    greeks_children = [
        html.Div(className='glass-card', style={'flex': '1', 'padding': '20px', 'borderLeft': f'4px solid {C["blue"]}'}, children=[
            html.P("Portfolio Delta ($ Delta)", style={'color': C['muted'], 'fontSize': '11px', 'textTransform': 'uppercase', 'margin': '0 0 5px 0'}),
            html.H3(f"₹{portfolio_delta:,.2f}", className='mono-text', style={'color': C['text'], 'margin': '0', 'fontWeight': 'bold'})
        ]),
        html.Div(className='glass-card', style={'flex': '1', 'padding': '20px', 'borderLeft': f'4px solid {C["purple"]}'}, children=[
            html.P("Portfolio Gamma", style={'color': C['muted'], 'fontSize': '11px', 'textTransform': 'uppercase', 'margin': '0 0 5px 0'}),
            html.H3(f"{portfolio_gamma:,.4f}", className='mono-text', style={'color': C['text'], 'margin': '0', 'fontWeight': 'bold'})
        ]),
        html.Div(className='glass-card', style={'flex': '1', 'padding': '20px', 'borderLeft': f'4px solid {C["gold"]}'}, children=[
            html.P("Portfolio Vega", style={'color': C['muted'], 'fontSize': '11px', 'textTransform': 'uppercase', 'margin': '0 0 5px 0'}),
            html.H3(f"₹{portfolio_vega:,.2f}", className='mono-text', style={'color': C['text'], 'margin': '0', 'fontWeight': 'bold'})
        ]),
        html.Div(className='glass-card', style={'flex': '1', 'padding': '20px', 'borderLeft': f'4px solid {C["red"]}'}, children=[
            html.P("Portfolio Theta", style={'color': C['muted'], 'fontSize': '11px', 'textTransform': 'uppercase', 'margin': '0 0 5px 0'}),
            html.H3(f"₹{portfolio_theta:,.2f}/day", className='mono-text', style={'color': C['text'], 'margin': '0', 'fontWeight': 'bold'})
        ])
    ]

    # Compute Shock Stress Test Curve Points
    pnl_points = []
    current_equity = cash + live_portfolio_val
    for shock in shocks:
        sim_val = cash
        for p in raw_portfolio:
            if "_" in p.symbol:
                try:
                    underlying, opt_type_char, strike_str, expiry_str = p.symbol.split('_')
                    opt_type = "call" if opt_type_char.upper() == "C" else "put"
                    strike = float(strike_str)
                    expiry = float(expiry_str)
                    cp = live_prices.get(underlying, 0.0)
                    if cp > 0.0:
                        sim_spot = cp * (1.0 + shock)
                        sim_res = Pricer().price(
                            model="bsm", spot=sim_spot, strike=strike,
                            vol=0.20, rate=0.05, expiry=expiry, option_type=opt_type
                        )
                        sim_val += sim_res.price * p.quantity * 100
                except:
                    pass
            else:
                cp = live_prices.get(p.symbol, 0.0)
                if cp > 0.0:
                    sim_price = cp * (1.0 + shock)
                    sim_val += sim_price * p.quantity
        sim_pnl = sim_val - current_equity
        pnl_points.append(sim_pnl)

    # Build Plotly Figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[s * 100 for s in shocks],
        y=pnl_points,
        mode='lines+markers',
        name='Portfolio Shock PnL',
        line=dict(color=C['cyan'], width=3),
        marker=dict(size=8, color=C['blue']),
        fill='tozeroy',
        fillcolor='rgba(6, 182, 212, 0.1)'
    ))
    fig.update_layout(
        title="Portfolio Shock Stress Test (Spot Price Shift)",
        xaxis_title="Underlying Spot Shock (%)",
        yaxis_title="Estimated PnL (₹)",
        template="plotly_dark",
        margin=dict(l=50, r=30, t=50, b=40),
        height=320,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
    )

    holdings_children = [
        html.H4("Current Positions", style={'margin': '0 0 20px 0', 'color': C['text'], 'borderBottom': '1px solid rgba(255,255,255,0.1)', 'paddingBottom': '15px'}),
        table_ui
    ]

    return stats_children, greeks_children, holdings_children, fig

# ── 3. DASHBOARD MAIN SCREEN ─────────────────────────────────────────────────
def render_dashboard(username):
    try:
        tier      = engine.get_subscription_tier(username)
        uses_left = engine.get_remaining_uses(username)
    except:
        tier, uses_left = "Unknown", 0

    stats_children, greeks_children, holdings_children, risk_fig = get_portfolio_views(username)

    return html.Div([
        # ── Dashboard Auto Refresh Interval (5 seconds) ──
        dcc.Interval(id='portfolio-refresh-interval', interval=5000, n_intervals=0),

        # ── Header Dashboard (Logouts & Subscription info) ──
        html.Div(className='glass-card animate-fade-up', style={'padding': '20px 30px', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '30px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '15px'}, children=[
                html.Div('', style={'fontSize': '24px', 'color': C['blue']}),
                html.Div([
                    html.H3(f"Welcome, {username}", style={'margin': '0', 'color': C['text']}),
                    html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'marginTop': '4px'}, children=[
                        html.Span(className='live-status'),
                        html.Span("LIVE CONNECTION", style={'color': C['green'], 'fontSize': '12px', 'textTransform': 'uppercase', 'letterSpacing': '1px'})
                    ])
                ])
            ]),
            
            html.Div(style={'display': 'flex', 'gap': '15px', 'alignItems': 'center'}, children=[
                html.Div(style={'padding': '8px 15px', 'background': 'rgba(251, 191, 36, 0.1)', 'border': f'1px solid {C["gold"]}', 'borderRadius': '20px', 'color': C['gold'], 'fontSize': '13px', 'fontWeight': 'bold'}, children=f"Tier: {tier}"),
                html.Div(style={'padding': '8px 15px', 'background': 'rgba(59, 130, 246, 0.1)', 'border': f'1px solid {C["blue"]}', 'borderRadius': '20px', 'color': C['blue'], 'fontSize': '13px', 'fontWeight': 'bold'}, children=f"Credits: {uses_left}"),
                html.Button("Logout", id='btn-logout', style={'padding': '8px 15px', 'background': 'transparent', 'color': C['red'], 'border': f'1px solid {C["red"]}', 'borderRadius': '20px', 'cursor': 'pointer', 'fontSize': '13px', 'fontWeight': 'bold'})
            ])
        ]),

        # ── Stat Cards Row ──
        html.Div(id='portfolio-stats-row', className='animate-fade-up delay-1', style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=stats_children),

        # ── Greeks Row ──
        html.Div(id='portfolio-greeks-row', className='animate-fade-up delay-2', style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}, children=greeks_children),

        # ── Main Content (Trade + Table) ──
        html.Div(style={'display': 'flex', 'gap': '30px', 'alignItems': 'flex-start'}, children=[
            # Left: Trade Panel
            html.Div(className='glass-card animate-fade-left delay-2', style={'width': '350px', 'padding': '30px', 'flexShrink': '0'}, children=[
                html.H4("Trade Terminal", style={'margin': '0 0 20px 0', 'color': C['text'], 'borderBottom': '1px solid rgba(255,255,255,0.1)', 'paddingBottom': '15px'}),
                
                dcc.RadioItems(id='order-type', options=[{'label': ' BUY', 'value': 'BUY'}, {'label': ' SELL', 'value': 'SELL'}], value='BUY', inline=True, style={'marginBottom': '15px', 'fontWeight': 'bold', 'color': C['text']}),
                
                # New Asset Selector
                html.Div(style={'marginBottom': '15px'}, children=[
                    html.Label("Asset Class", style={'color': C['muted'], 'fontSize': '11px', 'fontWeight': 'bold', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.RadioItems(id='trade-asset-type', options=[{'label': ' Stock  ', 'value': 'STOCK'}, {'label': ' Option', 'value': 'OPTION'}], value='STOCK', inline=True, style={'fontWeight': '500', 'color': C['text']})
                ]),

                # Option pricing parameters
                html.Div(id='trade-option-config-div', style={'display': 'none', 'background': 'rgba(255,255,255,0.02)', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid rgba(255,255,255,0.05)'}, children=[
                    html.Label("Option Type", style={'color': C['muted'], 'fontSize': '11px', 'fontWeight': 'bold'}),
                    dcc.RadioItems(id='trade-opt-type', options=[{'label': ' Call  ', 'value': 'CALL'}, {'label': ' Put', 'value': 'PUT'}], value='CALL', inline=True, style={'marginBottom': '10px', 'color': C['text']}),
                    
                    html.Label("Strike Price (₹)", style={'color': C['muted'], 'fontSize': '11px', 'fontWeight': 'bold'}),
                    dcc.Input(id='trade-strike', type='number', value=100, className='modern-input', style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}),
                    
                    html.Label("Expiry (Years)", style={'color': C['muted'], 'fontSize': '11px', 'fontWeight': 'bold'}),
                    dcc.Input(id='trade-expiry', type='number', value=0.5, step=0.1, className='modern-input', style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}),

                    html.Label("Implied Volatility (%)", style={'color': C['muted'], 'fontSize': '11px', 'fontWeight': 'bold'}),
                    dcc.Input(id='trade-vol', type='number', value=20, step=1, className='modern-input', style={'width': '100%', 'padding': '8px'})
                ]),

                html.Div(style={'display': 'flex', 'gap': '10px', 'marginBottom': '15px'}, children=[
                    dcc.Input(id='trade-sym', type='text', placeholder='SYMBOL', className='modern-input', style={'flex': '1', 'padding': '12px', 'textTransform': 'uppercase', 'fontFamily': 'JetBrains Mono'}),
                    html.Button('Fetch', id='btn-fetch', className='btn-secondary', style={'padding': '0 20px', 'borderRadius': '8px', 'cursor': 'pointer'})
                ]),
                
                dcc.Input(id='trade-name', type='text', placeholder='Company', readOnly=True, className='modern-input', style={'width': '100%', 'padding': '12px', 'marginBottom': '15px', 'opacity': '0.7'}),
                dcc.Input(id='trade-price', type='number', placeholder='Price', readOnly=True, className='modern-input mono-text', style={'width': '100%', 'padding': '12px', 'marginBottom': '15px', 'color': C['green']}),
                dcc.Input(id='trade-qty', type='number', placeholder='Quantity', min=1, className='modern-input', style={'width': '100%', 'padding': '12px', 'marginBottom': '25px'}),
                
                html.Button('Execute Trade', id='btn-execute', className='btn-neon', style={'width': '100%', 'padding': '15px', 'fontSize': '15px', 'cursor': 'pointer'}),
                html.Div(id='trade-msg', style={'marginTop': '15px', 'textAlign': 'center', 'height': '40px', 'fontSize': '13px'})
            ]),

            # Right: Holdings Table
            html.Div(id='portfolio-holdings', className='glass-card animate-fade-right delay-3', style={'flex': '1', 'padding': '30px'}, children=holdings_children)
        ]),

        # ── Stress Test PnL Shock Curve ──
        html.Div(className='glass-card animate-fade-up delay-4', style={'marginTop': '30px', 'padding': '30px'}, children=[
            html.H4("Portfolio Risk Stress Test (PnL Shock Curve)", style={'margin': '0 0 20px 0', 'color': C['text'], 'borderBottom': '1px solid rgba(255,255,255,0.1)', 'paddingBottom': '15px'}),
            dcc.Graph(id='portfolio-risk-chart', figure=risk_fig)
        ])
    ])


# ── 4. CALLBACKS ─────────────────────────────────────────────────────────────
@callback(Output('main-content-container', 'children'), Input('session-user', 'data'))
def route_page(username):
    if not username: return render_login_screen()
    return render_dashboard(username)

# ---> CALLBACK 1: Toggle Option parameter display
@callback(
    Output('trade-option-config-div', 'style'),
    Input('trade-asset-type', 'value')
)
def toggle_option_config(asset_type):
    if asset_type == 'OPTION':
        return {'background': 'rgba(255,255,255,0.02)', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid rgba(255,255,255,0.05)'}
    return {'display': 'none'}

# ---> CALLBACK 2: Login and Register
@callback(
    [Output('session-user', 'data'), Output('auth-msg', 'children'), Output('auth-msg', 'style')],
    [Input('btn-login', 'n_clicks'), Input('btn-register', 'n_clicks')],
    [State('auth-user', 'value'), State('auth-pass', 'value')],
    prevent_initial_call=True
)
def handle_login_register(btn_login, btn_register, user, pwd):
    print(f"DEBUG: handle_login_register called. btn_login={btn_login}, btn_register={btn_register}, user={user}")
    base_style = {'marginTop': '18px', 'textAlign': 'center', 'height': '18px', 'fontSize': '12px', 'fontFamily': 'JetBrains Mono, monospace'}
    ctx = dash.callback_context
    if not ctx.triggered: return no_update, "", base_style
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not user or not pwd: 
        print("DEBUG: missing user or pwd")
        return no_update, "Please enter username and password", {**base_style, 'color': C['red']}
        
    try:
        if btn_id == 'btn-register':
            print(f"DEBUG: Attempting to create user {user}")
            if engine.create_user(user, pwd, 10000.0): 
                print("DEBUG: User created successfully!")
                return user, "✓ Account created.", {**base_style, 'color': C['green']}
            print("DEBUG: User already exists!")
            return no_update, "Username exists.", {**base_style, 'color': C['red']}
        elif btn_id == 'btn-login':
            if engine.authenticate_user(user, pwd): 
                print("DEBUG: Authenticated successfully!")
                return user, "✓ Authenticated.", {**base_style, 'color': C['green']}
            print("DEBUG: Invalid credentials!")
            return no_update, "Invalid credentials.", {**base_style, 'color': C['red']}
    except Exception as e: 
        print(f"DEBUG: DB Error: {e}")
        return no_update, f"DB Error: {e}", {**base_style, 'color': C['red']}
    return no_update, "", base_style

# ---> CALLBACK 3: Logout
@callback(
    Output('session-user', 'data', allow_duplicate=True),
    Input('btn-logout', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks is None:
        return dash.no_update
    return None

# ---> CALLBACK 4: Fetch Live Data & Options Premium
@callback(
    [Output('trade-name', 'value'), Output('trade-price', 'value'), Output('trade-msg', 'children'), Output('trade-msg', 'style')],
    Input('btn-fetch', 'n_clicks'),
    [
        State('trade-asset-type', 'value'),
        State('trade-sym', 'value'),
        State('trade-opt-type', 'value'),
        State('trade-strike', 'value'),
        State('trade-expiry', 'value'),
        State('trade-vol', 'value'),
    ],
    prevent_initial_call=True
)
def fetch_live_data(n_clicks, asset_type, sym, opt_type, strike, expiry, vol):
    if not sym: return "", "", "Enter a symbol.", {'color': C['red']}
    try:
        ticker = yf.Ticker(sym.upper())
        price = ticker.fast_info['lastPrice']
        currency = ticker.fast_info['currency'] if 'currency' in ticker.fast_info else 'USD'
        
        fx_tag = f" ({currency} to USD)" if currency != 'USD' else ""
        if currency != 'USD':
            try:
                fx_ticker = yf.Ticker(f"{currency}USD=X")
                rate = fx_ticker.fast_info['lastPrice']
                price = price * rate
            except:
                pass

        if asset_type == 'STOCK':
            name = ticker.info.get('shortName', sym.upper())
            return name, round(price, 2), f"✓ {sym.upper()} fetched{fx_tag}.", {'color': C['green']}
        else:
            # OPTION
            strike = float(strike)
            expiry = float(expiry)
            vol_val = float(vol) / 100.0
            
            res = Pricer().price(
                model="bsm", spot=price, strike=strike, vol=vol_val,
                rate=0.05, expiry=expiry, option_type=opt_type.lower()
            )
            name = f"{sym.upper()} ₹{strike} {opt_type.capitalize()} (Exp: {expiry}y)"
            return name, round(res.price, 2), f"✓ Option premium computed dynamically.", {'color': C['green']}
    except Exception as ex: 
        return "", "", f"Failed to fetch: {ex}", {'color': C['red']}

# ---> CALLBACK 5: Execute Trades (Stocks & Options)
@callback(
    [Output('main-content-container', 'children', allow_duplicate=True), Output('trade-msg', 'children', allow_duplicate=True)],
    Input('btn-execute', 'n_clicks'),
    [
        State('session-user', 'data'),
        State('order-type', 'value'),
        State('trade-asset-type', 'value'),
        State('trade-sym', 'value'),
        State('trade-name', 'value'),
        State('trade-qty', 'value'),
        State('trade-price', 'value'),
        State('trade-opt-type', 'value'),
        State('trade-strike', 'value'),
        State('trade-expiry', 'value'),
    ],
    prevent_initial_call=True
)
def execute_trade(clicks, username, order_type, asset_type, sym, name, qty, price, opt_type, strike, expiry):
    if clicks is None: 
        return dash.no_update, dash.no_update
    if not sym or not qty or not price: return dash.no_update, "Fill all fields."
    if not engine.use_advanced_feature(username):
        return dash.no_update, html.Span("⚡ Credit limit reached. Upgrade plan.", style={'color': C['red']})
    try:
        if asset_type == 'STOCK':
            trade_symbol = sym.upper()
            trade_name = name
        else:
            trade_symbol = f"{sym.upper()}_{'C' if opt_type.upper() == 'CALL' else 'P'}_{strike}_{expiry}"
            trade_name = name
            
        if order_type == 'BUY': 
            engine.buy_stock(username, trade_symbol, trade_name, int(qty), float(price))
        else: 
            engine.sell_stock(username, trade_symbol, int(qty), float(price))
            
        return render_dashboard(username), html.Span(f"✓ Order executed.", style={'color': C['green']})
    except Exception as e: 
        return dash.no_update, html.Span(f"Error: {e}", style={'color': C['red']})

# ---> CALLBACK 6: Auto Refresh Dashboard, Greeks, and PnL Shock curve
@callback(
    [
        Output('portfolio-stats-row', 'children'), 
        Output('portfolio-greeks-row', 'children'), 
        Output('portfolio-holdings', 'children'),
        Output('portfolio-risk-chart', 'figure')
    ],
    Input('portfolio-refresh-interval', 'n_intervals'),
    State('session-user', 'data'),
    prevent_initial_call=True
)
def auto_refresh_portfolio(n_intervals, username):
    if not username: return no_update, no_update, no_update, no_update
    stats, greeks, holdings, risk_fig = get_portfolio_views(username)
    return stats, greeks, holdings, risk_fig