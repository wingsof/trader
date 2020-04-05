#include "bullwidget.h"
#include <QVBoxLayout>
#include <QPushButton>


BullWidget::BullWidget()
: QWidget(0) {
    QVBoxLayout * layout = new QVBoxLayout;
    QPushButton * button = new QPushButton("Hello");
    layout->addWidget(button);
    setLayout(layout);
}


BullWidget::~BullWidget() {}
