#include "time_info.h"

#include <google/protobuf/util/time_util.h>
#include <QDebug>

using google::protobuf::util::TimeUtil;

TimeInfo::TimeInfo() 
: QObject(0), isSimulation(false) {
    timer = new QTimer(this);
    connect(timer, SIGNAL(timeout()), SLOT(sendTimeInfo()));
    timer->setInterval(1000);
    timer->start(); 
}

void TimeInfo::timeInfoArrived(Timestamp *ts) {
    long msec = TimeUtil::TimestampToMilliseconds(*ts);    
    QDateTime receiveTime = QDateTime::fromMSecsSinceEpoch(msec, Qt::UTC);
    if (currentDateTime.isValid() and currentDateTime.time().minute() != receiveTime.time().minute())
        qWarning() << "current time " << currentDateTime;
    currentDateTime = receiveTime;
}

void TimeInfo::sendTimeInfo() {
    if (currentDateTime.isValid()) {
        emit timeChanged(currentDateTime);
    }
    else {
        emit timeChanged(QDateTime::currentDateTime());
    }
}


QDateTime TimeInfo::getCurrentDateTime() {
    if (currentDateTime.isValid())
        return currentDateTime;
    
    return QDateTime::currentDateTime();
}
