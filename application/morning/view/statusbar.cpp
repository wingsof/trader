#include "statusbar.h"
#include <QPushButton>
#include <QDate>
#include <QDebug>


StatusBar::StatusBar(QWidget *p)
: QToolBar(p), simulationDate(QDate::currentDate()) {
    startAction = addWidget(new QPushButton("start"));
    addSeparator();
    addSeparator();
    dateLabel = new QLabel(simulationDate.toString("yyyy/M/d"));
    addWidget(dateLabel);
    QPushButton *dateButton = new QPushButton("Date");
    addWidget(dateButton);
    connect(dateButton, SIGNAL(clicked()), SLOT(showCalendarWidget()));
    QPushButton *startSimulationButton = new QPushButton("start simulation");
    simulationAction = addWidget(startSimulationButton);
    connect(startSimulationButton, SIGNAL(clicked()), SLOT(prepareSimulation()));
}


StatusBar::~StatusBar() {}


void StatusBar::showCalendarWidget() {
    DatePick pick;
    connect(&pick, SIGNAL(dateSelected(const QDate &)), SLOT(dateSelected(const QDate &)));
    connect(&pick, SIGNAL(dateSelected(const QDate &)), &pick, SLOT(accept()));
    pick.exec();
}


void StatusBar::dateSelected(const QDate &d) {
    simulationDate = d;
    dateLabel->setText(simulationDate.toString("yyyy/M/d"));
}


void StatusBar::prepareSimulation() {
    simulationAction->setEnabled(false);
    emit startSimulation(simulationDate); 
}
