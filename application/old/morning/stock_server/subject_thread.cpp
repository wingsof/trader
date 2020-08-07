#include "subject_thread.h"

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
using google::protobuf::util::TimeUtil;
using google::protobuf::Timestamp;
using google::protobuf::Empty;

using stock_api::Stock;
using stock_api::StockCodeQuery;
using stock_api::StockQuery;
using stock_api::CybosDayDatas;
using stock_api::CybosSubjectTickData;


SubjectThread::SubjectThread(std::shared_ptr<stock_api::Stock::Stub> stub)
: QThread(0){
    stub_ = stub;
}


void SubjectThread::run() {
    ClientContext context;
    Empty empty;
    CybosSubjectTickData data;
    std::unique_ptr<ClientReader<CybosSubjectTickData> > reader(
        stub_->ListenCybosSubject(&context, empty)); 
    while (reader->Read(&data)) {
        emit tickArrived(new CybosSubjectTickData(data));
        std::cout << "Subject Data" << "name: " << data.name() << std::endl;
    }
    Status status = reader->Finish();
    if (status.ok()) {
        std::cout << "Tick succeeded" << std::endl;
    } else {
        std::cout << "Tick Failed" << std::endl;
    }
}
