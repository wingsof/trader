#include "stockmodel.h"
#include "stock_server/data_provider.h"
#include "stock_server/stock_object.h"
#include "stock_server/time_info.h"
#include "chart_creator.h"
#include <QDebug>


/*
    StockModel provides various stock model to UI for interaction
    when UI send start signal(simulation or real)
    prepare stock object after reading code list
*/


StockModel::StockModel()
: QObject(0), provider(DataProvider::getInstance()) {
    //QStringList codes = provider->requestYesterdayTopAmount();
    //qWarning() << "code list " << codes;
}


StockModel::~StockModel() {}


StockObject * StockModel::getStockObject(const QString &code) const {
    return DataProvider::getInstance().getStockObject(code);
}

QString StockModel::getCompanyName(const QString &code) {
    StockObject *obj = getStockObject(code);
    if (obj) 
        return obj->getCompanyName();

    return QString();
}

qreal StockModel::getCurrentProfit(const QString &code) {
    StockObject *obj = getStockObject(code);
    if (obj) {
        double current = (double)obj->getCurrentPrice();
        double yclose = (double)obj->getYesterdayClose();
        qreal profit = (current - yclose) / yclose * 100.;
        return profit;
    }

    return 0.0;
}


QPixmap * StockModel::createTickChart(const QString &code, int beforeDuration) const {
    StockObject *obj = getStockObject(code);
    if (obj == NULL) {
        qWarning() << code << " stock object is NULL";
        return new QPixmap(200, 100);
    }

    QList<StockObject::PeriodTickData *> ptd = obj->getPeriodData(TimeInfo::getInstance().getCurrentDateTime(), beforeDuration);
    if (ptd.count() == 0) {
        qWarning() << code << " period tick count is zero";
        return new QPixmap(200, 100);
    }
    return ChartCreator::createTickPixmapChart(ptd, code, obj->getYesterdayClose(), obj->getTodayOpen(), obj->getTodayHigh(), obj->getTodayLow());
}


void StockModel::startSimulation(QDateTime dt) {
    DataProvider::getInstance().startSimulation(dt.toTime_t());
}



