#ifndef CHART_CREATOR_H_
#define CHART_CREATOR_H_

#include <QPixmap>
#include <QtCharts>
#include <QPainter>
#include <QDebug>

using namespace QtCharts;


class ChartCreator {
public:
    static QPixmap * createTickPixmapChart(QWidget *p) {
        QChart * chart = new QChart;
        QSplineSeries * priceSeries = new QSplineSeries;
        //QLineSeries * lineSeries = new QLineSeries;
        QPen pen = priceSeries->pen();
        pen.setColor(Qt::black);
        priceSeries->setPen(pen);

        QList<QDateTime> dt;
        for (int j = 0; j < 19; ++j) {
            dt << QDateTime(QDate(2020, 4, 7), QTime(9, 10, 0+j));
        }
        QList<int> prices;
        prices << 21600 <<21600<<21600<<21650<<21600<<
                21650<<21600<<21600<<21650<<21650<<
                21650<<21700<<21700<<21600<<21650<<
                21650<<21650<<21700<<21650;

        for (int j = 0; j < 19; ++j) {
            priceSeries->append(dt.at(j).toMSecsSinceEpoch(), prices.at(j));
        }

        //lineSeries->append(t1.toMSecsSinceEpoch(), 102);
        //lineSeries->append(t6.toMSecsSinceEpoch(), 102);

        chart->addSeries(priceSeries);
        //chart->addSeries(lineSeries);
        QValueAxis * priceAxis = new QValueAxis;
        priceAxis->setRange(21600 * 0.99, 21700 * 1.01);
        QDateTimeAxis * datetimeAxis = new QDateTimeAxis;
        datetimeAxis->setTickCount(30);
        datetimeAxis->setFormat("");

        chart->addAxis(priceAxis, Qt::AlignLeft);
        chart->addAxis(datetimeAxis, Qt::AlignBottom);
        chart->setMargins(QMargins(0,0,0,0));
        //chart->setPlotArea(QRectF(0,0,200,100));

        priceSeries->attachAxis(priceAxis);
        priceSeries->attachAxis(datetimeAxis);

        //lineSeries->attachAxis(priceAxis);
        //lineSeries->attachAxis(datetimeAxis);

        priceAxis->hide();
        chart->legend()->setVisible(false);

        QChartView * view = new QChartView(chart);
        view->setRenderHint(QPainter::Antialiasing);
        view->resize(200, 100);
        QPixmap grabPixmap = view->grab();
        qWarning() << grabPixmap.width() << ", " << grabPixmap.height();
        QPixmap * pixmap = new QPixmap(view->grab());

        /*
        QChartView * view = new QChartView(chart);
        view->setRenderHint(QPainter::Antialiasing);
        QPixmap * pixmap = new QPixmap(150, 70);
        QPainter painter(pixmap);
        view->render(&painter);
        */

        return pixmap; 
    }
};

#endif
