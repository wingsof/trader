#include "comparewidget.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>
#include "qwt_minutewindow.h"
#include "minutewindow.h"
#include "data_provider.h"


CompareWidget::CompareWidget(QWidget *p)
: QWidget(p) {
    //QVBoxLayout * layout = new QVBoxLayout;

    minuteWindow = new MinuteWindow(this);
    qwtMinuteWindow = new QwtMinuteWindow(this);

    QWidget *w = new QWidget(this);
    QHBoxLayout * hLayout = new QHBoxLayout;

    QPushButton * display1 = new QPushButton("Display 1");
    QPushButton * clear1 = new QPushButton("Clear 1");
    QPushButton * display2 = new QPushButton("Display 2");
    QPushButton * clear2 = new QPushButton("Clear 2");
    connect(display1, SIGNAL(clicked()), SLOT(displayData1()));
    connect(display2, SIGNAL(clicked()), SLOT(displayData2()));
    connect(clear1, SIGNAL(clicked()), SLOT(clearData1()));
    connect(clear2, SIGNAL(clicked()), SLOT(clearData2()));
    hLayout->addWidget(display1);
    hLayout->addWidget(clear1);
    hLayout->addWidget(display2);
    hLayout->addWidget(clear2);

    w->setLayout(hLayout);

    minuteWindow->setGeometry(0, 0, 1280, 480);
    qwtMinuteWindow->setGeometry(0, 480, 1280, 480);
    w->setGeometry(0, 960, 1280, 50);
    //layout->addWidget(w);

    //setLayout(layout);
}


void CompareWidget::displayData1() {
    minuteWindow->displayPastData(DataProvider::getInstance().getMinuteData());
}

void CompareWidget::displayData2() {
    qwtMinuteWindow->displayPastData(DataProvider::getInstance().getMinuteData());
}


void CompareWidget::clearData1() {
    minuteWindow->clearData();
}


void CompareWidget::clearData2() {
    qwtMinuteWindow->clearData();
}
