#ifndef TEST_WIDGET_H_
#define TEST_WIDGET_H_

#include <QWidget>
#include <QtCharts>
#include <QDebug>

using namespace QtCharts;

class TestWidget : public QWidget {
Q_OBJECT
public:
    TestWidget(QWidget *p=0);

protected:
    //void paintEvent(QPaintEvent *p);


private:
    QPixmap *pixmap;
    QChartView *view;
    QChart *chart;
    QCandlestickSeries * candleSeries;

    void addTestData();

private slots:
    void addData();
};


#endif
