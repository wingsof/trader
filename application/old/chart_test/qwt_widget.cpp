#include "qwt_widget.h"

#include <qwt_plot.h>
#include <qwt_date.h>
#include <qwt_samples.h>
#include <qwt_date_scale_draw.h>
#include <qwt_plot_tradingcurve.h>
#include <qwt_plot_barchart.h>
#include <QVector>
#include <QDebug>
#include <QVBoxLayout>

QwtTestWidget::QwtTestWidget(QWidget *p)
: QWidget(p) {
    QVBoxLayout * layout = new QVBoxLayout;
    QwtPlot * plot = new QwtPlot;
    QwtDateScaleDraw *scaleDraw = new QwtDateScaleDraw( Qt::UTC );
    scaleDraw->setDateFormat( QwtDate::Millisecond, "MM/dd" );
    scaleDraw->setDateFormat( QwtDate::Second, "MM/dd" );
    scaleDraw->setDateFormat( QwtDate::Minute, "MM/dd" );
    scaleDraw->setDateFormat( QwtDate::Hour, "MM/dd" );
    scaleDraw->setDateFormat( QwtDate::Day, "MM/dd" );
    scaleDraw->setDateFormat( QwtDate::Week, "Www" );

    plot->setAxisScaleDraw(QwtPlot::xBottom, scaleDraw);

    QDateTime dt = QDateTime::currentDateTime();
    dt.setTime(QTime(0,0));
    plot->setAxisScale(QwtPlot::xBottom, QwtDate::toDouble(dt.addDays(-10)),
                        QwtDate::toDouble(dt.addDays(-1)), 24 * 3600 * 1000);

    QwtPlotTradingCurve *curve = new QwtPlotTradingCurve();
    curve->setOrientation(Qt::Vertical);

    //curve->setSymbolExtent( 12 * 3600 * 1000.0 );
    curve->setMinSymbolWidth( 10 );
    curve->setMaxSymbolWidth( 20 );
    curve->setSamples(addTestData());
    curve->setSymbolBrush( QwtPlotTradingCurve::Decreasing, Qt::blue);
    curve->setSymbolBrush( QwtPlotTradingCurve::Increasing, Qt::red);

    curve->attach(plot); 
    curve->setVisible(true);

    
    layout->addWidget(plot);
    QwtPlot * barPlot = new QwtPlot;
    barPlot->setAxisScaleDraw(QwtPlot::xBottom, scaleDraw);
    barPlot->setAxisScale(QwtPlot::xBottom, QwtDate::toDouble(dt.addDays(-10)),
                        QwtDate::toDouble(dt.addDays(-1)), 24 * 3600 * 1000);
    QwtPlotBarChart * barChart = new QwtPlotBarChart;
    QVector<double> volumes = {10000, 20000, 15000, 30000, 5000};
    barChart->setSamples(volumes);
    barChart->attach(barPlot);
    barChart->setVisible(true);
    layout->addWidget(barPlot);
    setLayout(layout);
}


QVector<QwtOHLCSample> QwtTestWidget::addTestData() {
    QVector<QwtOHLCSample> samples;
    const int dataCount = 5;
    int sampleOhlc[][5] = {
        {100, 110, 90, 110, 10000},
        {110, 120, 100, 120, 20000},
        {120, 130, 110, 130, 15000},
        {130, 140, 120, 110, 30000},
        {140, 150, 130, 145, 5000}
    };
    QDateTime dt = QDateTime::currentDateTime();
    dt.setTime(QTime(0,0));
    int j = 0;
    for (int i = -1 * dataCount; i < 0; ++i) {
        samples += QwtOHLCSample(QwtDate::toDouble(dt.addDays(i)),
                                sampleOhlc[j][0],
                                sampleOhlc[j][1],
                                sampleOhlc[j][2],
                                sampleOhlc[j][3]);
        j += 1;
        qWarning() << "data date " << dt.addDays(i);
    }
    samples += QwtOHLCSample(QwtDate::toDouble(dt.addDays(-10)),
                            80, 85, 75, 78);

    return samples;
}
