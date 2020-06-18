#ifndef DATA_PROVIDER_H_
#define DATA_PROVIDER_H_

#include <QObject>
#include <QDateTime>
#include "stock_provider.grpc.pb.h"


class BidAskThread;
class StockSelectionThread;
class TickThread;
class SpeedStatistics;

using stock_api::CybosBidAskTickData;
using stock_api::CybosTickData;


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

private:
    DataProvider();

    std::shared_ptr<stock_api::Stock::Stub> stub_;

    TickThread *tickThread;
    BidAskThread *bidAskThread;
    StockSelectionThread *stockSelectionThread;
    SpeedStatistics * speedStatistics;

signals:
    void stockCodeChanged(QString code, QDateTime untilTime, int countOfDays);
    void tickArrived(CybosTickData *);
    void bidAskTickArrived(CybosBidAskTickData *);
};


#endif
