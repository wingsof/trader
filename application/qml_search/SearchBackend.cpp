#include "SearchBackend.h"
#include <QDebug>
#include <QProcess>
#include <QStringList>


SearchBackend::SearchBackend(QObject *parent)
: QObject(parent) {
    m_currentCode = "";
    m_currentDateTime = QDateTime::currentDateTime();
    m_days = 120;

    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged,
            this, &SearchBackend::stockCodeChanged);
    DataProvider::getInstance()->startStockCodeListening();
    m_simulationRunning = false; // read from server whether currently running
    qWarning() << "SearchBackend";
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


bool SearchBackend::simulationRunning() {
    return m_simulationRunning;
}


void SearchBackend::stockCodeChanged(QString code, QDateTime untilTime, int countOfDays) {
    setCurrentCode(code);
}


void SearchBackend::setSimulationRunning(bool r) {

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
    QString dir = "/home/nnnlife/workspace/trader/application/qml_tick";
    bool ret = process->startDetached(dir + "/morning_tick", QStringList(), dir);

}


void SearchBackend::launchDayChart() {
    QProcess *process = new QProcess;
    connect(process, &QProcess::started, process, &QProcess::deleteLater);
    QString dir = "/home/nnnlife/workspace/trader/application/qml_dayquery";
    bool ret = process->startDetached(dir + "/morning_dayview", QStringList(), dir);
}
