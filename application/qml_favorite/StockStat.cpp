#include "StockStat.h"
#include <QDebug>


StockStat::StockStat()
: QObject(nullptr) {
    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged, this, &StockStat::slotStockCodeChanged);
    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged, this, &StockStat::stockCodeChanged);
    connect(DataProvider::getInstance(), &DataProvider::stockListTypeChanged, this, &StockStat::stockListTypeChanged);
    connect(DataProvider::getInstance(), &DataProvider::tickArrived, this, &StockStat::tickArrived);

    DataProvider::getInstance()->startStockCodeListening();
    DataProvider::getInstance()->startListTypeListening();
    DataProvider::getInstance()->startStockTick();
}


QStringList StockStat::getRecentSearch() {
    return DataProvider::getInstance()->getRecentSearch();
}


void StockStat::slotStockCodeChanged(QString code, QDateTime untilTime, int _countOfDays) {
    Q_UNUSED(code);
    if (!today.isValid() || (today.toMSecsSinceEpoch() != untilTime.toMSecsSinceEpoch())) {
        today = untilTime;
        countOfDays = _countOfDays;
        clearStat();
    }
}


void StockStat::setCurrentCode(const QString &code) {
    if (today.isValid())
        DataProvider::getInstance()->setCurrentStock(code, today, countOfDays);
}


StockInfo * StockStat::getInfo(const QString &code) {
    if (infoMap.contains(code))
        return infoMap[code];
    else if (today.isValid() && !infoMap.contains(code)) {
        infoMap[code] = new StockInfo(code, today);
        connect(infoMap[code], &StockInfo::infoUpdated, this, &StockStat::infoUpdated);
        return infoMap[code];
    }
    return nullptr;
}


void StockStat::clearStat() {
    QMapIterator<QString, StockInfo *> i(infoMap);
    while (i.hasNext()) {
        i.next();
        delete i.value();
    }
    infoMap.clear();
}


void StockStat::tickArrived(CybosTickData *data) {
    QString code = QString::fromStdString(data->code());
    if (infoMap.contains(code)) {
        StockInfo *info = getInfo(code);
        info->setTodayData(data->start_price(), data->current_price(),
                            data->cum_amount());
        emit infoUpdated(code);
    }
}


StockInfo::StockInfo(const QString &code, const QDateTime &dt)
: QObject(nullptr) {
    m_code = code;
    m_todayOpen = m_currentPrice = 0;
    m_todayAmount = 0;
    m_name = DataProvider::getInstance()->getCompanyName(code);
    connect(DataProvider::getInstance(), &DataProvider::dayDataReady, this, &StockInfo::dayDataReceived);
    DataProvider::getInstance()->requestDayData(m_code, 5, dt.addDays(-1));
}


StockInfo::~StockInfo() {}


void StockInfo::dayDataReceived(QString code, CybosDayDatas *data) {
    if (m_code != code) 
        return;
    int count = data->day_data_size();
    if (count > 1) {
        const CybosDayData &d = data->day_data(count - 1);
        const CybosDayData &d2 = data->day_data(count - 2);
        yesterdayData = d;
        beforeYesterdayData = d2;
        qWarning() << code << "\tdate: " << d.date() << "\tamount: " << d.amount();
        emit infoUpdated(m_code);
    }
    else {
        qWarning() << code << " data size is under 2, actual: " << count;
    }
}


void StockInfo::setTodayData(int openPrice, int currentPrice, uint64_t amount) {
    m_todayOpen = openPrice;
    m_currentPrice = currentPrice;
    m_todayAmount = amount * 10000;
}


int StockInfo::beforeYesterdayClosePrice() {
    return beforeYesterdayData.close_price();
}


bool StockInfo::isYesterdayDataReceived() {
    return yesterdayData.close_price() == 0;
}


bool StockInfo::isTodayDataReceived() {
    return m_todayOpen == 0;
}
