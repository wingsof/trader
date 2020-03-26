#include "data_provider.h"

#include <iostream>
#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
#include <grpcpp/security/credentials.h>



using grpc::Channel;
using grpc::ClientContext;
using grpc::ClientReader;
using grpc::ClientReaderWriter;
using grpc::ClientWriter;
using grpc::Status;

using stock_api::Stock;


DataProvider::DataProvider()
: QObject(0), stub_(Stock::NewStub(grpc::CreateChannel("localhost:50052", grpc::InsecureChannelCredentials()))){

}


DataProvider::~DataProvider() {
}

void DataProvider::stock_tick_handler() {
    // distribute tick data to subscribers
}
