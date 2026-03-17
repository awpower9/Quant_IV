"""
intro_page.py — Educational introduction to options.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

def intro_layout() -> html.Div:
    """Create the educational introduction page layout."""
    
    intro_markdown = """
## What is an Option?
Imagine you want to buy a house that costs $500,000, but you need a few months to save up. You could pay the seller a $5,000 fee right now to buy the **"option"** to purchase the house at exactly $500,000 anytime in the next 3 months—no matter what happens to the overall housing market!

If house prices skyrocket to $600,000, you're thrilled! You still securely get to buy it for $500,000. If house prices crash to $400,000, you simply walk away and lose nothing except the $5,000 fee you paid upfront.

This is exactly how stock options work. An **Option** is a contract that gives you the *right* (but not the obligation) to buy or sell a stock at a locked-in price by a certain date.

There are two main types of options:
- **Call Option**: Gives you the right to **buy** the stock. You buy this if you think the stock is going to shoot up.
- **Put Option**: Gives you the right to **sell** the stock. You buy this if you think the stock is going to crash (just like buying insurance).

---

## The 5 Core Ingredients
To figure out how much that $5,000 upfront "fee" (the option's price) should realistically cost, professional traders and mathematical algorithms use exactly 5 basic ingredients:

### 1. Spot Price ($S_0$) - *Where are we now?*
This is the current real-world market price of the stock right now. If Apple stock is trading at $150 today, the Spot Price is $150. Everything hinges on where this price moves.

### 2. Strike Price ($K$) - *Your Locked-In Deal*
The **Strike Price** is the exact price you locked into your contract. 
- If you own a **Call** with a $100 strike, you hold the golden ticket to buy the stock for $100, even if the real market price shoots to $1,000!

### 3. Time to Expiry ($T$) - *The Ticking Clock*
Options are exactly like milk; they have a strict expiration date. **Time to Expiry** is exactly how much time is left until your contract becomes completely worthless. The more time you have left, the more expensive the option is, because there's a higher runway for the stock price to do something crazy in your favor!

### 4. Volatility ($\sigma$) - *The Wildcard*
**Volatility** measures how wild and aggressively the stock's price swings. A boring utility company has very low volatility. A crazy new tech startup has massive volatility. High volatility physically makes options *much more expensive* because massive price swings mean massive potential payouts.

### 5. Risk-Free Interest Rate ($r$) - *The Benchmark*
This is the completely safe interest rate you could get by just putting your cash in a basic bank savings account. It acts merely as a mathematical baseline to compare trades against.

---

## "Moneyness" - Are we winning?
Traders proudly use three simple terms to describe if an option is currently profitable:

- **In-The-Money (ITM)**: You are currently winning! If you exercised your right right now, you would literally make money. For example, a Call option to buy at $100 when the stock is currently sitting at $120.
- **At-The-Money (ATM)**: The stock price is exactly equal to your locked-in Strike Price.
- **Out-Of-The-Money (OTM)**: You are currently losing. If your option expired today, it would be completely worthless and you'd lose your upfront fee. 

### Let's play with the models!
Now that you securely know the basics, head to the **Models** page. Play around with these 5 sliders and watch how the different intricate math algorithms physically process them to spit out a perfectly fair "price" for your option!
"""

    return html.Div([
        dbc.Container([
            html.H1("Introduction to Options Trading", className="display-4 fw-bold mb-4 mt-3"),
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(intro_markdown, mathjax=True)
                ])
            ], className="shadow-sm p-4 mb-5 border-0 bg-dark text-light"),
            
            html.Div([
                dbc.Button("Start Pricing Models →", href="/models", color="primary", size="lg")
            ], className="text-center mb-5")
        ], className="py-4")
    ])
