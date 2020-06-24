#ifndef DAY_DATA_PROVIDER_H_
#define DAY_DATA_PROVIDER_H_


#include <QObject>
#include <QMap>
#include <QDateTime>
#include <qqml.h>
#include "stock_provider.grpc.pb.h"
#include <google/protobuf/util/time_util.h>


using google::protobuf::Timestamp;
using google::protobuf::util::TimeUtil;
using stock_api::CybosDayData;
using grpc::ClientContext;
using stock_api::CybosDayDatas;


class DayDataQuery {
public:
    explicit DayDataQuery(const QString &code, const QDateTime &fromTime, const QDateTime &untilTime, bool isMinute=false) {
        mCode = code;
        mFromTime = fromTime;
        mUntilTime = untilTime;
        requestMinuteData = isMinute;
    }

public:
    const QString &getCode() { return mCode; }
    const QDateTime &getFromTime() { return mFromTime; }
    const QDateTime &getUntilTime() { return mUntilTime; }
    bool isRequestMinuteData() { return requestMinuteData; }

private:
    QString mCode;
    QDateTime mFromTime;
    QDateTime mUntilTime;
    bool requestMinuteData;
};


class DayDataProvider : public QObject {
    Q_OBJECT
public:
    DayDataProvider(std::shared_ptr<stock_api::Stock::Stub> stub);

    Q_INVOKABLE void requestDayData(const QString &code,
                                    int countOfDays,
                                    const QDateTime &untilTime);

    Q_INVOKABLE void requestMinuteData(const QString &code,
                                    const QDateTime &fromTime,
                                    const QDateTime &untilTime);


private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QList<DayDataQuery> waitingQueue;
    bool isProcessing = false;

private:
    void checkWaitingList();

private slots:
    void dataReceived(QString, CybosDayDatas*);
    void minuteDataReceived(QString, CybosDayDatas*);

signals:
    void dataReady(QString, CybosDayDatas*);
    void minuteDataReady(QString, CybosDayDatas*);
};

class DayDataCollector : public QObject {
Q_OBJECT
public:
    DayDataCollector(std::shared_ptr<stock_api::Stock::Stub> stub,
                        const QString &_code,
                        const QDateTime &_fromTime,
                        const QDateTime &_untilTime,
                        bool isRequestMinute);

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QString code;
    Timestamp * fromTime;
    Timestamp * untilTime;
    bool requestMinuteData;

public slots:
    void process();

signals:
    void finished(QString, CybosDayDatas *);
    void minuteDataReady(QString, CybosDayDatas *);
};


#endif
