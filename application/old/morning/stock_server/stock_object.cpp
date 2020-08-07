#include "stock_object.h"
#include "stock_server/time_info.h"
#include <QDebug>
#include "daydata_provider.h"
#include "minutedata_provider.h"

using stock_api::CybosTickData;

using stock_api::CybosBidAskTickData;
using stock_api::CybosSubjectTickData;


StockObject::StockObject(const QString &_code, DayDataProvider * d, MinuteDataProvider * m, QObject *p)
: QObject(p), code(_code), dayDataProvider(d),
  minuteDataProvider(m) {
    lastMinuteIndex = 0;
    isKospi = false;
    dayDatas = NULL;
    connect((QObject *)dayDataProvider, SIGNAL(dataReady(QString, CybosDayDatas *)),
            this, SLOT(receiveDayData(QString, CybosDayDatas *)));
    dayDataProvider->requestDayData(code);

    connect((QObject *)minuteDataProvider, SIGNAL(dataReady(QString, CybosDayDatas *)),
            this, SLOT(receiveMinuteData(QString, CybosDayDatas *)));
    minuteDataProvider->requestMinuteData(code);

    qWarning() << "StockObject created: " << code;
}


StockObject::~StockObject() {}


void StockObject::receiveDayData(QString _code, CybosDayDatas * data) {
    if (_code == code) {
        dayDatas = data;
        emit readyDayData(code);
        //qWarning() << "receiveDayData " << code << ", count : " << data->day_data_size();
    }
}


void StockObject::receiveMinuteData(QString _code, CybosDayDatas * data) {
    if (_code == code) {
        pastMinuteDatas = data;
        emit readyPastMinuteData(code);
    }
}


void StockObject::connectToDayWindow(QObject * obj) {
    if (!dayWindowConnected) {
        connect(this, SIGNAL(readyDayData(QString)), obj, SLOT(dayDataArrived(QString)));
        dayWindowConnected = true;
    }
}


void StockObject::connectToMinuteWindow(QObject *obj) {
    if (!minuteWindowConnected) {
        connect(this, SIGNAL(readyPastMinuteData(QString)), obj, SLOT(pastMinuteDataArrived(QString)));
        minuteWindowConnected = false;
    }
}


CybosDayDatas * StockObject::getDayDatas() {
    return dayDatas;
}


CybosDayDatas * StockObject::getPastMinuteDatas() {
    return pastMinuteDatas;
}


void StockObject::handleTickData(CybosTickData *data) {
    isKospi = data->is_kospi();
    if (data->market_type() == StockObject::MarketType::IN_MARKET) {
        if (openPrice == 0)
            openPrice = data->start_price();

        if (yesterdayClose == 0)
            yesterdayClose = data->current_price() + data->yesterday_diff();

        if (todayHigh == 0)
            todayHigh = data->highest_price();

        if (todayLow == 0)
            todayLow = data->lowest_price();

        if (companyName.isEmpty()) {
            companyName = QString::fromStdString(data->company_name());
        }

        setCurrentPrice(data->current_price());
        tickData.append(data);
    }
}


void StockObject::setCurrentPrice(unsigned int price) {
    if (currentPrice != price) {
        currentPrice = price;
        emit currentPriceChanged(code, currentPrice);
    }
}


void StockObject::handleBidAskData(CybosBidAskTickData *data) {

}


void StockObject::handleSubjectData(CybosSubjectTickData *data) {

}


QList<StockObject::PeriodTickData *> StockObject::getPeriodData(const QDateTime &dt, int msecs) {
    QList<PeriodTickData *> snapshot;
    QList<PeriodTickData *>::reverse_iterator i;
    for (i = periodTickData.rbegin(); i != periodTickData.rend(); ++i) {
        if ((*i)->date.msecsTo(dt) < msecs)
            snapshot.append(*i);
    }
    // TODO: Create PeriodTickData which not processed as PeriodTickData
    return snapshot;
}


const QList<StockObject::PeriodTickData *> & StockObject::getMinuteData() {
    return minuteData;
}


void StockObject::createMinuteData() {
    PeriodTickData * first = periodTickData.at(lastMinuteIndex);
    PeriodTickData * last = periodTickData.last();
    if (first->date.msecsTo(last->date) >= 1000 * 60) {
        StockObject::PeriodTickData * ptd = new StockObject::PeriodTickData;
        ptd->open = first->open;
        ptd->close = last->close;
        ptd->date = last->date;
        ptd->low = ptd->open;

        for (int i = lastMinuteIndex; i < periodTickData.count(); ++i) {
            const PeriodTickData * data = periodTickData.at(i);
            ptd->amount += data->amount;
            ptd->buy_volume += data->buy_volume;
            ptd->sell_volume += data->sell_volume;

            if (data->low < ptd->low)
                ptd->low = data->low;

            if (data->high > ptd->high)
                ptd->high = data->high;
        } 
        lastMinuteIndex = periodTickData.count();
        minuteData.append(ptd);
        emit minuteDataUpdated(code, ptd);
    }
    // Handle minute realtime data using currentPrice
}


void StockObject::processTickData() {
    if (tickData.isEmpty())
        return;

    long total_prices = 0;
    StockObject::PeriodTickData * ptd = new StockObject::PeriodTickData;
    ptd->open = tickData.first()->current_price();
    ptd->low = ptd->open;
    ptd->close = tickData.last()->current_price();
    QListIterator<CybosTickData *> i(tickData);

    while (i.hasNext()) {
        CybosTickData * ctd = i.next();
        // TODO: skip tick data which outdated
        total_prices += ctd->current_price();
        ptd->amount += ctd->volume() * ctd->current_price();
        if (ctd->current_price() > ptd->high)
            ptd->high = ctd->current_price();

        if (ctd->current_price() < ptd->low)
            ptd->low = ctd->current_price();

        if (ctd->buy_or_sell())
            ptd->buy_volume += ctd->volume();
        else
            ptd->sell_volume += ctd->volume();
    }
    ptd->date = TimeInfo::getInstance().getCurrentDateTime();
    averagePrices.append(total_prices / tickData.count());
    periodTickData.append(ptd);
    createMinuteData();
    clearTickData();
}


void StockObject::clearTickData() {
    QMutableListIterator<CybosTickData *> i(tickData);
    while (i.hasNext()) {
        CybosTickData * data = i.next();
        i.remove();
        delete data;
    }
}
