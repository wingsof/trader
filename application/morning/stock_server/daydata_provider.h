#ifndef DAY_DATA_PROVIDER_H_
#define DAY_DATA_PROVIDER_H_


#include <QObject>
#include "stock_provider.grpc.pb.h"


class DayDataProcess : public QObject {
Q_OBJECT
public:
    DayDataProcess(std::shared_ptr<stock_api::Stock::Stub> stub);

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
};


class DayDataProvider : public QObject {
Q_OBJECT
public:
    DayDataProvider(std::shared_ptr<stock_api::Stock::Stub> stub);

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
};


#endif
