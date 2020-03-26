#ifndef _DATA_PROVIDER_H_
#define _DATA_PROVIDER_H_

#include <iostream>
#include <memory>
#include <QObject>
#include "stock_provider.grpc.pb.h"


class DataProvider : public QObject {
Q_OBJECT
public:
    DataProvider();
    ~DataProvider();

    void subscribe_stock(const std::string & code);

    static DataProvider & getInstance() {
        static DataProvider provider;
        return provider;
    }

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;

    void stock_tick_handler();
};


#endif
