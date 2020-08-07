#ifndef STOCK_OBJECT_H_
#define STOCK_OBJECT_H_


#include <QObject>
#include <QList>
#include <memory>
#include <QDateTime>
#include "stock_provider.pb.h"


class DayDataProvider;
class MinuteDataProvider;
using stock_api::CybosDayDatas;


class StockObject : public QObject {
Q_OBJECT
public:
    class PeriodTickData {
    public:
        long amount = 0;
        long open = 0;
        long close = 0;
        long low = 0;
        long high = 0;
        QDateTime date;
        long buy_volume = 0;
        long sell_volume = 0;
    };

public:
    enum MarketType { PRE_MARKET=49, IN_MARKET=50 };

    StockObject(const QString &_code, DayDataProvider *d, MinuteDataProvider *m, QObject *p=0);
    ~StockObject();

    void handleTickData(stock_api::CybosTickData *data);
    void handleBidAskData(stock_api::CybosBidAskTickData *data);
    void handleSubjectData(stock_api::CybosSubjectTickData *data);

    void processTickData();
    QList<StockObject::PeriodTickData *>  getPeriodData(const QDateTime &dt, int msecs);

public:
    const QString &getCode() { return code; }
    const QString &getCompanyName() { return companyName; }
    const unsigned int getYesterdayClose() { return yesterdayClose; }
    const unsigned int getTodayOpen() { return openPrice; }
    const unsigned int getTodayHigh() { return todayHigh; }
    const unsigned int getTodayLow() { return todayLow; }
    const unsigned int getCurrentPrice() { return currentPrice; }

    CybosDayDatas * getDayDatas();
    const QList<StockObject::PeriodTickData *> & getMinuteData();
    CybosDayDatas * getPastMinuteDatas();

    void connectToDayWindow(QObject *obj);
    void connectToMinuteWindow(QObject *obj);

private:
    QString code;
    unsigned int currentPrice = 0;

    unsigned int openPrice = 0;
    unsigned int yesterdayClose = 0;
    unsigned int todayHigh = 0;
    unsigned int todayLow = 0;

    int lastMinuteIndex = 0;
    QString companyName;
    bool isKospi;

    bool dayWindowConnected = false;
    bool minuteWindowConnected = false;

    DayDataProvider * dayDataProvider;
    MinuteDataProvider * minuteDataProvider;

    CybosDayDatas * dayDatas;
    CybosDayDatas * pastMinuteDatas;

    QList<stock_api::CybosTickData *> tickData;
    QList<StockObject::PeriodTickData *> periodTickData;
    QList<StockObject::PeriodTickData *> minuteData;
    QList<float> averagePrices;

    void createMinuteData();
    void clearTickData();

    void setCurrentPrice(unsigned int price);

private slots:
    void receiveDayData(QString, CybosDayDatas *);
    void receiveMinuteData(QString, CybosDayDatas *);

signals:
    void readyDayData(QString);
    void readyPastMinuteData(QString);
    void minuteDataUpdated(QString, StockObject::PeriodTickData *);

    void currentPriceChanged(QString, unsigned int);
};


#endif
