#include "SimulationEvent.h"

#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
#include <grpcpp/security/credentials.h>
#include <google/protobuf/util/time_util.h>
#include <google/protobuf/timestamp.pb.h>


using grpc::Channel;
using grpc::ClientContext;
using grpc::ClientReader;
using grpc::ClientReaderWriter;
using grpc::ClientWriter;
using grpc::Status;
using google::protobuf::Timestamp;
using google::protobuf::Empty;



SimulationEvent::SimulationEvent(std::shared_ptr<stock_api::Stock::Stub> stub)
: QThread(0){
    stub_ = stub;
}


void SimulationEvent::run() {
    ClientContext context;
    Empty empty;
    SimulationStatus data;
    std::unique_ptr<ClientReader<SimulationStatus> > reader(
        stub_->ListenSimulationStatusChanged(&context, empty)); 
    while (reader->Read(&data)) {
        emit simulationStatusChanged(new SimulationStatus(data));
    }
    Status status = reader->Finish();
    if (!status.ok()) {
        std::cout << "SimulationEvent Failed " << status.error_message() << std::endl;
    }
}
