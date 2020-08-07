#include "qwt_minutewindow.h"
#include "qwt_pastminutechart.h"

#include <google/protobuf/util/time_util.h>
#include <QDateTime>
#include <QHBoxLayout>

#include <QDebug>
using google::protobuf::util::TimeUtil;


QwtMinuteWindow::QwtMinuteWindow(QWidget *p)
: QWidget(p) {
    QHBoxLayout * layout = new QHBoxLayout;
    yesterdayChartView = new QwtPastMinuteChart;
    beforeYesterdayChartView = new QwtPastMinuteChart;
    yesterdayChartView->resize(600, 480);
    beforeYesterdayChartView->resize(600, 480);
    layout->addWidget(beforeYesterdayChartView);
    layout->addWidget(yesterdayChartView);
    layout->setSpacing(0);
    layout->setContentsMargins(0, 0, 0, 0);
    setLayout(layout);
    resize(1200, 480);
}


void QwtMinuteWindow::displayPastData(CybosDayDatas * data) {
    qWarning() << "displayPastData" << data->day_data_size();
    if (data->day_data_size() == 0)
        return;
    
    int currentDate = data->day_data(0).date();
    int high = 0;
    int low = 10000000;
    std::vector<CybosDayDatas> v;
    CybosDayDatas dayData;

    for (int i = 0; i < data->day_data_size(); ++i) {
        const CybosDayData &d = data->day_data(i);
        if (d.lowest_price() < low)
            low = d.lowest_price();

        if (d.highest_price() > high)
            high = d.highest_price();

        if (d.date() != currentDate || i == data->day_data_size() - 1) {
            v.push_back(dayData);
            dayData.Clear();
            currentDate = d.date();
        }
        else {
            CybosDayData * d = dayData.add_day_data();
            d->CopyFrom(data->day_data(i));
        }
    }
    qWarning() << "past minute data size " << v.size();
    if (v.size() == 2) {
        beforeYesterdayChartView->setData(&v[0], low, high);
        yesterdayChartView->setData(&v[1], low, high);
    }
    else if (v.size() == 1) {
        yesterdayChartView->setData(&v[0], low, high);
    }

}


void QwtMinuteWindow::clearData() {
    yesterdayChartView->clearData();
    beforeYesterdayChartView->clearData();
}
