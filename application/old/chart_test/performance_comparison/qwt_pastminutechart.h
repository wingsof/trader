#ifndef QWT_WIDGET_H_
#define QWT_WIDGET_H_

#include <QWidget>
#include <QVector>
#include <qwt_samples.h>


#include "stock_provider.grpc.pb.h"
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;

class QwtPlot;
class QwtDateScaleDraw;
class QwtPlotTradingCurve;


class QwtPastMinuteChart : public QWidget {
Q_OBJECT
public:
    QwtPastMinuteChart(QWidget *p=0);
    QVector<QwtOHLCSample> addTestData();

    void setData(CybosDayDatas *data, int minPrice, int maxPrice);
    void clearData();

private:
    QwtPlot *plot;
    QwtDateScaleDraw *scaleDraw;
    QwtPlotTradingCurve *curve;

    QDateTime convertToDateTime(int d, int t);
};


#endif
