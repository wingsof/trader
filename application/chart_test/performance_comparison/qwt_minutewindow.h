#ifndef QWT_MINUTE_WINDOW_H_
#define QWT_MINUTE_WINDOW_H_

#include <QWidget>


#include "stock_provider.grpc.pb.h"
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;

class QwtPastMinuteChart;


class QwtMinuteWindow : public QWidget {
Q_OBJECT
public:
    QwtMinuteWindow(QWidget *p=0);
    void displayPastData(CybosDayDatas *data);
    void clearData();

private:
    QwtPastMinuteChart * yesterdayChartView;
    QwtPastMinuteChart * beforeYesterdayChartView;
};

#endif
