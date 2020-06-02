#include "realtimeminutechart.h"

#include "stock_server/stock_object.h"


RealtimeMinuteChart::RealtimeMinuteChart(QWidget *p)
: QChartView(p) {
    chart = new QChart;
    candleSeries = new QCandlestickSeries;
    candleSeries->setIncreasingColor(QColor(Qt::red));
    candleSeries->setDecreasingColor(QColor(Qt::blue));
    candleSeries->setBodyOutlineVisible(false);
    QPen pen = candleSeries->pen();
    pen.setWidth(1);
    chart->addSeries(candleSeries);
    QValueAxis *priceAxis = new QValueAxis;
    priceAxis->setTickCount(10);
    datetimeAxis = new QDateTimeAxis;
    QDateTime dt = QDateTime::currentDateTime();
    dt.setTime(QTime(9, 0, 0));
    QDateTime untilDt = QDateTime::currentDateTime();
    untilDt.setTime(QTime(15, 30, 0));
    datetimeAxis->setRange(dt, untilDt);

    chart->addAxis(priceAxis, Qt::AlignLeft);
    chart->addAxis(datetimeAxis, Qt::AlignBottom);
    chart->setMargins(QMargins(0,0,0,0));
    chart->legend()->setVisible(false);

    candleSeries->attachAxis(priceAxis);
    candleSeries->attachAxis(datetimeAxis);

    setChart(chart);
    setRenderHint(QPainter::Antialiasing);
}


void RealtimeMinuteChart::setData(const QList<StockObject::PeriodTickData *> & minuteData, int minPrice, int maxPrice) {

}


void RealtimeMinuteChart::resetCurrentPrice() {
    openPrice = 0;
    highPrice = 0;
    lowPrice = 0;
}


void RealtimeMinuteChart::setCode(const QString &code) {
    currentCode = code;
    resetCurrentPrice();
    candleSeries->clear();
}


void RealtimeMinuteChart::minuteDataUpdated(QString code, StockObject::PeriodTickData *data) {

}


void RealtimeMinuteChart::currentPriceChanged(QString code, unsigned int price) {

}
