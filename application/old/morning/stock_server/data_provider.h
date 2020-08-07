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

class StockObject;
class MorningTimer;
class ChooserPlugin;
class DayDataProvider;
class MinuteDataProvider;

class DataProvider : public QObject {
Q_OBJECT
public:
    DataProvider();
    ~DataProvider();

    CybosDayDatas * requestStockDayData(const std::string &code, time_t from_date, time_t until_date);
    void requestStockTick(const std::string &code);
    void requestBidAskTick(const std::string &code);
    void requestSubjectTick(const std::string &code);
    QStringList requestYesterdayTopAmount(const QDateTime &dt);

    void requestDayData(const QString &code);
    void requestMinuteData(const QString &code);

    void startSimulation(const QDateTime & from_time);
    void startListenTicks();

    static DataProvider & getInstance() {
        static DataProvider provider;
        return provider;
    }

    ChooserPlugin *getChooser() { return chooserPlugin; }

    StockObject *getStockObject(const QString &code);

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QMap<QString, StockObject *> object_map;

private:
    void createStockObject(const QString &code);
    ChooserPlugin *         chooserPlugin;
    MorningTimer *          tickHandleTimer;
    DayDataProvider *       dayDataProvider     = NULL;
    MinuteDataProvider *    minuteDataProvider  = NULL;

private slots:
    void stockTickHandler(CybosTickData *);
    void bidAskTickHandler(CybosBidAskTickData *);
    void subjectTickHandler(CybosSubjectTickData *);

    void processTick();
};


#endif
