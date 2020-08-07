#ifndef DAY_DATA_PROVIDER_H_
#define DAY_DATA_PROVIDER_H_


#include <QObject>
#include <QMap>
#include <QDateTime>
#include "stock_provider.grpc.pb.h"
#include <google/protobuf/util/time_util.h>


using google::protobuf::Timestamp;
using google::protobuf::util::TimeUtil;
using grpc::ClientContext;

using stock_api::CybosDayDatas;


class DayDataProvider : public QObject {
Q_OBJECT
public:
    DayDataProvider(std::shared_ptr<stock_api::Stock::Stub> stub,
                                    const QDateTime &fromTime,
                                    const QDateTime &untilTime);

    void requestDayData(const QString &code);

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QMap<QString, CybosDayDatas *> dayDatas;
    QList<QString> waitingCodes;
    bool isProcessing = false;
    QDateTime fromTime;
    QDateTime untilTime;

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
