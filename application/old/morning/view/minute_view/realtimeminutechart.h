#ifndef REALTIME_MINUTE_CHART_H_
#define REALTIME_MINUTE_CHART_H_


#include <QtCharts>

using namespace QtCharts;

#include "stock_server/stock_object.h"

class RealtimeMinuteChart : public QChartView {
Q_OBJECT
public:
    RealtimeMinuteChart(QWidget *p=0);
    void setData(const QList<StockObject::PeriodTickData *> & minuteData, int minPrice, int maxPrice);
    void setCode(const QString &code);

private:
    QChart *chart;
    QCandlestickSeries *candleSeries;
    QDateTimeAxis * datetimeAxis;

    int openPrice;
    int highPrice;
    int lowPrice;

    void resetCurrentPrice();
    QString currentCode;

public slots:
    void currentPriceChanged(QString, unsigned int);
    void minuteDataUpdated(QString, StockObject::PeriodTickData *);
};


#endif
