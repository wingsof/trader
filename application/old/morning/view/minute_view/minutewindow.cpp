#include "minutewindow.h"

#include "stock_model/stockmodel.h"
#include "stock_server/stock_object.h"
#include "pastminutechart.h"
#include "realtimeminutechart.h"

#include <google/protobuf/util/time_util.h>
#include <QDateTime>
#include <QHBoxLayout>

#include <QDebug>
using google::protobuf::util::TimeUtil;


MinuteWindow::MinuteWindow(StockModel &model, QWidget *parent)
: QWidget(parent), stockModel(model) {
    connect(&stockModel, SIGNAL(currentCodeChanged(const QString &)),
            this, SLOT(codeChanged(const QString &)));
    QHBoxLayout *layout = new QHBoxLayout;
    yesterdayChartView = new PastMinuteChart;
    beforeYesterdayChartView = new PastMinuteChart;
    todayChartView = new RealtimeMinuteChart;

    yesterdayChartView->resize(600, 480);
    beforeYesterdayChartView->resize(600, 480);
    todayChartView->resize(600, 480);
    layout->addWidget(yesterdayChartView);
    layout->addWidget(beforeYesterdayChartView);
    layout->addWidget(todayChartView);
    layout->setSpacing(0);
    //layout->setContentMargin(0, 0, 0, 0);
    setLayout(layout);
    resize(1800, 480);
}



void MinuteWindow::pastMinuteDataArrived(QString code) {
    if (currentCode == code) {
        displayPastData(stockModel.getStockObject(code)->getPastMinuteDatas(), code);
    }
}


void MinuteWindow::displayPastData(CybosDayDatas *data, const QString &code) {
    qWarning() << "displayPastData" << data->day_data_size();
    if (data->day_data_size() == 0)
        return;
    
    int currentDate = data->day_data(0).date();
    qWarning() << "init current date" << currentDate;
    int high = stockModel.getStockObject(code)->getTodayHigh();
    int low = stockModel.getStockObject(code)->getTodayLow();
    std::vector<CybosDayDatas> v;
    CybosDayDatas dayData;

    for (int i = 0; i < data->day_data_size(); ++i) {
        const CybosDayData &d = data->day_data(i);
        if (d.lowest_price() < low)
            low = d.lowest_price();

        if (d.highest_price() > high)
            high = d.highest_price();

        qWarning() << "data date " << d.date();
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
    todayChartView->setData(stockModel.getStockObject(code)->getMinuteData(), low, high);
    connect(stockModel.getStockObject(currentCode), SIGNAL(currentPriceChanged(QString, unsigned int)), todayChartView, SLOT(currentPriceChanged(QString, unsigned int)));
    connect(stockModel.getStockObject(currentCode), SIGNAL(minuteDataUpdated(QString, StockObject::PeriodTickData *)), todayChartView, SLOT(minuteDataUpdated(QString, StockObject::PeriodTickData *)));
}


void MinuteWindow::codeChanged(const QString &code) {
    qWarning() << "codeChanged (minutewindow) " << code;
    if (code.length() > 0) {
        disconnect(stockModel.getStockObject(currentCode), SIGNAL(currentPriceChanged(QString, unsigned int)), todayChartView, SLOT(currentPriceChanged(QString, unsigned int)));
        disconnect(stockModel.getStockObject(currentCode), SIGNAL(minuteDataUpdated(QString, StockObject::PeriodTickData *)), todayChartView, SLOT(minuteDataUpdated(QString, StockObject::PeriodTickData *)));
    }

    currentCode = code;
    todayChartView->setCode(currentCode);
    CybosDayDatas * data = stockModel.getStockObject(code)->getPastMinuteDatas();
    if (data == NULL) {
        qWarning() << "connectToMinuteWindow";
        stockModel.getStockObject(code)->connectToMinuteWindow(this);
    }
    else {
        displayPastData(data, code);
    }
}
