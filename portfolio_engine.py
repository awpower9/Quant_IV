"""
quantiv_engine.py — Python-based User & Portfolio Management
Replaces the old C++ database engine.
"""

class Position:
    def __init__(self, sym, name, qty, price):
        self.symbol = sym
        self.name = name
        self.quantity = qty
        self.purchase_price = price
        self.current_total_value = qty * price

class QuantivPortfolioEngine:
    def __init__(self):
        # In-memory database (Resets on server restart)
        # You can replace this with SQLite later!
        self.users = {
            "admin": {"pwd": "password", "tier": "Pro", "cash": 10000.0, "credits": 100, "portfolio": []}
        }

    def authenticate_user(self, username, password):
        user = self.users.get(username)
        return user is not None and user['pwd'] == password

    def create_user(self, username, password, cash):
        if username in self.users: 
            return False
        self.users[username] = {"pwd": password, "tier": "Basic", "cash": cash, "credits": 10, "portfolio": []}
        return True

    def get_subscription_tier(self, username):
        return self.users.get(username, {}).get("tier", "Basic")

    def get_available_cash(self, username):
        return self.users.get(username, {}).get("cash", 0.0)

    def get_portfolio_value(self, username):
        user = self.users.get(username, {})
        cash = user.get("cash", 0.0)
        stock_value = sum(p.current_total_value for p in user.get("portfolio", []))
        return cash + stock_value

    def get_user_portfolio(self, username):
        return self.users.get(username, {}).get("portfolio", [])

    def get_remaining_uses(self, username):
        return self.users.get(username, {}).get("credits", 0)

    def upgrade_subscription(self, username, tier):
        if username in self.users:
            self.users[username]["tier"] = tier
            self.users[username]["credits"] = 50 if tier == "Plus" else 100
            return True
        return False

    def use_advanced_feature(self, username):
        user = self.users.get(username)
        if user and user["credits"] > 0:
            user["credits"] -= 1
            return True
        return False

    def buy_stock(self, username, sym, name, qty, price):
        user = self.users.get(username)
        if user:
            cost = qty * price
            if user["cash"] >= cost:
                user["cash"] -= cost
                user["portfolio"].append(Position(sym, name, qty, price))
            else:
                raise Exception("Insufficient funds")

    def sell_stock(self, username, sym, qty, price):
        user = self.users.get(username)
        if not user: return
        
        for i, pos in enumerate(user["portfolio"]):
            if pos.symbol == sym:
                if pos.quantity >= qty:
                    pos.quantity -= qty
                    user["cash"] += qty * price
                    if pos.quantity == 0:
                        user["portfolio"].pop(i)
                    return
                else:
                    raise Exception("Not enough shares to sell")
        raise Exception("Stock not found in portfolio")