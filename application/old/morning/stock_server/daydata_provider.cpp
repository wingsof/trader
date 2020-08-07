#include "daydata_provider.h"
#include <QThread>
#include <google/protobuf/util/time_util.h>
#include <QDebug>


using grpc::ClientContext;
using stock_api::StockQuery;


DayDataCollector::DayDataCollector(std::shared_ptr<stock_api::Stock::Stub> stub,
                        const QString &_code,
                        const QDateTime &_fromTime,
                        const QDateTime &_untilTime)
: QObject(0), stub_(stub), code(_code){
    qWarning() << "DayDataCollector " << code;
    fromTime = new Timestamp(TimeUtil::TimeTToTimestamp(_fromTime.toTime_t()));
    untilTime = new Timestamp(TimeUtil::TimeTToTimestamp(_untilTime.toTime_t()));
}

void DayDataCollector::process() {
    ClientContext context;
    CybosDayDatas * data = new CybosDayDatas;
    StockQuery stock_query;
    stock_query.set_code(code.toStdString());
    stock_query.set_allocated_from_datetime(fromTime);
    stock_query.set_allocated_until_datetime(untilTime);
    stub_->GetDayData(&context, stock_query, data);
    emit finished(code, data);
}


DayDataProvider::DayDataProvider(std::shared_ptr<stock_api::Stock::Stub> stub,
                                const QDateTime &_fromTime,
                                const QDateTime &_untilTime)
: QObject(0) {
    fromTime = _fromTime;
    untilTime = _untilTime;
    stub_ = stub;
}


void DayDataProvider::requestDayData(const QString &code) {
    qWarning() << "requestDayData " << code;
    if (dayDatas.contains(code)) {
        emit dataReady(code, dayDatas[code]);
        return;
    }
    
    waitingCodes.append(code);
    checkWaitingList();
}


void DayDataProvider::dataReceived(QString code, CybosDayDatas *data) {
    dayDatas[code] = data;
    isProcessing = false;
    emit dataReady(code, dayDatas[code]);
    checkWaitingList();
}


void DayDataProvider::checkWaitingList() {
    if (isProcessing)
        return;
    qWarning() << "checkWatiingList " << waitingCodes.count();
    if (waitingCodes.count() > 0) {
        isProcessing = true;
        QString code = waitingCodes.first();
        waitingCodes.removeFirst();
        QThread * thread = new QThread;
        DayDataCollector * worker = new DayDataCollector(stub_ ,code, fromTime, untilTime);
        worker->moveToThread(thread);
        connect(thread, SIGNAL(started()), worker, SLOT(process()));
        connect(worker, SIGNAL(finished(QString, CybosDayDatas*)), this, SLOT(dataReceived(QString, CybosDayDatas*)));
        connect(worker, SIGNAL(finished(QString, CybosDayDatas*)), thread, SLOT(quit()));
        connect(worker, SIGNAL(finished(QString, CybosDayDatas*)), worker, SLOT(deleteLater()));
        connect(thread, SIGNAL(finished()), thread, SLOT(deleteLater()));
        thread->start();
    }
}
