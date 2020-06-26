#include "DataProvider.h"
#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
#include <grpcpp/security/credentials.h>
#include <google/protobuf/util/time_util.h>
#include "TickThread.h"
#include "TimeThread.h"
#include "BidAskThread.h"
#include "StockSelectionThread.h"
#include "SpeedStatistics.h"
#include "MinuteData.h"
#include "DayDataProvider.h"


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
    minuteData = NULL;
    tickThread = new TickThread(stub_);
    bidAskThread = new BidAskThread(stub_);
    stockSelectionThread = new StockSelectionThread(stub_);
    timeThread = new TimeThread(stub_);
    dayDataProvider = new DayDataProvider(stub_);

    connect(tickThread, &TickThread::tickArrived, this, &DataProvider::tickArrived);
    connect(bidAskThread, &BidAskThread::tickArrived, this, &DataProvider::bidAskTickArrived);
    connect(stockSelectionThread, &StockSelectionThread::stockCodeChanged, this, &DataProvider::stockCodeChanged);
    connect(dayDataProvider, &DayDataProvider::dataReady, this, &DataProvider::dayDataReady);
    connect(dayDataProvider, &DayDataProvider::minuteDataReady, this, &DataProvider::minuteDataReady);
}


void DataProvider::createSpeedStatistics(int secs) {
    if (speedStatistics == NULL)
        speedStatistics = new SpeedStatistics(secs, this);
}


void DataProvider::requestDayData(const QString &code, int countOfDays, const QDateTime &_untilTime) {
    dayDataProvider->requestDayData(code, countOfDays, _untilTime);
}


void DataProvider::requestMinuteData(const QString &code, const QDateTime &fromTime, const QDateTime &untilTime) {
    dayDataProvider->requestMinuteData(code, fromTime, untilTime);
}


void DataProvider::collectMinuteData(int min) {
    if (minuteData == NULL) {
        minuteData = new MinuteData(this, min);
        connect(tickThread, &TickThread::tickArrived, minuteData, &MinuteData::stockTickArrived);
        connect(minuteData, &MinuteData::minuteTickUpdated, this, &DataProvider::minuteTickUpdated);
    }
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


void DataProvider::setCurrentStock(const QString &code, const QDateTime &dt, int countOfDays) {
    stockSelectionThread->setCurrentStock(code, dt, countOfDays);
}


MinuteTick * DataProvider::getMinuteTick(const QString &code) {
    if (minuteData && !code.isEmpty())
        return minuteData->getMinuteTick(code);
    return nullptr;
}
