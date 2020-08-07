#include "data_provider.h"

#include <iostream>
#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
#include <grpcpp/security/credentials.h>
#include "minutedata_provider.h"


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
    minuteDataProvider = new MinuteDataProvider(stub_, QDateTime::currentDateTime(), 2);
    connect(minuteDataProvider, SIGNAL(dataReady(QString, CybosDayDatas *)), this, SLOT(receiveMinuteData(QString, CybosDayDatas *)));
}


DataProvider::~DataProvider() {
}


CybosDayDatas * DataProvider::getMinuteData() {
    return minuteDatas;
}


void DataProvider::receiveMinuteData(QString code, CybosDayDatas *data) {
    minuteDatas = data;
}


void DataProvider::requestMinuteData(const QString &code) {
    if (minuteDataProvider != NULL)
        minuteDataProvider->requestMinuteData(code);
}
