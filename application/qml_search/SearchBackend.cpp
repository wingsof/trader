#include "SearchBackend.h"
#include <QDebug>
#include <QProcess>
#include <QStringList>


SearchBackend::SearchBackend(QObject *parent)
: QObject(parent) {
    m_currentCode = "";
    m_currentDateTime = QDateTime::currentDateTime();
    m_serverDateTime = QDateTime::currentDateTime();
    m_simulationSpeed = 1.0;

    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged,
            this, &SearchBackend::stockCodeChanged);
    connect(DataProvider::getInstance(), &DataProvider::timeInfoArrived, this, &SearchBackend::timeInfoArrived);
    connect(DataProvider::getInstance(), &DataProvider::simulationStatusChanged, this, &SearchBackend::setSimulationStatus);
    DataProvider::getInstance()->startStockCodeListening();
    m_simulationRunning = DataProvider::getInstance()->isSimulation();
    //qWarning() << "SearchBackend";
}


void SearchBackend::timeInfoArrived(QDateTime dt) {
    //qWarning() << "SearchBackend>\t" << "timeInfoArrived : " << dt;
    setServerDateTime(dt);
}


QString SearchBackend::currentCode() {
    return m_currentCode;
}


QDateTime SearchBackend::currentDateTime() {
    return m_currentDateTime; 
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


void SearchBackend::stockCodeChanged(QString code) {
    setCurrentCode(code);
}


void SearchBackend::setSimulationRunning(bool r) {
    qWarning() << "setSimulationRunning: org " << m_simulationRunning << "\t value : " << r;
    if (m_simulationRunning ^ r) {
        m_simulationRunning = r;
        emit simulationRunningChanged();
    }
}


void SearchBackend::setSimulationStatus(bool status) {
    qWarning() << "setSimulationStatus : " << status;
    setSimulationRunning(status);
}


void SearchBackend::startSimulation() {
    qWarning() << "startSimulation";
    DataProvider::getInstance()->startSimulation();
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
    if (m_simulationRunning &&  m_simulationSpeed != s) {
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


void SearchBackend::sendCurrentStock(const QString &code) {
    DataProvider::getInstance()->setCurrentStock(code);
}


void SearchBackend::sendCurrentDateTime(const QDateTime &dt) {
    DataProvider::getInstance()->setCurrentDateTime(dt);
}


bool SearchBackend::launchApp(const QString &path, const QString &name) {
    QProcess *process = new QProcess;
    connect(process, &QProcess::started, process, &QProcess::deleteLater);
    QString dir = qgetenv("MORNING_PATH") + path;
    bool ret = process->startDetached(dir + "/" + name, QStringList(), dir);
    return ret;
}


void SearchBackend::launchTick() {
    launchApp("/application/qml_today", "qml_today");
}


void SearchBackend::launchTrader() {
    launchApp("/application/qml_trading", "qml_trading");
}


void SearchBackend::launchBidAsk() {
    launchApp("/application/qml_bidask", "morning_bidask");
}


void SearchBackend::launchDayChart() {
    launchApp("/application/qml_dayquery", "morning_dayview");
}


void SearchBackend::launchFavorite() {
    launchApp("/application/qml_favorite", "qml_favorite");
}


void SearchBackend::startSubscribeCodes() {
    QStringList subscribeCodes = DataProvider::getInstance()->getSubscribeCodes();
    qWarning() << "Subscrbie Code count : " << subscribeCodes.size();
    for (int i = 0; i < subscribeCodes.size(); i++) {
        DataProvider::getInstance()->requestTickSubscribe(subscribeCodes.at(i));
        if (subscribeCodes.at(i).startsWith("A")) {
            DataProvider::getInstance()->requestBidAskSubscribe(subscribeCodes.at(i));
            DataProvider::getInstance()->requestSubjectSubscribe(subscribeCodes.at(i));
        }
    }
    DataProvider::getInstance()->requestAlarmSubscribe();
}
