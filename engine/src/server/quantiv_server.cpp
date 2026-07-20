#include <iostream>
#include <memory>
#include <string>
#include <grpcpp/grpcpp.h>
#include "quantiv.grpc.pb.h"
#include "quantiv/core/option.hpp"
#include "quantiv/core/market_data.hpp"
#include "quantiv/models/black_scholes.hpp"
#include "quantiv/models/binomial.hpp"
#include "quantiv/models/trinomial.hpp"
#include "quantiv/models/monte_carlo.hpp"
#include "quantiv/models/pro_engine.hpp"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using quantiv::api::Option;
using quantiv::api::MarketData;
using quantiv::api::PricingRequest;
using quantiv::api::PricingResponse;
using quantiv::api::BinomialRequest;
using quantiv::api::MertonRequest;
using quantiv::api::HestonRequest;
using quantiv::api::QuantivPricer;
using CoreOption = quantiv::core::Option;
using CoreMarketData = quantiv::core::MarketData;

class QuantivPricerServiceImpl final : public QuantivPricer::Service {
    CoreOption ToCoreOption(const Option& opt) {
        return CoreOption(
            opt.strike(),
            opt.expiry(),
            opt.option_type() == quantiv::api::OptionType::CALL ? quantiv::core::OptionType::Call : quantiv::core::OptionType::Put,
            opt.exercise_style() == quantiv::api::ExerciseStyle::EUROPEAN ? quantiv::core::ExerciseStyle::European : quantiv::core::ExerciseStyle::American
        );
    }
    
    CoreMarketData ToCoreMarketData(const MarketData& mkt) {
        return CoreMarketData(mkt.spot(), mkt.vol(), mkt.rate(), mkt.dividend());
    }

    void CopyGreeks(const quantiv::core::PricingResult& res, PricingResponse* response) {
        if (!res.greeks.empty()) {
            auto* greeks_pb = response->mutable_greeks();
            if (res.greeks.count("delta")) greeks_pb->set_delta(res.greeks.at("delta"));
            if (res.greeks.count("gamma")) greeks_pb->set_gamma(res.greeks.at("gamma"));
            if (res.greeks.count("vega")) greeks_pb->set_vega(res.greeks.at("vega"));
            if (res.greeks.count("theta")) greeks_pb->set_theta(res.greeks.at("theta"));
            if (res.greeks.count("rho")) greeks_pb->set_rho(res.greeks.at("rho"));
        }
    }

    Status PriceBlackScholes(ServerContext* context, const PricingRequest* request, PricingResponse* response) override {
        quantiv::models::BlackScholes pricer;
        auto res = pricer.price(ToCoreOption(request->option()), ToCoreMarketData(request->market()));
        response->set_price(res.price);
        CopyGreeks(res, response);
        return Status::OK;
    }

    Status PriceBinomial(ServerContext* context, const BinomialRequest* request, PricingResponse* response) override {
        quantiv::models::Binomial pricer(request->steps());
        auto res = pricer.price(ToCoreOption(request->option()), ToCoreMarketData(request->market()));
        response->set_price(res.price);
        CopyGreeks(res, response);
        return Status::OK;
    }

    Status PriceTrinomial(ServerContext* context, const BinomialRequest* request, PricingResponse* response) override {
        quantiv::models::Trinomial pricer(request->steps());
        auto res = pricer.price(ToCoreOption(request->option()), ToCoreMarketData(request->market()));
        response->set_price(res.price);
        CopyGreeks(res, response);
        return Status::OK;
    }

    Status PriceMonteCarlo(ServerContext* context, const BinomialRequest* request, PricingResponse* response) override {
        quantiv::models::MonteCarlo pricer(request->steps()); 
        auto res = pricer.price(ToCoreOption(request->option()), ToCoreMarketData(request->market()));
        response->set_price(res.price);
        CopyGreeks(res, response);
        return Status::OK;
    }

    Status PriceMerton(ServerContext* context, const MertonRequest* request, PricingResponse* response) override {
        quantiv::models::ProEngine pricer;
        auto res = pricer.price_merton(ToCoreOption(request->option()), ToCoreMarketData(request->market()), request->lamb(), request->mu_j(), request->sigma_j());
        response->set_price(res.price);
        CopyGreeks(res, response);
        return Status::OK;
    }

    Status PriceHeston(ServerContext* context, const HestonRequest* request, PricingResponse* response) override {
        quantiv::models::ProEngine pricer;
        auto res = pricer.price_heston(ToCoreOption(request->option()), ToCoreMarketData(request->market()), request->kappa(), request->theta(), request->vol_of_vol(), request->rho());
        response->set_price(res.price);
        CopyGreeks(res, response);
        return Status::OK;
    }
};

void RunServer() {
    std::string server_address("0.0.0.0:50051");
    QuantivPricerServiceImpl service;

    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "QuantIV gRPC Server listening on " << server_address << std::endl;
    server->Wait();
}

int main(int argc, char** argv) {
    RunServer();
    return 0;
}
