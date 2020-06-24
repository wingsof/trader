#ifndef DATA_PROVIDER_H_
#define DATA_PROVIDER_H_

#include <QObject>
#include <QDateTime>
#include "stock_provider.grpc.pb.h"


class BidAskThread;
class StockSelectionThread;
class TickThread;
class SpeedStatistics;
class MinuteData;
class TimeThread;
class MinuteTick;
class DayDataProvider;

using stock_api::CybosBidAskTickData;
using stock_api::CybosTickData;
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;


class DataProvider : public QObject {
Q_OBJECT
public:
    static DataProvider *getInstance() {
        static DataProvider *provider = NULL;
        if (provider == NULL)
            provider = new DataProvider;
        return provider;
    }

    void startStockTick();
    void startBidAskTick();
    void startStockCodeListening();
    void createSpeedStatistics(int secs=60);
    void collectMinuteData(int min=1);
    MinuteTick *getMinuteTick(const QString &code);
    void requestDayData(const QString &code, int countOfDays, const QDateTime &_untilTime);
    void requestMinuteData(const QString &code, const QDateTime &fromTime, const QDateTime &untilTime);

private:
    DataProvider();

    std::shared_ptr<stock_api::Stock::Stub> stub_;

    TickThread *tickThread;
    BidAskThread *bidAskThread;
    StockSelectionThread *stockSelectionThread;
    SpeedStatistics * speedStatistics;
    MinuteData *minuteData;
    TimeThread *timeThread;
    DayDataProvider *dayDataProvider;

signals:
    void stockCodeChanged(QString code, QDateTime untilTime, int countOfDays);
    void tickArrived(CybosTickData *);
    void bidAskTickArrived(CybosBidAskTickData *);
    void minuteTickUpdated(QString);
    void dayDataReady(QString, CybosDayDatas *);
    void minuteDataReady(QString, CybosDayDatas *);
};


#endif
