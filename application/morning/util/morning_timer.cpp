#include "morning_timer.h"
#include "stock_server/time_info.h"
#include <QDateTime>
#include <QDebug>


MorningTimer::MorningTimer(int _interval, QObject *p)
: QObject(p), interval(_interval) {
    timer = new QTimer(this);
    timer->setInterval(int(interval / 100));
    connect(timer, SIGNAL(timeout()), SLOT(processTimeout()));
}


MorningTimer::~MorningTimer() {}


void MorningTimer::processTimeout() {
    QDateTime now = TimeInfo::getInstance().getCurrentDateTime();
    if (!lastProcessedTime.isValid())
        lastProcessedTime = TimeInfo::getInstance().getCurrentDateTime();
    //qWarning() << "timer timeout: " << lastProcessedTime.msecsTo(now);
    if (lastProcessedTime.msecsTo(now) >= interval) {
        //qWarning() << "timer process";
        lastProcessedTime = now;
        emit timeout();
    }
}


void MorningTimer::start() {
    timer->start();
}
