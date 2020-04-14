#include "testwidget.h"
#include "chart_creator.h"
#include <QPainter>
#include <QVBoxLayout>
#include <QDateTime>
#include <QDebug>
#include <QPen>

TestWidget::TestWidget(QWidget *p)
: QWidget(p) {
    //resize(150, 70);
    //pixmap = ChartCreator::createTickPixmapChart(this);
    QVBoxLayout * layout = new QVBoxLayout;
    chart = new QChart;
    candleSeries = new QCandlestickSeries;
    candleSeries->setUseOpenGL(true);
    //addTestData();
    candleSeries->setIncreasingColor(QColor(Qt::red));
    candleSeries->setDecreasingColor(QColor(Qt::blue));
    candleSeries->setBodyOutlineVisible(false);
    QPen pen = candleSeries->pen();
    pen.setWidth(1);
    candleSeries->setPen(pen);
    QDateTime dt = QDateTime::currentDateTime();

    QValueAxis *priceAxis = new QValueAxis;
    QBarCategoryAxis *datetimeAxis = new QBarCategoryAxis;
    /*
    for (int i = -30; i < 0; ++i) {
        qWarning() << dt.addDays(i).toString("yyyy/MM/dd");
        datetimeAxis->append(dt.addDays(i).toString("yyyy/MM/dd"));
    }*/
    //priceAxis->setRange(50, 200);
    //datetimeAxis->setRange(dt.addDays(-10), dt);
    chart->addSeries(candleSeries);
    chart->addAxis(priceAxis, Qt::AlignLeft);
    chart->addAxis(datetimeAxis, Qt::AlignBottom);
    //chart->setMargins(QMargins(0,0,0,0));
    chart->legend()->setVisible(false);

    candleSeries->attachAxis(priceAxis);
    candleSeries->attachAxis(datetimeAxis);
    view = new QChartView(chart, this);
    view->setRenderHint(QPainter::Antialiasing);

    QPushButton * button = new QPushButton("Add");
    connect(button, SIGNAL(clicked()), SLOT(addData()));
    layout->addWidget(view);
    layout->addWidget(button);
    setLayout(layout);
    resize(1280, 720);
}


void TestWidget::addTestData() {
    candleSeries->clear();
    QDateTime dt = QDateTime::currentDateTime();
    bool result = candleSeries->append(new QCandlestickSet(100, 110, 90, 110, dt.addDays(-10).toMSecsSinceEpoch()));
    qWarning() << "append result " << result;
    candleSeries->append(new QCandlestickSet(110, 120, 100, 120, dt.addDays(-9).toMSecsSinceEpoch()));
    candleSeries->append(new QCandlestickSet(120, 130, 110, 130, dt.addDays(-8).toMSecsSinceEpoch()));
    candleSeries->append(new QCandlestickSet(130, 140, 120, 140, dt.addDays(-7).toMSecsSinceEpoch()));
    candleSeries->append(new QCandlestickSet(140, 150, 130, 150, dt.addDays(-6).toMSecsSinceEpoch()));
    candleSeries->append(new QCandlestickSet(150, 160, 140, 160, dt.addDays(-4).toMSecsSinceEpoch()));
    candleSeries->append(new QCandlestickSet(160, 170, 150, 170, dt.addDays(-3).toMSecsSinceEpoch()));
    candleSeries->append(new QCandlestickSet(170, 180, 160, 180, dt.addDays(-2).toMSecsSinceEpoch()));
    candleSeries->append(new QCandlestickSet(180, 190, 170, 190, dt.addDays(-1).toMSecsSinceEpoch()));
}


void TestWidget::addData() {
    qWarning() << "addData";
    
    addTestData();
    
    QDateTime dt = QDateTime::currentDateTime();
    QBarCategoryAxis * axis = qobject_cast<QBarCategoryAxis*>(chart->axisX());
    axis->clear();
    for (int i = -9; i < 0; ++i) {
        axis->append(dt.addDays(i).toString("yyyy/MM/dd"));
    }
    
    chart->axisY()->setRange(50, 200);
    //view->update();
}

/*
void TestWidget::paintEvent(QPaintEvent *p) {
    QPainter painter(this);
    painter.drawPixmap(QRect(0,0,200,100), *pixmap, QRect(0,0,200,100));
    //painter.fillRect(QRect(0, 100, 200, 100), QBrush(QColor(Qt::yellow)));
}
*/
