#ifndef DAY_WINDOW_H_
#define DAY_WINDOW_H_


#include <QWidget>

class StockModel;

#include <QtCharts>

using namespace QtCharts;

#include "stock_server/stock_provider.grpc.pb.h"
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;


class DayWindow : public QWidget {
Q_OBJECT
public:
    DayWindow(StockModel &model, QWidget *p=0);

private:
    StockModel &stockModel;
    QCandlestickSeries *candleSeries;
    QString currentCode;
    QChart *chart;
    QChartView *view;
    QDateTimeAxis *datetimeAxis;

    void createCandleData(CybosDayDatas * data);

private slots:
    void codeChanged(const QString &);
    void dayDataArrived(QString);
};


#endif