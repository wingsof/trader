#include "TraderThread.h"

#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
#include <grpcpp/security/credentials.h>
#include <google/protobuf/util/time_util.h>
#include <google/protobuf/timestamp.pb.h>
#include <QDebug>


using grpc::ClientContext;
using google::protobuf::Empty;

using stock_api::TradeMsg;


TraderThread::TraderThread(std::shared_ptr<stock_api::Stock::Stub> stub)
: QThread(0){
    stub_ = stub;
}


void TraderThread::requestOrder(int price, int quantity, int percentage, int option) {
    qWarning()  << "TraderThread : " << price << "\t" << quantity << "\t" << percentage << "\t" << option;
    ClientContext context;
    TradeMsg msg;
    msg.set_price(price);
    msg.set_quantity(quantity);
    msg.set_percentage(percentage);
    Empty empty;
    stub_->RequestOrder(&context, msg, &empty);
}


void TraderThread::run() {

}
