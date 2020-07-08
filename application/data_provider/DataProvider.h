#ifndef DATA_PROVIDER_H_
#define DATA_PROVIDER_H_

#include <QObject>
#include <QDateTime>
#include <QStringList>
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
class StockListThread;

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
    void startListTypeListening();

    MinuteTick *getMinuteTick(const QString &code);

    QString getCompanyName(const QString &code);

    bool isSimulation();
    void createSpeedStatistics(int secs=60);
    void collectMinuteData(int min=1);
    void requestDayData(const QString &code, int countOfDays, const QDateTime &_untilTime);
    void requestMinuteData(const QString &code, const QDateTime &fromTime, const QDateTime &untilTime);
    void setCurrentStock(const QString &code);
    void setCurrentDateTime(const QDateTime &dt);
    void startSimulation();
    void stopSimulation();

    QStringList getRecentSearch();
    QStringList getFavoriteList();
    void addToFavorite(const QString &code);
    void removeFromFavorite(const QString &code);
    const QDateTime & currentDateTime() { return m_currentDateTime; }

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
    StockListThread *       stockListThread;


    QString currentStockCode;
    QDateTime m_currentDateTime;

    SIMULATION m_simulationStatus;

    void _stopSimulation();
    bool _isSimulation();
    void _setCurrentStock(const QString &code);
    void _setCurrentDateTime(const QDateTime &dt);

private slots:
    void convertTimeInfo(Timestamp *);
    void setSimulationStatus(SimulationStatus *status);
    void stockCodeReceived(QString code);

signals:
    void stockCodeChanged(QString code);
    void tickArrived(CybosTickData *);
    void bidAskTickArrived(CybosBidAskTickData *);
    void minuteTickUpdated(QString);
    void dayDataReady(QString, CybosDayDatas *);
    void minuteDataReady(QString, CybosDayDatas *);
    void timeInfoArrived(QDateTime dt);
    void simulationStatusChanged(bool);
    void stockListTypeChanged(QString);
};


#endif
