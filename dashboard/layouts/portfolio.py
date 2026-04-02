import dash
from dash import dcc, html, callback, Input, Output, State, dash_table, no_update
import pandas as pd
import yfinance as yf
from quantiv import _quantiv_engine



try:
    engine = _quantiv_engine.QuantivPortfolioEngine()
except Exception as e:
    print(f"FAILED TO LOAD C++ ENGINE: {e}")

# Color Palette for inline styles
C = {
    'green': '#10b981', 'red': '#ef4444', 'blue': '#3b82f6', 
    'gold': '#fbbf24', 'muted': '#94a3b8', 'text': '#f8fafc'
}

def portfolio_layout():
  return html.Div([
    
    html.Div(id='main-content-container', style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '40px 20px'})
])

# ── 1. LOGIN SCREEN (Animated) ────────────────────────────────────────────────
def render_login_screen():
    return html.Div(className='animate-fade-up', style={
        'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center',
        'justifyContent': 'center', 'minHeight': '80vh'
    }, children=[
        html.Div(className='glass-card delay-1 animate-fade-up', style={'width': '400px', 'padding': '40px'}, children=[
            
            html.Div(style={'textAlign': 'center', 'marginBottom': '30px'}, children=[
                html.Div('', style={'fontSize': '40px', 'color': C['green'], 'animation': 'float 3s ease-in-out infinite'}),
                html.H2("Quantiv Terminal", style={'color': C['text'], 'margin': '10px 0 5px 0', 'fontWeight': '700'}),
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


# ── 2. DASHBOARD SCREEN (Animated & Glassmorphic) ──────────────────────────────
def render_dashboard(username):
    try:
        tier      = engine.get_subscription_tier(username)
        cash      = engine.get_available_cash(username)
        total_val = engine.get_portfolio_value(username)
        raw_portfolio = engine.get_user_portfolio(username)
        uses_left = engine.get_remaining_uses(username)
    except:
        tier, cash, total_val, raw_portfolio, uses_left = "Unknown", 0.0, 0.0, [], 0

    # Data Table
    if not raw_portfolio:
        table_ui = html.Div(className='glass-card animate-fade-up delay-4', style={'padding': '40px', 'textAlign': 'center'}, children=[
            html.P("Portfolio is empty.", style={'color': C['muted'], 'fontSize': '16px'}),
            html.P("Execute your first trade to populate this table.", style={'color': C['muted'], 'fontSize': '13px', 'opacity': '0.7'})
        ])
    else:
        df = pd.DataFrame([{"Symbol": p.symbol, "Name": p.name, "Qty": p.quantity, "Avg Cost": f"${p.purchase_price:,.2f}", "Total Value": f"${p.current_total_value:,.2f}"} for p in raw_portfolio])
        table_ui = html.Div(className='animate-fade-up delay-4', children=[
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_header={'backgroundColor': 'rgba(0,0,0,0.4)', 'color': C['muted'], 'fontWeight': 'bold', 'border': 'none', 'padding': '15px'},
                style_cell={'backgroundColor': 'rgba(20,20,30,0.4)', 'color': C['text'], 'border': 'none', 'borderBottom': '1px solid rgba(255,255,255,0.05)', 'padding': '15px', 'textAlign': 'left', 'fontFamily': 'Inter'},
                style_data_conditional=[{'if': {'column_id': 'Total Value'}, 'color': C['green'], 'fontWeight': 'bold'}],
            )
        ])

    return html.Div([
        
        # ── Header (With Logout Button!) ──
        html.Div(className='glass-card animate-fade-up', style={'padding': '20px 30px', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '30px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '15px'}, children=[
                html.Div('', style={'fontSize': '24px', 'color': C['blue']}),
                html.Div([
                    html.H3(f"Welcome, {username}", style={'margin': '0', 'color': C['text']}),
                    html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '8px', 'marginTop': '4px'}, children=[
                        html.Span(className='live-status'),
                        html.Span("", style={'color': C['green'], 'fontSize': '12px', 'textTransform': 'uppercase', 'letterSpacing': '1px'})
                    ])
                ])
            ]),
            
            # --- THE USER PILLS & LOGOUT BUTTON ---
            html.Div(style={'display': 'flex', 'gap': '15px', 'alignItems': 'center'}, children=[
                html.Div(style={'padding': '8px 15px', 'background': 'rgba(251, 191, 36, 0.1)', 'border': f'1px solid {C["gold"]}', 'borderRadius': '20px', 'color': C['gold'], 'fontSize': '13px', 'fontWeight': 'bold'}, children=f"Tier: {tier}"),
                html.Div(style={'padding': '8px 15px', 'background': 'rgba(59, 130, 246, 0.1)', 'border': f'1px solid {C["blue"]}', 'borderRadius': '20px', 'color': C['blue'], 'fontSize': '13px', 'fontWeight': 'bold'}, children=f"Credits: {uses_left}"),
                html.Button("Logout", id='btn-logout', style={'padding': '8px 15px', 'background': 'transparent', 'color': C['red'], 'border': f'1px solid {C["red"]}', 'borderRadius': '20px', 'cursor': 'pointer', 'fontSize': '13px', 'fontWeight': 'bold'})
            ])
        ]),

        # ── Stat Cards Row ──
        html.Div(className='animate-fade-up delay-1', style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}, children=[
            html.Div(className='glass-card', style={'flex': '1', 'padding': '25px'}, children=[
                html.P("Total Equity", style={'color': C['muted'], 'fontSize': '13px', 'textTransform': 'uppercase', 'margin': '0 0 10px 0'}),
                html.H1(f"${total_val:,.2f}", className='mono-text', style={'color': C['green'], 'margin': '0', 'fontSize': '36px'})
            ]),
            html.Div(className='glass-card', style={'flex': '1', 'padding': '25px'}, children=[
                html.P("Buying Power", style={'color': C['muted'], 'fontSize': '13px', 'textTransform': 'uppercase', 'margin': '0 0 10px 0'}),
                html.H1(f"${cash:,.2f}", className='mono-text', style={'color': C['text'], 'margin': '0', 'fontSize': '36px'})
            ])
        ]),

        # ── Main Content (Trade + Table) ──
        html.Div(style={'display': 'flex', 'gap': '30px', 'alignItems': 'flex-start'}, children=[
            
            # Left: Trade Panel
            html.Div(className='glass-card animate-fade-left delay-2', style={'width': '350px', 'padding': '30px', 'flexShrink': '0'}, children=[
                html.H4("Trade Terminal", style={'margin': '0 0 20px 0', 'color': C['text'], 'borderBottom': '1px solid rgba(255,255,255,0.1)', 'paddingBottom': '15px'}),
                
                dcc.RadioItems(id='order-type', options=[{'label': ' BUY', 'value': 'BUY'}, {'label': ' SELL', 'value': 'SELL'}], value='BUY', inline=True, style={'marginBottom': '20px', 'fontWeight': 'bold', 'color': C['text']}),
                
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
            html.Div(className='glass-card animate-fade-right delay-3', style={'flex': '1', 'padding': '30px'}, children=[
                html.H4("Current Positions", style={'margin': '0 0 20px 0', 'color': C['text'], 'borderBottom': '1px solid rgba(255,255,255,0.1)', 'paddingBottom': '15px'}),
                table_ui
            ])
        ])
    ])


# ── 3. CALLBACKS ───────────────────────────────────────────────────────────────
@callback(Output('main-content-container', 'children'), Input('session-user', 'data'))
def route_page(username):
    if not username: return render_login_screen()
    return render_dashboard(username)

# ---> CALLBACK 1: Handles Login and Register Only
# ---> CALLBACK 1: Handles Login and Register Only
@callback(
    [Output('session-user', 'data'), Output('auth-msg', 'children'), Output('auth-msg', 'style')],
    [Input('btn-login', 'n_clicks'), Input('btn-register', 'n_clicks')],
    [State('auth-user', 'value'), State('auth-pass', 'value')],
    prevent_initial_call=True
)
def handle_login_register(btn_login, btn_register, user, pwd):
    # FIXED: Replaced the missing FONT variable with the actual font string
    base_style = {'marginTop': '18px', 'textAlign': 'center', 'height': '18px', 'fontSize': '12px', 'fontFamily': 'JetBrains Mono, monospace'}
    
    ctx = dash.callback_context
    if not ctx.triggered: return no_update, "", base_style
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not user or not pwd: return no_update, "⚠ Missing fields.", {**base_style, 'color': C['red']}
    try:
        if btn_id == 'btn-register':
            if engine.create_user(user, pwd, 700.0): return user, "✓ Account created.", {**base_style, 'color': C['green']}
            return no_update, "Username exists.", {**base_style, 'color': C['red']}
        elif btn_id == 'btn-login':
            if engine.authenticate_user(user, pwd): return user, "✓ Authenticated.", {**base_style, 'color': C['green']}
            return no_update, "Invalid credentials.", {**base_style, 'color': C['red']}
    except Exception as e: return no_update, f"DB Error: {e}", {**base_style, 'color': C['red']}
    return no_update, "", base_style


# ---> CALLBACK 2: Handles Logout Only
@callback(
    Output('session-user', 'data', allow_duplicate=True),
    Input('btn-logout', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks is None:
        return dash.no_update
    # Destroys the session token, kicking them back to the login screen
    return None

# ... (Keep fetch_live_data and execute_trade callbacks exactly the same below this) ...

@callback(
    [Output('trade-name', 'value'), Output('trade-price', 'value'), Output('trade-msg', 'children'), Output('trade-msg', 'style')],
    Input('btn-fetch', 'n_clicks'), State('trade-sym', 'value'), prevent_initial_call=True
)
def fetch_live_data(n_clicks, sym):
    if not sym: return "", "", "Enter a symbol.", {'color': C['red']}
    try:
        ticker = yf.Ticker(sym.upper())
        return ticker.info.get('shortName', sym.upper()), round(ticker.fast_info['lastPrice'], 2), f"✓ {sym.upper()} fetched.", {'color': C['green']}
    except: return "", "", f"Failed to fetch {sym.upper()}", {'color': C['red']}

@callback(
    [Output('main-content-container', 'children', allow_duplicate=True), Output('trade-msg', 'children', allow_duplicate=True)],
    Input('btn-execute', 'n_clicks'),
    [State('session-user', 'data'), State('order-type', 'value'), State('trade-sym', 'value'), State('trade-name', 'value'), State('trade-qty', 'value'), State('trade-price', 'value')],
    prevent_initial_call=True
)
def execute_trade(clicks, username, order_type, sym, name, qty, price):
    if clicks is None: 
        return dash.no_update, dash.no_update
    if not sym or not qty or not price: return dash.no_update, "Fill all fields."
    if not engine.use_advanced_feature(username):
        return dash.no_update, html.Span("⚡ Credit limit reached. Upgrade plan.", style={'color': C['red']})
    try:
        if order_type == 'BUY': engine.buy_stock(username, sym.upper(), name, int(qty), float(price))
        else: engine.sell_stock(username, sym.upper(), int(qty), float(price))
        return render_dashboard(username), html.Span(f"✓ Order executed.", style={'color': C['green']})
    except Exception as e: return dash.no_update, html.Span(f"Error: {e}", style={'color': C['red']})