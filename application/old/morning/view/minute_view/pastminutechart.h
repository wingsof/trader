#ifndef PAST_MINUTE_CHART_H_
#define PAST_MINUTE_CHART_H_

#include <QtCharts>

using namespace QtCharts;

#include "stock_server/stock_provider.grpc.pb.h"
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;

class PastMinuteChart : public QChartView {
Q_OBJECT
public:
    PastMinuteChart(QWidget *p=0);
    void setData(CybosDayDatas *data, int minPrice, int maxPrice);

private:
    QChart *chart;
    QCandlestickSeries *candleSeries;
    QDateTimeAxis * datetimeAxis;
};


#endif
