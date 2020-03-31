#ifndef _DATA_PROVIDER_H_
#define _DATA_PROVIDER_H_

#include <iostream>
#include <memory>
#include <QObject>
#include <time.h>
#include <unordered_map>
#include <any>
#include "stock_provider.grpc.pb.h"
#include <google/protobuf/util/time_util.h>
#include <google/protobuf/timestamp.pb.h>
#include "stock_provider.grpc.pb.h"


using stock_api::CybosTickData;
using stock_api::CybosBidAskTickData;


class DataProvider : public QObject {
Q_OBJECT
public:
    DataProvider();
    ~DataProvider();

    void requestStockDayData(const std::string &code, time_t from_date, time_t until_date);
    void requestStockTick(const std::string &code);
    void requestBidAskTick(const std::string &code);
    static DataProvider & getInstance() {
        static DataProvider provider;
        return provider;
    }

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;

private slots:
    void stockTickHandler(CybosTickData *);
    void bidAskTickHandler(CybosBidAskTickData *);
};


#endif
