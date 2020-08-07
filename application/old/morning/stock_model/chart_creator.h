#ifndef CHART_CREATOR_H_
#define CHART_CREATOR_H_

#include <QPixmap>
#include <QtCharts>
#include <QPainter>
#include "stock_server/stock_object.h"

using namespace QtCharts;

#include <QFile>
#include <QDebug>

class ChartCreator {
public:
    static QPixmap * createTickPixmapChart(QList<StockObject::PeriodTickData *> & ptdList,
                                           const QString &code,
                                           unsigned int yesterdayClose,
                                           unsigned int todayOpen,
                                           unsigned int todayHigh,
                                           unsigned int todayLow) {
        QChart * chart = new QChart;
        QSplineSeries * priceSeries = new QSplineSeries;
        QPen pen = priceSeries->pen();
        pen.setColor(Qt::black);
        priceSeries->setPen(pen);
        double max_price = 0;
        double min_price = 0;

        QListIterator<StockObject::PeriodTickData *> i(ptdList);
        while (i.hasNext()) {
            StockObject::PeriodTickData * ptd = i.next();
            priceSeries->append(ptd->date.toMSecsSinceEpoch(), ptd->close);

            if (min_price == 0)
                min_price = ptd->close;

            if (ptd->close > max_price)
                max_price = ptd->close;

            if (ptd->close < ptd->close)
                min_price = ptd->close;
        }

        chart->addSeries(priceSeries);

        // TODO: create lineseries when open, high, close, low is in range of priceSeries
        QValueAxis *priceAxis = new QValueAxis;
        priceAxis->setRange(min_price * 0.99, max_price * 1.01);
        QDateTimeAxis *datetimeAxis = new QDateTimeAxis;
        datetimeAxis->setTickCount(ptdList.count());
        datetimeAxis->setFormat("");

        chart->addAxis(priceAxis, Qt::AlignLeft);
        chart->addAxis(datetimeAxis, Qt::AlignBottom);
        chart->setMargins(QMargins(0,0,0,0));

        priceSeries->attachAxis(priceAxis);
        priceSeries->attachAxis(datetimeAxis);

        priceAxis->hide();
        chart->legend()->setVisible(false);

        QChartView * view = new QChartView(chart);
        view->setRenderHint(QPainter::Antialiasing);
        view->resize(200, 100);
        QPixmap * pixmap = new QPixmap(view->grab());        
        delete view;
        return pixmap; 
    }
};

#endif
