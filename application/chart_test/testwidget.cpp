#include "testwidget.h"
#include "chart_creator.h"
#include <QPainter>


TestWidget::TestWidget(QWidget *p)
: QWidget(p) {
    //resize(150, 70);
    pixmap = ChartCreator::createTickPixmapChart(this);
    resize(1280, 720);
}


void TestWidget::paintEvent(QPaintEvent *p) {
    QPainter painter(this);
    painter.drawPixmap(QRect(0,0,200,100), *pixmap, QRect(0,0,200,100));
    //painter.fillRect(QRect(0, 100, 200, 100), QBrush(QColor(Qt::yellow)));
}
