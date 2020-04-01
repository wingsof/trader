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
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;
using stock_api::SimulationArgument;


DataProvider::DataProvider()
: QObject(0), stub_(Stock::NewStub(grpc::CreateChannel("localhost:50052", grpc::InsecureChannelCredentials()))){
    TickThread * tthread = new TickThread(stub_);
    QObject::connect(tthread, SIGNAL(tickArrived(CybosTickData *)), SLOT(stockTickHandler(CybosTickData *)));
    tthread->start();
    BidAskThread * bthread = new BidAskThread(stub_);
    QObject::connect(bthread, SIGNAL(tickArrived(CybosBidAskTickData *)), SLOT(bidAskTickHandler(CybosBidAskTickData *)));
    bthread->start();
    SubjectThread * sthread = new SubjectThread(stub_);
    QObject::connect(sthread, SIGNAL(tickArrived(CybosSubjectTickData *)), SLOT(subjectTickHandler(CybosSubjectTickData *)));
}


DataProvider::~DataProvider() {
}


void DataProvider::stockTickHandler(CybosTickData * data) {
    std::cout << "Tick Arrived" << std::endl;
}


void DataProvider::bidAskTickHandler(CybosBidAskTickData *data) {
    std::cout << "BidAsk Arrived" << std::endl;
}


void DataProvider::subjectTickHandler(CybosSubjectTickData *data) {
    std::cout << "Subject Arrived" << std::endl;
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
    sa.set_allocated_from_datetime(new Timestamp(TimeUtil::TimeTToTimestamp(from_time)));
    TimeThread * tthread = new TimeThread(stub_);
    connect(tthread, SIGNAL(timeInfoArrived(Timestamp *)), &(TimeInfo::getInstance()), SLOT(timeInfoArrived(Timestamp *)));
    tthread->start();
    stub_->StartSimulation(&context, sa, &empty);
}


void DataProvider::requestStockDayData(const std::string &code, time_t from_date, time_t until_date) {
    ClientContext context;
    CybosDayDatas data;
    StockQuery stock_query;
    stock_query.set_code(code);
    Timestamp *from_timestamp = new Timestamp(TimeUtil::TimeTToTimestamp(from_date));
    Timestamp *until_timestamp = new Timestamp(TimeUtil::TimeTToTimestamp(until_date));
    stock_query.set_allocated_from_datetime(from_timestamp);
    stock_query.set_allocated_until_datetime(until_timestamp);
    stub_->GetDayData(&context, stock_query, &data);
    for (int i = 0; i < data.day_data_size(); ++i) {
        CybosDayData d = data.day_data(i);
        std::cout << "price: " << d.start_price() << "\ttime: " << d.date() << std::endl;
    }
}
