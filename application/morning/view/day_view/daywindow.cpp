#include "daywindow.h"

#include "stock_model/stockmodel.h"
#include "stock_server/stock_object.h"
#include <google/protobuf/util/time_util.h>
#include <QDateTime>

#include <QDebug>
using google::protobuf::util::TimeUtil;


DayWindow::DayWindow(StockModel &model, QWidget *parent)
: QWidget(parent), stockModel(model) {
    connect(&stockModel, SIGNAL(currentCodeChanged(const QString &)),
            this, SLOT(codeChanged(const QString &)));
    chart = new QChart;

    candleSeries = new QCandlestickSeries;
    candleSeries->setIncreasingColor(QColor(Qt::red));
    candleSeries->setDecreasingColor(QColor(Qt::blue));
    candleSeries->setBodyOutlineVisible(false);
    QPen pen = candleSeries->pen();
    pen.setWidth(1);
    chart->addSeries(candleSeries);

    QValueAxis *priceAxis = new QValueAxis;
    priceAxis->setTickCount(10);
    datetimeAxis = new QDateTimeAxis;
    QDateTime dt = QDateTime::currentDateTime();
    datetimeAxis->setRange(dt.addDays(-180), dt);
    
    chart->addAxis(priceAxis, Qt::AlignLeft);
    chart->addAxis(datetimeAxis, Qt::AlignBottom);
    chart->setMargins(QMargins(0,0,0,0));
    chart->legend()->setVisible(false);

    candleSeries->attachAxis(priceAxis);
    candleSeries->attachAxis(datetimeAxis);
    view = new QChartView(chart, this);
    view->setRenderHint(QPainter::Antialiasing);
    view->resize(800, 480);
}


void DayWindow::createCandleData(CybosDayDatas *data) {
    qWarning() << "createCandleData size " << data->day_data_size();
    QDateTime fromDate;
    QDateTime untilDate;
    candleSeries->clear();
    //datetimeAxis->clear();
    int max_price = 0;
    int min_price = 100000000;
    for (int i = 0; i < data->day_data_size(); ++i) {
        const CybosDayData &d = data->day_data(i);
        unsigned int date = d.date();
        QDateTime dt(QDate(int(date / 10000),
                            int(date % 10000 / 100),
                            int(date % 100)));
        if (i == 0)
            fromDate = dt;
        else if (i == data->day_data_size() - 1)
            untilDate = dt;

        if (d.highest_price() > max_price)
            max_price = d.highest_price();
        
        if (d.lowest_price() < min_price)
            min_price = d.lowest_price();

        candleSeries->append(new QCandlestickSet(
                                d.start_price(), d.highest_price(),
                                d.lowest_price(), d.close_price(),
                                dt.toMSecsSinceEpoch()));
        //datetimeAxis->append(dt.toString("yyyy/MM/dd"));
    }
    if (data->day_data_size() > 0) {
        chart->axisX()->setRange(fromDate, untilDate);
        chart->axisY()->setRange(min_price * 0.9, max_price * 1.1);
        qobject_cast<QValueAxis*>(chart->axisY())->applyNiceNumbers();
    }
}


void DayWindow::dayDataArrived(QString code) {
    if (currentCode == code) {
        candleSeries->clear();
        createCandleData(stockModel.getStockObject(code)->getDayDatas());
    }
}


void DayWindow::codeChanged(const QString &code) {
    qWarning() << "codeChanged (dayWindow) " << code;
    currentCode = code;
    CybosDayDatas * data = stockModel.getStockObject(code)->getDayDatas();
    candleSeries->clear();
    if (data == NULL) {
        stockModel.getStockObject(code)->connectToDayWindow(this);
    }
    else {
        createCandleData(data);
    }
}
