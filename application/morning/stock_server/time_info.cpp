#include "time_info.h"

#include <google/protobuf/util/time_util.h>
#include <QDebug>

using google::protobuf::util::TimeUtil;

TimeInfo::TimeInfo() 
: QObject(0){
    timer = new QTimer(this);
    connect(timer, SIGNAL(timeout()), SLOT(sendTimeInfo()));
    timer->setInterval(1000);
    timer->start(); 
}

void TimeInfo::timeInfoArrived(Timestamp *ts) {
    long msec = TimeUtil::TimestampToMilliseconds(*ts);    
    currentDateTime = QDateTime::fromMSecsSinceEpoch(msec, Qt::UTC);
}

void TimeInfo::sendTimeInfo() {
    if (currentDateTime.isValid()) {
        emit timeChanged(currentDateTime);
    }
    else {
        emit timeChanged(QDateTime::currentDateTime());
    }
}
