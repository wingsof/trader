#include "DataProvider.h"
#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
#include <grpcpp/security/credentials.h>
#include <google/protobuf/util/time_util.h>
#include "TickThread.h"
#include "BidAskThread.h"
#include "StockSelectionThread.h"
#include "SpeedStatistics.h"


using grpc::Channel;
using grpc::ClientContext;
using grpc::ClientReader;
using grpc::ClientReaderWriter;
using grpc::ClientWriter;
using grpc::Status;
using google::protobuf::util::TimeUtil;
using google::protobuf::Timestamp;
using google::protobuf::Empty;

using stock_api::Stock;
using stock_api::StockCodeQuery;
using stock_api::StockQuery;
using stock_api::CybosDayData;
using stock_api::CodeList;
using stock_api::SimulationArgument;

using grpc::ClientContext;
using stock_api::StockQuery;

using stock_api::CybosTickData;
using stock_api::CybosDayDatas;
using stock_api::CybosBidAskTickData;
using stock_api::CybosSubjectTickData;
using google::protobuf::Timestamp;


DataProvider::DataProvider()
: QObject(0) {
    setenv("TZ", "UTC", 1);
    qRegisterMetaType<CybosTickData>("CybosTickData");
    qRegisterMetaType<CybosDayDatas>("CybosDayDatas");
    qRegisterMetaType<CybosBidAskTickData>("CybosBidAskTickData");
    qRegisterMetaType<CybosSubjectTickData>("CybosSubjectTickData");
    qRegisterMetaType<Timestamp>("Timestamp");

    stub_ = Stock::NewStub(grpc::CreateChannel("localhost:50052", grpc::InsecureChannelCredentials()));

    speedStatistics = NULL;
    tickThread = new TickThread(stub_);
    bidAskThread = new BidAskThread(stub_);
    stockSelectionThread = new StockSelectionThread(stub_);
    connect(tickThread, &TickThread::tickArrived, this, &DataProvider::tickArrived);
    connect(bidAskThread, &BidAskThread::tickArrived, this, &DataProvider::bidAskTickArrived);
    connect(stockSelectionThread, &StockSelectionThread::stockCodeChanged, this, &DataProvider::stockCodeChanged);
}


void DataProvider::createSpeedStatistics(int secs) {
    if (speedStatistics == NULL)
        speedStatistics = new SpeedStatistics(secs, this);
}


void DataProvider::startStockTick() {
    tickThread->start();
}


void DataProvider::startBidAskTick() {
    bidAskThread->start();
}


void DataProvider::startStockCodeListening() {
    stockSelectionThread->start();
}
