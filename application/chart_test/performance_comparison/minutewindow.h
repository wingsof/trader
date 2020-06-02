#ifndef MINUTE_WINDOW_H_
#define MINUTE_WINDOW_H_


#include <QWidget>


#include "stock_provider.grpc.pb.h"
using stock_api::CybosDayDatas;
using stock_api::CybosDayData;

class PastMinuteChart;


class MinuteWindow : public QWidget {
Q_OBJECT
public:
    MinuteWindow(QWidget *p=0);

    void displayPastData(CybosDayDatas *data);
    void clearData();
private:
    PastMinuteChart *yesterdayChartView;
    PastMinuteChart *beforeYesterdayChartView;

};


#endif
