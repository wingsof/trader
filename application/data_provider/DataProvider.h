#ifndef DATA_PROVIDER_H_
#define DATA_PROVIDER_H_

#include <QObject>
#include <QDateTime>
#include "stock_provider.grpc.pb.h"
#include <google/protobuf/timestamp.pb.h>

class BidAskThread;
class StockSelectionThread;
class TickThread;
class SpeedStatistics;
class MinuteData;
class TimeThread;
class MinuteTick;
class DayDataProvider;
class SimulationEvent;

using stock_api::CybosBidAskTickData;
using stock_api::CybosTickData;
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;
using stock_api::SimulationStatus;
using google::protobuf::Timestamp;


class DataProvider : public QObject {
Q_OBJECT
public:
    enum SIMULATION {
        STOP = 0,
        RUNNING = 1,
        STOP_TO_RUNNING = 2,
        RUNNING_TO_STOP = 3,
    };

    static DataProvider *getInstance() {
        static DataProvider *provider = NULL;
        if (provider == NULL)
            provider = new DataProvider;
        return provider;
    }

    void startStockTick();
    void startBidAskTick();
    void startStockCodeListening();
    void startTimeListening();

    MinuteTick *getMinuteTick(const QString &code);

    bool isSimulation();
    void createSpeedStatistics(int secs=60);
    void collectMinuteData(int min=1);
    void requestDayData(const QString &code, int countOfDays, const QDateTime &_untilTime);
    void requestMinuteData(const QString &code, const QDateTime &fromTime, const QDateTime &untilTime);
    void setCurrentStock(const QString &code, const QDateTime &dt, int countOfDays);
    void startSimulation(const QDateTime &dt);
    void stopSimulation();

private:
    DataProvider();

    std::shared_ptr<stock_api::Stock::Stub> stub_;

    TickThread *            tickThread;
    BidAskThread *          bidAskThread;
    StockSelectionThread *  stockSelectionThread;
    SpeedStatistics *       speedStatistics;
    MinuteData *            minuteData;
    TimeThread *            timeThread;
    DayDataProvider *       dayDataProvider;
    SimulationEvent *       simulationEvent;
    QString currentStockCode;

    SIMULATION m_simulationStatus;

    void _stopSimulation();
    bool _isSimulation();


private slots:
    void convertTimeInfo(Timestamp *);
    void setSimulationStatus(SimulationStatus *status);
    void stockCodeReceived(QString code, QDateTime untilTime, int countOfDays);

signals:
    void stockCodeChanged(QString code, QDateTime untilTime, int countOfDays);
    void tickArrived(CybosTickData *);
    void bidAskTickArrived(CybosBidAskTickData *);
    void minuteTickUpdated(QString);
    void dayDataReady(QString, CybosDayDatas *);
    void minuteDataReady(QString, CybosDayDatas *);
    void timeInfoArrived(QDateTime dt);
    void simulationStatusChanged(bool);
};


#endif
