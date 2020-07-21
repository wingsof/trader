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


void TraderThread::order(const QString &code, int price, int quantity, int percentage, OrderMsg::Method m, bool isBuy) {
    ClientContext context;
    TradeMsg msg;
    msg.set_msg_type(TradeMsg::ORDER_MSG);
    OrderMsg *orderMsg = new OrderMsg;
    orderMsg->set_code(code.toStdString());
    orderMsg->set_is_buy(isBuy);
    orderMsg->set_price(price);
    orderMsg->set_quantity(quantity);
    orderMsg->set_percentage(percentage);
    orderMsg->set_method(m);
    msg.set_allocated_order_msg(orderMsg);

    Empty empty;
    stub_->RequestToTrader(&context, msg, &empty);
}


void TraderThread::run() {

}
