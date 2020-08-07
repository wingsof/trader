#ifndef _DATA_PROVIDER_H_
#define _DATA_PROVIDER_H_

#include <iostream>
#include <memory>
#include <QObject>
#include <QStringList>
#include <QDateTime>
#include <QMap>
#include <QTimer>
#include <time.h>
#include "stock_provider.grpc.pb.h"
#include <google/protobuf/util/time_util.h>
#include <google/protobuf/timestamp.pb.h>


using stock_api::CybosTickData;
using stock_api::CybosBidAskTickData;
using stock_api::CybosSubjectTickData;
using stock_api::CybosDayDatas;

class MinuteDataProvider;

class DataProvider : public QObject {
Q_OBJECT
public:
    DataProvider();
    ~DataProvider();

    void requestMinuteData(const QString &code);

    CybosDayDatas * getMinuteData();

    static DataProvider & getInstance() {
        static DataProvider provider;
        return provider;
    }

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;

private:
    MinuteDataProvider *    minuteDataProvider  = NULL;
    CybosDayDatas * minuteDatas = NULL;

private slots:
    void receiveMinuteData(QString, CybosDayDatas *);
};


#endif
