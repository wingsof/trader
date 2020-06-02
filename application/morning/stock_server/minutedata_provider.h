#ifndef MINUTE_DATA_PROVIDER_H_
#define MINUTE_DATA_PROVIDER_H_


#include <QObject>
#include <QMap>
#include <QDateTime>
#include "stock_provider.grpc.pb.h"
#include <google/protobuf/util/time_util.h>


using google::protobuf::Timestamp;
using google::protobuf::util::TimeUtil;
using grpc::ClientContext;

using stock_api::CybosDayDatas;


class MinuteDataProvider : public QObject {
Q_OBJECT
public:
    MinuteDataProvider(std::shared_ptr<stock_api::Stock::Stub> stub,
                                    const QDateTime & _today, int count=2);

    void requestMinuteData(const QString &code);

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QMap<QString, CybosDayDatas *> minuteDatas;
    int dataCount;
    QList<QString> waitingCodes;
    bool isProcessing = false;
    QDateTime today;

private:
    void checkWaitingList();

private slots:
    void dataReceived(QString, CybosDayDatas*);

signals:
    void dataReady(QString, CybosDayDatas*);
};

class MinuteDataCollector : public QObject {
Q_OBJECT
public:
    MinuteDataCollector(std::shared_ptr<stock_api::Stock::Stub> stub,
                        const QString &_code,
                        const QDateTime &_untilTime,
                        int count);

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QString code;
    Timestamp * todayTime;
    int dataCount;

public slots:
    void process();

signals:
    void finished(QString, CybosDayDatas *);
};


#endif
