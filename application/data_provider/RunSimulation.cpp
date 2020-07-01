#include "RunSimulation.h"

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
using google::protobuf::util::TimeUtil;

using stock_api::SimulationArgument;


RunSimulation::RunSimulation(const QDateTime &dt, std::shared_ptr<stock_api::Stock::Stub> stub)
: QThread(0){
    stub_ = stub;
    simulationStartTime = dt;
}


void RunSimulation::run() {
    ClientContext context;
    Empty empty;
    SimulationArgument argument;
    argument.set_allocated_from_datetime(new Timestamp(TimeUtil::TimeTToTimestamp(simulationStartTime.toTime_t())));

    std::unique_ptr<ClientReader<Empty> > reader(
        stub_->StartSimulation(&context, argument)); 
    while (reader->Read(&empty)) {
        ;
    }
    Status status = reader->Finish();
    if (!status.ok()) {
        std::cout << "RunSimulation Failed " << status.error_message() << std::endl;
    }
}
