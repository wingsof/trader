#ifndef MINUTE_WINDOW_H_
#define MINUTE_WINDOW_H_


#include <QWidget>

class StockModel;

#include <QtCharts>

using namespace QtCharts;

#include "stock_server/stock_provider.grpc.pb.h"
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;

class PastMinuteChart;
class RealtimeMinuteChart;


class MinuteWindow : public QWidget {
Q_OBJECT
public:
    MinuteWindow(StockModel &model, QWidget *p=0);

private:
    StockModel &stockModel;
    PastMinuteChart *yesterdayChartView;
    PastMinuteChart *beforeYesterdayChartView;
    RealtimeMinuteChart *todayChartView;
    QString currentCode;

    void displayPastData(CybosDayDatas *data, const QString &code);

private slots:
    void codeChanged(const QString &);
    void pastMinuteDataArrived(QString);
};


#endif
