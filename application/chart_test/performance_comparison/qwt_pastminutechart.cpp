#include "qwt_pastminutechart.h"

#include <qwt_plot.h>
#include <qwt_date.h>
#include <qwt_samples.h>
#include <qwt_date_scale_draw.h>
#include <qwt_plot_tradingcurve.h>
#include <QVector>
#include <QDebug>


QwtPastMinuteChart::QwtPastMinuteChart(QWidget *p)
: QWidget(p) {
    plot = new QwtPlot(this);

    scaleDraw = new QwtDateScaleDraw( Qt::UTC );
    scaleDraw->setDateFormat( QwtDate::Millisecond, "hh:mm" );
    scaleDraw->setDateFormat( QwtDate::Second, "hh:mm" );
    scaleDraw->setDateFormat( QwtDate::Minute, "hh:mm" );
    scaleDraw->setDateFormat( QwtDate::Hour, "hh:mm" );
    scaleDraw->setDateFormat( QwtDate::Day, "hh:mm" );
    scaleDraw->setDateFormat( QwtDate::Week, "Www" );

    plot->setAxisScaleDraw(QwtPlot::xBottom, scaleDraw);

    QDateTime dt = QDateTime::currentDateTime();
    dt.setTime(QTime(0,0));

    curve = new QwtPlotTradingCurve();
    curve->setOrientation(Qt::Vertical);

    //curve->setSymbolExtent( 12 * 3600 * 1000.0 );
    //curve->setMinSymbolWidth( 10 );
    //curve->setMaxSymbolWidth( 20 );
    //curve->setSamples(addTestData());
    curve->setSymbolBrush( QwtPlotTradingCurve::Decreasing, Qt::blue);
    curve->setSymbolBrush( QwtPlotTradingCurve::Increasing, Qt::red);

    curve->attach(plot); 
    curve->setVisible(true);
    plot->resize(600, 480);
}


void QwtPastMinuteChart::clearData() {
    qWarning() << "QwtPastMinuteChart clearData";
    QVector<QwtOHLCSample> samples;
    curve->setSamples(samples);
    plot->replot();
}


QDateTime QwtPastMinuteChart::convertToDateTime(int d, int t) {
    QDateTime dt(QDate(int(d / 10000),
                        int(d % 10000 / 100),
                        int(d % 100)));
    dt.setTime(QTime(int(t / 100), int(t % 100)));
    return dt;
}


void QwtPastMinuteChart::setData(CybosDayDatas *data, int minPrice, int maxPrice) {
    int dataSize = data->day_data_size();
    if ( dataSize == 0) {
        clearData();
        return;
    }

    QVector<QwtOHLCSample> samples;
    QDateTime fromDate = convertToDateTime(data->day_data(0).date(), data->day_data(0).time());
    QDateTime untilDate = convertToDateTime(data->day_data(dataSize - 1).date(), 
                                            data->day_data(dataSize - 1).time());;
    QDateTime timeCursor = fromDate;
    int o, h, l, c;
    o = h = l = c = 0;

    for (int i = 0; i < data->day_data_size(); ++i) {
        const CybosDayData &d = data->day_data(i);
        unsigned int date = d.date();
        
        samples += QwtOHLCSample(QwtDate::toDouble(dt), d.start_price(),
                                d.highest_price(), d.lowest_price(),
                                d.close_price());
    }
    if (data->day_data_size() > 0) {
        qWarning() << "QwtPastMinuteChart" << fromDate << untilDate;
        plot->setAxisScale(QwtPlot::xBottom, QwtDate::toDouble(fromDate),
                        QwtDate::toDouble(untilDate), 3600 * 1000);
        plot->setAxisScale(QwtPlot::yLeft, minPrice, maxPrice);
        plot->setAxisTitle( QwtPlot::xBottom, untilDate.toString("MM/dd") );

        curve->setSamples(samples);
        plot->replot();
    }
}
