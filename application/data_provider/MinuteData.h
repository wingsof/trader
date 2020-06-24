#ifndef MINUTE_DATA_H_
#define MINUTE_DATA_H_

#include <QObject>
#include <QMap>
#include <QDateTime>
#include "stock_provider.grpc.pb.h"

using stock_api::CybosBidAskTickData;
using stock_api::CybosTickData;
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;


class MinuteTick {
public:
    MinuteTick(int intervaMin);    
    
    bool appendTick(CybosTickData *d);
    const CybosDayData &getCurrent() { return currentData; }
    const CybosDayDatas &getQueue() { return queue; }
    bool isTimeout(long current);
    int getYesterdayClose() { return yesterdayClose; }

    int getHighestPrice() { return highestPrice; }
    int getLowestPrice() { return lowestPrice; }
    uint getHighestVolume() { return highestVolume; }
    uint getLowestVolume() { return lowestVolume; }

private:
    CybosDayData currentData;
    CybosDayDatas queue;
    long currentMSecs;
    int yesterdayClose;
    int intervalMinute;
    int highestPrice;
    int lowestPrice;
    uint highestVolume;
    uint lowestVolume;

    void setCurrentData(CybosTickData *d, long msec);
    void updateCurrentData(CybosTickData *d);
    void pushToQueue();
    void setBoundary(int price, uint volume);

public:
    QString getDebugString();
};


class MinuteData : public QObject {
Q_OBJECT
public:
    MinuteData(QObject *parent, int min);
    MinuteTick * getMinuteTick(const QString &code);

private:
    QMap<QString, MinuteTick *> codeMap;
    long lastCheckTime;
    int intervalMinute;

public slots:
    void stockTickArrived(CybosTickData *);

signals:
    void minuteTickUpdated(QString);
};


#endif
