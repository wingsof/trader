#include "tickwindow.h"
#include <QtCharts/QChartView>
#include "view/viewcontroller.h"

using namespace QtCharts;

TickWindow::TickWindow(QWidget *parent)
: QWidget(parent) {
    QChartView *v = new QChartView(this);
    v->setRenderHint(QPainter::Antialiasing);
    resize(1280, 720);
}

TickWindow::~TickWindow() {

}


void TickWindow::codeChanged(QString code) {

}
