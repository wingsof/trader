#include "minutedata_provider.h"
#include <QThread>
#include <google/protobuf/util/time_util.h>
#include <QDebug>


using grpc::ClientContext;
using stock_api::StockQuery;
using stock_api::PastMinuteQuery;


MinuteDataCollector::MinuteDataCollector(std::shared_ptr<stock_api::Stock::Stub> stub,
                        const QString &_code,
                        const QDateTime & _today,
                        int count)
: QObject(0), stub_(stub), code(_code), dataCount(count){
    qWarning() << "MinuteDataCollector " << code;
    todayTime = new Timestamp(TimeUtil::TimeTToTimestamp(_today.toTime_t()));
}

void MinuteDataCollector::process() {
    ClientContext context;
    CybosDayDatas * data = new CybosDayDatas;
    PastMinuteQuery query;
    query.set_code(code.toStdString());
    query.set_count_of_days(dataCount);
    query.set_allocated_today(todayTime);
    stub_->GetPastMinuteData(&context, query, data);
    emit finished(code, data);
}


MinuteDataProvider::MinuteDataProvider(std::shared_ptr<stock_api::Stock::Stub> stub,
                                const QDateTime & _today, int count)
: QObject(0), dataCount(count) {
    today = _today;
    stub_ = stub;
}


void MinuteDataProvider::requestMinuteData(const QString &code) {
    qWarning() << "requestMinuteData " << code;
    if (minuteDatas.contains(code)) {
        emit dataReady(code, minuteDatas[code]);
        return;
    }
    
    waitingCodes.append(code);
    checkWaitingList();
}


void MinuteDataProvider::dataReceived(QString code, CybosDayDatas *data) {
    minuteDatas[code] = data;
    isProcessing = false;
    emit dataReady(code, minuteDatas[code]);
    checkWaitingList();
}


void MinuteDataProvider::checkWaitingList() {
    if (isProcessing)
        return;
    qWarning() << "checkWatiingList " << waitingCodes.count();
    if (waitingCodes.count() > 0) {
        isProcessing = true;
        QString code = waitingCodes.first();
        waitingCodes.removeFirst();
        QThread * thread = new QThread;
        MinuteDataCollector * worker = new MinuteDataCollector(stub_ ,code, today, dataCount);
        worker->moveToThread(thread);
        connect(thread, SIGNAL(started()), worker, SLOT(process()));
        connect(worker, SIGNAL(finished(QString, CybosDayDatas*)), this, SLOT(dataReceived(QString, CybosDayDatas*)));
        connect(worker, SIGNAL(finished(QString, CybosDayDatas*)), thread, SLOT(quit()));
        connect(worker, SIGNAL(finished(QString, CybosDayDatas*)), worker, SLOT(deleteLater()));
        connect(thread, SIGNAL(finished()), thread, SLOT(deleteLater()));
        thread->start();
    }
}
