#include "data_provider.h"

#include <iostream>
#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
#include <grpcpp/security/credentials.h>
#include "tick_thread.h"
#include "bidask_thread.h"
#include "subject_thread.h"
#include "time_info.h"
#include "time_thread.h"
#include "stock_object.h"
#include "plugin/chooser/topamount.h"
#include "util/morning_timer.h"
#include "stock_server/plugin/chooser/chooserplugin.h"
#include <QDebug>


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


DataProvider::DataProvider()
: QObject(0), stub_(Stock::NewStub(grpc::CreateChannel("localhost:50052", grpc::InsecureChannelCredentials()))){
    chooserPlugin = new TopAmount(&object_map);
    tickHandleTimer = new MorningTimer(1000, this);
}


DataProvider::~DataProvider() {
}


void DataProvider::startListenTicks() {
    TickThread * tthread = new TickThread(stub_);
    QObject::connect(tthread, SIGNAL(tickArrived(CybosTickData *)), SLOT(stockTickHandler(CybosTickData *)));
    tthread->start();
    BidAskThread * bthread = new BidAskThread(stub_);
    QObject::connect(bthread, SIGNAL(tickArrived(CybosBidAskTickData *)), SLOT(bidAskTickHandler(CybosBidAskTickData *)));
    bthread->start();
    SubjectThread * sthread = new SubjectThread(stub_);
    QObject::connect(sthread, SIGNAL(tickArrived(CybosSubjectTickData *)), SLOT(subjectTickHandler(CybosSubjectTickData *)));
    // Caution: Timer should be created after set simulation time since morning timer read from it
    connect(tickHandleTimer, SIGNAL(timeout()), SLOT(processTick()));
    tickHandleTimer->start();
    chooserPlugin->start();
}


void DataProvider::processTick() {
    qWarning() << "processTick : " << TimeInfo::getInstance().getCurrentDateTime();
    QMapIterator<QString, StockObject *> i(object_map);
    while (i.hasNext()) {
        StockObject * sobj = i.next().value();
        sobj->processTickData();
    }
}


void DataProvider::createStockObject(const QString &code) {
    if (!object_map.contains(code))
        object_map[code] = new StockObject(code, this);
}


void DataProvider::stockTickHandler(CybosTickData * data) {
    QString code_str(QString::fromStdString(data->code()));
    createStockObject(code_str);
    object_map[code_str]->handleTickData(data);
}


void DataProvider::bidAskTickHandler(CybosBidAskTickData *data) {
    QString code_str(QString::fromStdString(data->code()));
    createStockObject(code_str);
    object_map[code_str]->handleBidAskData(data);
}


void DataProvider::subjectTickHandler(CybosSubjectTickData *data) {
    QString code_str(QString::fromStdString(data->code()));
    createStockObject(code_str);
    object_map[code_str]->handleSubjectData(data);
}


void DataProvider::requestStockTick(const std::string &code) {
    ClientContext context;
    StockCodeQuery code_query;
    Empty empty;
    code_query.set_code(code);
    stub_->RequestCybosTickData(&context, code_query, &empty);
}


void DataProvider::requestBidAskTick(const std::string &code) {
    ClientContext context;
    StockCodeQuery code_query;
    Empty empty;
    code_query.set_code(code);
    stub_->RequestCybosBidAsk(&context, code_query, &empty);
}


void DataProvider::requestSubjectTick(const std::string &code) {
    ClientContext context;
    StockCodeQuery code_query;
    Empty empty;
    code_query.set_code(code);
    stub_->RequestCybosSubject(&context, code_query, &empty);
}


void DataProvider::startSimulation(time_t from_time) {
    ClientContext context;
    Empty empty;
    SimulationArgument sa;
    Timestamp * ts = new Timestamp(TimeUtil::TimeTToTimestamp(from_time));
    sa.set_allocated_from_datetime(ts);
    TimeThread * tthread = new TimeThread(stub_);
    connect(tthread, SIGNAL(timeInfoArrived(Timestamp *)), &(TimeInfo::getInstance()), SLOT(timeInfoArrived(Timestamp *)));
    tthread->start();
    TimeInfo::getInstance().timeInfoArrived(ts);
    stub_->StartSimulation(&context, sa, &empty);
    startListenTicks();
}


StockObject * DataProvider::getStockObject(const QString &code) {
    if (object_map.contains(code))
        return object_map[code];
    return NULL;
}


CybosDayDatas * DataProvider::requestStockDayData(const std::string &code, time_t from_date, time_t until_date) {
    ClientContext context;
    CybosDayDatas * data = new CybosDayDatas;
    StockQuery stock_query;
    stock_query.set_code(code);
    Timestamp *from_timestamp = new Timestamp(TimeUtil::TimeTToTimestamp(from_date));
    Timestamp *until_timestamp = new Timestamp(TimeUtil::TimeTToTimestamp(until_date));
    stock_query.set_allocated_from_datetime(from_timestamp);
    stock_query.set_allocated_until_datetime(until_timestamp);
    stub_->GetDayData(&context, stock_query, data);
    return data;
    /*
    for (int i = 0; i < data.day_data_size(); ++i) {
        CybosDayData d = data.day_data(i);
        std::cout << "price: " << d.start_price() << "\ttime: " << d.date() << std::endl;
    }
    */
}


QStringList DataProvider::requestYesterdayTopAmount(const QDateTime &dt) {
    ClientContext context;
    CodeList data;
    Timestamp request_timestamp(TimeUtil::TimeTToTimestamp(dt.toTime_t()));
    stub_->GetYesterdayTopAmountCodes(&context, request_timestamp, &data);
    QStringList codeList;
    for (int i = 0; i < data.codelist_size(); ++i) {
        codeList.append(QString::fromStdString(data.codelist(i)));
    }
    return codeList;
}
