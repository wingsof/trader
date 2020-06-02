#include "pastminutechart.h"


PastMinuteChart::PastMinuteChart(QWidget * p)
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
    dt.setTime(QTime(0, 0, 0));
    datetimeAxis->setRange(dt.addDays(-1), dt);

    chart->addAxis(priceAxis, Qt::AlignLeft);
    chart->addAxis(datetimeAxis, Qt::AlignBottom);
    chart->setMargins(QMargins(0,0,0,0));
    chart->legend()->setVisible(false);

    candleSeries->attachAxis(priceAxis);
    candleSeries->attachAxis(datetimeAxis);

    setChart(chart);
    setRenderHint(QPainter::Antialiasing);
}


void PastMinuteChart::setData(CybosDayDatas *data, int minPrice, int maxPrice) {
    qWarning() << "PastMinuteChart::setData " << data->day_data_size();
    QDateTime fromDate;
    QDateTime untilDate;
    candleSeries->clear();
    //datetimeAxis->clear();
    for (int i = 0; i < data->day_data_size(); ++i) {
        const CybosDayData &d = data->day_data(i);
        unsigned int date = d.date();
        QDateTime dt(QDate(int(date / 10000),
                            int(date % 10000 / 100),
                            int(date % 100)));
        dt.setTime(QTime(int(d.time() / 100), int(d.time() % 100)));
        if (i == 0)
            fromDate = dt;
        else if (i == data->day_data_size() - 1)
            untilDate = dt;

        candleSeries->append(new QCandlestickSet(
                                d.start_price(), d.highest_price(),
                                d.lowest_price(), d.close_price(),
                                dt.toMSecsSinceEpoch()));
        //datetimeAxis->append(dt.toString("yyyy/MM/dd"));
    }
    if (data->day_data_size() > 0) {
        qWarning() << "PastMinuteChart" << fromDate << untilDate;
        chart->axisX()->setRange(fromDate, untilDate);
        chart->axisY()->setRange(minPrice, maxPrice);
        qobject_cast<QValueAxis*>(chart->axisY())->applyNiceNumbers();
    }
}


void PastMinuteChart::clearData() {
    candleSeries->clear();
}
