#include "SearchBackend.h"
#include <QDebug>
#include <QProcess>
#include <QStringList>


SearchBackend::SearchBackend(QObject *parent)
: QObject(parent) {
    m_currentCode = "";
    m_currentDateTime = QDateTime::currentDateTime();
    m_serverDateTime = QDateTime::currentDateTime();
    m_days = 120;
    m_simulationSpeed = 1.0;

    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged,
            this, &SearchBackend::stockCodeChanged);
    connect(DataProvider::getInstance(), &DataProvider::timeInfoArrived, this, &SearchBackend::timeInfoArrived);
    connect(DataProvider::getInstance(), &DataProvider::simulationStatusChanged, this, &SearchBackend::setSimulationStatus);
    DataProvider::getInstance()->startStockCodeListening();
    DataProvider::getInstance()->startTimeListening();
    m_simulationRunning = DataProvider::getInstance()->isSimulation();
    qWarning() << "SearchBackend";
}


void SearchBackend::timeInfoArrived(QDateTime dt) {
    setServerDateTime(dt);
}


QString SearchBackend::currentCode() {
    return m_currentCode;
}


QDateTime SearchBackend::currentDateTime() {
    return m_currentDateTime; 
}


int SearchBackend::days() {
    return m_days;
}


qreal SearchBackend::simulationSpeed() {
    return m_simulationSpeed;
}


bool SearchBackend::simulationRunning() {
    return m_simulationRunning;
}


QDateTime SearchBackend::serverDateTime() {
    return m_serverDateTime;
}


void SearchBackend::stockCodeChanged(QString code, QDateTime untilTime, int countOfDays) {
    setCurrentCode(code);
}


void SearchBackend::setSimulationRunning(bool r) {
    qWarning() << "setSimulationRunning: org " << m_simulationRunning << "\t value : " << r;
    if (m_simulationRunning ^ r) {
        qWarning() << "changed";
        m_simulationRunning = r;
        emit simulationRunningChanged();
    }
}


void SearchBackend::setSimulationStatus(bool status) {
    qWarning() << "setSimulationStatus : " << status;
    setSimulationRunning(status);
}


void SearchBackend::startSimulation(const QDateTime &dt) {
    qWarning() << "startSimulation : " << dt;
    DataProvider::getInstance()->startSimulation(dt);
}


void SearchBackend::stopSimulation() {
    qWarning() << "stopSimulation";
    DataProvider::getInstance()->stopSimulation();
}


void SearchBackend::setServerDateTime(const QDateTime &dt) {
    if (m_serverDateTime.toMSecsSinceEpoch() != dt.toMSecsSinceEpoch()) {
        m_serverDateTime = dt;
        emit serverDateTimeChanged();
    }
}


void SearchBackend::setSimulationSpeed(qreal s) {
    if ( m_simulationSpeed != s) {
        m_simulationSpeed = s;
        emit simulationSpeedChanged();
    }
}


void SearchBackend::setCurrentCode(const QString &code) {
    qWarning() << "setCurrentCode : " << code;
    if (m_currentCode != code) {
        m_currentCode = code;
        emit currentCodeChanged();
    }
}


void SearchBackend::setCurrentDateTime(const QDateTime &dt) {
    if (m_currentDateTime.toMSecsSinceEpoch() != dt.toMSecsSinceEpoch()) {
        m_currentDateTime = dt;
        emit currentDateTimeChanged();
    }
}


void SearchBackend::setDays(int d) {
    if (m_days != d) {
        m_days = d;
        emit daysChanged();
    }
}


void SearchBackend::sendCurrent(const QString &code, const QDateTime &dt, int countOfDays) {
    qWarning() << "sendCurrent : " << code << "\t" << dt << "\t" << countOfDays;
    DataProvider::getInstance()->setCurrentStock(code, dt, countOfDays);
}


void SearchBackend::launchTick() {
    QProcess *process = new QProcess;
    connect(process, &QProcess::started, process, &QProcess::deleteLater);
    QString dir = "/home/nnnlife/workspace/trader/application/qml_today";
    bool ret = process->startDetached(dir + "/qml_today", QStringList(), dir);
}


void SearchBackend::launchVolumeGraph() {
    QProcess *process = new QProcess;
    connect(process, &QProcess::started, process, &QProcess::deleteLater);
    QString dir = "/home/nnnlife/workspace/trader/application/qml_comparison";
    bool ret = process->startDetached(dir + "/qml_comparison", QStringList(), dir);
}


void SearchBackend::launchBidAsk() {
    QProcess *process = new QProcess;
    connect(process, &QProcess::started, process, &QProcess::deleteLater);
    QString dir = "/home/nnnlife/workspace/trader/application/qml_bidask";
    bool ret = process->startDetached(dir + "/morning_bidask", QStringList(), dir);

}


void SearchBackend::launchDayChart() {
    QProcess *process = new QProcess;
    connect(process, &QProcess::started, process, &QProcess::deleteLater);
    QString dir = "/home/nnnlife/workspace/trader/application/qml_dayquery";
    bool ret = process->startDetached(dir + "/morning_dayview", QStringList(), dir);
}
