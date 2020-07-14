#ifndef _TRADER_THREAD_H_
#define _TRADER_THREAD_H_


#include <QThread>
#include <iostream>
#include "stock_provider.grpc.pb.h"


class TraderThread : public QThread {
Q_OBJECT
public:
    TraderThread(std::shared_ptr<stock_api::Stock::Stub> stub);

    void requestOrder(int price, int quantity, int percentage, int option);

protected:
    void run();

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
};


#endif
