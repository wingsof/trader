#include "MinuteData.h"
#include <google/protobuf/util/time_util.h>
#include <QDebug>

using google::protobuf::util::TimeUtil;

// TODO: need heartbeat because it is possible having no data for some period

MinuteTick::MinuteTick(int intervalMin) {
    currentMSecs = 0;
    yesterdayClose = 0;
    highestVolume = lowestVolume = 0;
    highestPrice = lowestPrice = 0;
    intervalMinute = intervalMin;
}


void MinuteTick::setCurrentData(CybosTickData *d, long msec) {
    QDateTime dt = QDateTime::fromMSecsSinceEpoch(msec, Qt::UTC);
    currentData.set_date(dt.toString("yyyyMMdd").toUInt());
    currentData.set_time(dt.toString("hhmm").toUInt());
    currentData.set_start_price(d->current_price());
    currentData.set_highest_price(d->current_price());
    currentData.set_lowest_price(d->current_price());
    currentData.set_close_price(d->current_price());
    currentData.set_volume(d->volume());
    currentData.set_amount(d->volume() * d->current_price());
    currentData.set_cum_sell_volume(d->cum_sell_volume());
    currentData.set_cum_buy_volume(d->cum_buy_volume());
    currentMSecs = msec;
}


bool MinuteTick::isTimeout(long current) {
    if (currentMSecs == 0)
        return false;
    else if (current - currentMSecs > intervalMinute * 60 * 1000)
        return true;

    return false;
}


bool MinuteTick::appendTick(CybosTickData *d) {
    long msec = TimeUtil::TimestampToMilliseconds(d->tick_date());

    if (d->market_type() == 49) {
        if (currentMSecs > 0) {
            pushToQueue();
            currentMSecs = 0;
            return true;
        }
    }
    else if (d->market_type() == 50) {
        yesterdayClose = d->current_price() - d->yesterday_diff();
        setBoundary(d->current_price(), d->volume());
        if (currentMSecs == 0) {
            setCurrentData(d, msec);
        }
        else {
            if (isTimeout(msec)) {
                pushToQueue();    
                setCurrentData(d, msec);
            }
            else {
                updateCurrentData(d);
            }
        }
        return true;
    }
    return false;
}


void MinuteTick::setBoundary(int price, uint volume) {
    if (lowestPrice == 0 || lowestPrice > price)
        lowestPrice = price;

    if (price > highestPrice)
        highestPrice = price;

    if (lowestVolume == 0 || lowestVolume > volume)
        lowestVolume = volume;

    if (volume > highestVolume)
        highestVolume = volume;
}


QString MinuteTick::getDebugString() {
    QString debug = QString("current minute size : ");
    debug += QString::number(queue.day_data_size());
    debug += "\ncurrentData: \n";
    debug += QString::fromStdString(currentData.DebugString());
    debug += "\n";
    return debug;
}


void MinuteTick::pushToQueue() {
    CybosDayData *d = queue.add_day_data();
    *d = currentData;
    currentData.Clear();
}


void MinuteTick::updateCurrentData(CybosTickData *d) {
    if (d->current_price() > currentData.highest_price())
        currentData.set_highest_price(d->current_price());
    
    if (d->current_price() < currentData.lowest_price())
        currentData.set_lowest_price(d->current_price());

    currentData.set_close_price(d->current_price());
    currentData.set_volume(currentData.volume() + d->volume());
    currentData.set_amount(d->volume() * d->current_price() + currentData.amount());
    currentData.set_cum_sell_volume(d->cum_sell_volume());
    currentData.set_cum_buy_volume(d->cum_buy_volume());
}


MinuteData::MinuteData(QObject *parent, int min)
: QObject(parent) {
    lastCheckTime = 0;
    intervalMinute = min;
}


MinuteTick * MinuteData::getMinuteTick(const QString &code) {
    if (codeMap.contains(code))
        return codeMap[code];

    return nullptr;
}


void MinuteData::stockTickArrived(CybosTickData *data) {
    QString code = QString::fromStdString(data->code());
    if (!codeMap.contains(code)) {
        codeMap[code] = new MinuteTick(intervalMinute);
    }

    if (codeMap[code]->appendTick(data)) 
        emit minuteTickUpdated(code);
}
