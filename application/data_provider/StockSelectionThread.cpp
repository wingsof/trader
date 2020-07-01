#include "StockSelectionThread.h"
#include <google/protobuf/util/time_util.h>
#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>

using grpc::Channel;
using grpc::ClientContext;
using grpc::ClientReader;
using grpc::ClientReaderWriter;
using grpc::ClientWriter;
using grpc::Status;

using google::protobuf::Empty;
using google::protobuf::Timestamp;

using stock_api::StockSelection;
using google::protobuf::util::TimeUtil;


StockSelectionThread::StockSelectionThread(std::shared_ptr<stock_api::Stock::Stub> stub)
: QThread(0) {
    stub_ = stub;
}


void StockSelectionThread::setCurrentStock(const QString &code, const QDateTime &dt, int countOfDays) {
    ClientContext context;
    StockSelection data;
    Empty empty;
    data.set_code(code.toStdString());
    Timestamp *untilTime = new Timestamp(TimeUtil::TimeTToTimestamp(dt.toTime_t()));
    data.set_allocated_until_datetime(untilTime);
    data.set_count_of_days(countOfDays);
    stub_->SetCurrentStock(&context, data, &empty);
}


void StockSelectionThread::run() {
    ClientContext context;
    Empty empty;
    StockSelection data;
    std::unique_ptr<ClientReader<StockSelection> > reader(
        stub_->ListenCurrentStock(&context, empty)); 
    while (reader->Read(&data)) {
        long msec = TimeUtil::TimestampToMilliseconds(data.until_datetime());
        std::cout << "Read StockSelection: " << data.code() << std::endl;
        emit stockCodeChanged(QString::fromStdString(data.code()),
                              QDateTime::fromMSecsSinceEpoch(msec).toLocalTime(),
                              data.count_of_days());
    }
    Status status = reader->Finish();
    if (status.ok()) {
        std::cout << "StockSelectionThread succeeded" << std::endl;
    } else {
        std::cout << "StockSelectionThread Failed " << status.error_message() << std::endl << status.error_details() << std::endl;
    }
}
