#include "quantiv/core/portfolio_engine.h"
#include <iostream>
#include <stdexcept>

QuantivPortfolioEngine::QuantivPortfolioEngine() {
    // UPDATE THIS with your actual Postgres credentials if they are different!
    conn_string = "dbname=quantivdb user=postgres password=postgres hostaddr=127.0.0.1 port=5432";
    
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        
        // Auto-create tables if they don't exist
        w.exec("CREATE TABLE IF NOT EXISTS users (username VARCHAR(50) PRIMARY KEY, password VARCHAR(255), tier VARCHAR(20), cash FLOAT, credits INT)");
        w.exec("CREATE TABLE IF NOT EXISTS portfolio (id SERIAL PRIMARY KEY, username VARCHAR(50), symbol VARCHAR(20), name VARCHAR(100), quantity INT, purchase_price FLOAT)");
        
        // Ensure our test admin exists
        w.exec("INSERT INTO users (username, password, tier, cash, credits) VALUES ('admin', 'password', 'Pro', 10000.0, 100) ON CONFLICT DO NOTHING");
        
        w.commit();
    } catch (const std::exception &e) {
        std::cerr << "[DB Warning] Failed to connect to Postgres. Is it running? " << e.what() << std::endl;
    }
}

bool QuantivPortfolioEngine::create_user(const std::string& username, const std::string& password, double cash) {
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        w.exec_params("INSERT INTO users (username, password, tier, cash, credits) VALUES ($1, $2, 'Basic', $3, 10)", username, password, cash);
        w.commit();
        return true;
    } catch (...) { return false; }
}

bool QuantivPortfolioEngine::authenticate_user(const std::string& username, const std::string& password) {
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        pqxx::result r = w.exec_params("SELECT password FROM users WHERE username = $1", username);
        if (!r.empty() && r[0][0].as<std::string>() == password) return true;
    } catch (...) {}
    return false;
}

std::string QuantivPortfolioEngine::get_subscription_tier(const std::string& username) {
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        pqxx::result r = w.exec_params("SELECT tier FROM users WHERE username = $1", username);
        if (!r.empty()) return r[0][0].as<std::string>();
    } catch (...) {}
    return "Basic";
}

double QuantivPortfolioEngine::get_available_cash(const std::string& username) {
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        pqxx::result r = w.exec_params("SELECT cash FROM users WHERE username = $1", username);
        if (!r.empty()) return r[0][0].as<double>();
    } catch (...) {}
    return 0.0;
}

std::vector<Position> QuantivPortfolioEngine::get_user_portfolio(const std::string& username) {
    std::vector<Position> portfolio;
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        pqxx::result r = w.exec_params("SELECT symbol, name, quantity, purchase_price FROM portfolio WHERE username = $1", username);
        for (auto row : r) {
            Position p;
            p.symbol = row[0].as<std::string>();
            p.name = row[1].as<std::string>();
            p.quantity = row[2].as<int>();
            p.purchase_price = row[3].as<double>();
            p.current_total_value = p.quantity * p.purchase_price; // simplified calculation
            portfolio.push_back(p);
        }
    } catch (...) {}
    return portfolio;
}

double QuantivPortfolioEngine::get_portfolio_value(const std::string& username) {
    double cash = get_available_cash(username);
    double stock_val = 0.0;
    auto port = get_user_portfolio(username);
    for (const auto& p : port) stock_val += p.current_total_value;
    return cash + stock_val;
}

int QuantivPortfolioEngine::get_remaining_uses(const std::string& username) {
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        pqxx::result r = w.exec_params("SELECT credits FROM users WHERE username = $1", username);
        if (!r.empty()) return r[0][0].as<int>();
    } catch (...) {}
    return 0;
}

bool QuantivPortfolioEngine::upgrade_subscription(const std::string& username, const std::string& tier) {
    try {
        int new_credits = (tier == "Plus") ? 50 : 100;
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        w.exec_params("UPDATE users SET tier = $1, credits = $2 WHERE username = $3", tier, new_credits, username);
        w.commit();
        return true;
    } catch (...) { return false; }
}

bool QuantivPortfolioEngine::use_advanced_feature(const std::string& username) {
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        pqxx::result r = w.exec_params("SELECT credits FROM users WHERE username = $1 FOR UPDATE", username);
        if (!r.empty()) {
            int credits = r[0][0].as<int>();
            if (credits > 0) {
                w.exec_params("UPDATE users SET credits = credits - 1 WHERE username = $1", username);
                w.commit();
                return true;
            }
        }
    } catch (...) {}
    return false;
}

void QuantivPortfolioEngine::buy_stock(const std::string& username, const std::string& sym, const std::string& name, int qty, double price) {
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        double cost = qty * price;
        
        pqxx::result r = w.exec_params("SELECT cash FROM users WHERE username = $1", username);
        if (r.empty() || r[0][0].as<double>() < cost) throw std::runtime_error("Insufficient funds");
        
        w.exec_params("UPDATE users SET cash = cash - $1 WHERE username = $2", cost, username);
        w.exec_params("INSERT INTO portfolio (username, symbol, name, quantity, purchase_price) VALUES ($1, $2, $3, $4, $5)", username, sym, name, qty, price);
        w.commit();
    } catch (const std::exception& e) {
        throw;
    }
}

void QuantivPortfolioEngine::sell_stock(const std::string& username, const std::string& sym, int qty, double price) {
    try {
        pqxx::connection c(conn_string);
        pqxx::work w(c);
        
        pqxx::result r = w.exec_params("SELECT id, quantity FROM portfolio WHERE username = $1 AND symbol = $2 LIMIT 1", username, sym);
        if (r.empty()) throw std::runtime_error("Stock not found");
        
        int id = r[0][0].as<int>();
        int current_qty = r[0][1].as<int>();
        
        if (current_qty < qty) throw std::runtime_error("Not enough shares");
        
        if (current_qty == qty) {
            w.exec_params("DELETE FROM portfolio WHERE id = $1", id);
        } else {
            w.exec_params("UPDATE portfolio SET quantity = quantity - $1 WHERE id = $2", qty, id);
        }
        
        w.exec_params("UPDATE users SET cash = cash + $1 WHERE username = $2", qty * price, username);
        w.commit();
    } catch (const std::exception& e) {
        throw;
    }
}