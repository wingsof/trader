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
    explicit DayDataQuery(const QString &code, const QDateTime &fromTime, const QDateTime &untilTime) {
        mCode = code;
        mFromTime = fromTime;
        mUntilTime = untilTime;
    }

public:
    const QString &getCode() { return mCode; }
    const QDateTime &getFromTime() { return mFromTime; }
    const QDateTime &getUntilTime() { return mUntilTime; }

private:
    QString mCode;
    QDateTime mFromTime;
    QDateTime mUntilTime;
};


class DayDataProvider : public QObject {
    Q_OBJECT
public:
    DayDataProvider();

    Q_INVOKABLE void requestDayData(const QString &code,
                                    int countOfDays,
                                    const QDateTime &_untilTime);
    std::shared_ptr<stock_api::Stock::Stub> getStub() { return stub_; }

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QList<DayDataQuery> waitingQueue;
    bool isProcessing = false;

private:
    void checkWaitingList();

private slots:
    void dataReceived(QString, CybosDayDatas*);

signals:
    void dataReady(QString, CybosDayDatas*);
};

class DayDataCollector : public QObject {
Q_OBJECT
public:
    DayDataCollector(std::shared_ptr<stock_api::Stock::Stub> stub,
                        const QString &_code,
                        const QDateTime &_fromTime,
                        const QDateTime &_untilTime);

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QString code;
    Timestamp * fromTime;
    Timestamp * untilTime;

public slots:
    void process();

signals:
    void finished(QString, CybosDayDatas *);
};


#endif
