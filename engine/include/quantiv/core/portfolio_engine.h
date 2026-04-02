#pragma once
#include <string>
#include <vector>
#include <pqxx/pqxx>

struct Position {
    std::string symbol;
    std::string name;
    int quantity;
    double purchase_price;
    double current_total_value;
};

class QuantivPortfolioEngine {
private:
    std::string conn_string;

public:
    QuantivPortfolioEngine();
    
    bool create_user(const std::string& username, const std::string& password, double cash);
    bool authenticate_user(const std::string& username, const std::string& password);
    
    std::string get_subscription_tier(const std::string& username);
    double get_available_cash(const std::string& username);
    double get_portfolio_value(const std::string& username);
    std::vector<Position> get_user_portfolio(const std::string& username);
    int get_remaining_uses(const std::string& username);
    
    bool upgrade_subscription(const std::string& username, const std::string& tier);
    bool use_advanced_feature(const std::string& username);
    
    void buy_stock(const std::string& username, const std::string& sym, const std::string& name, int qty, double price);
    void sell_stock(const std::string& username, const std::string& sym, int qty, double price);
};