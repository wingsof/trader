#ifndef SEARCH_BACKEND_H_
#define SEARCH_BACKEND_H_


#include <QObject>
#include <qqml.h>
#include "DataProvider.h"


class SearchBackend : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString currentCode READ currentCode WRITE setCurrentCode NOTIFY currentCodeChanged)
    Q_PROPERTY(QDateTime currentDateTime READ currentDateTime WRITE setCurrentDateTime NOTIFY currentDateTimeChanged)
    Q_PROPERTY(QDateTime serverDateTime READ serverDateTime WRITE setServerDateTime NOTIFY serverDateTimeChanged)
    Q_PROPERTY(int days READ days WRITE setDays NOTIFY daysChanged)
    Q_PROPERTY(bool simulationRunning READ simulationRunning WRITE setSimulationRunning NOTIFY simulationRunningChanged)
    Q_PROPERTY(qreal simulationSpeed READ simulationSpeed WRITE setSimulationSpeed NOTIFY simulationSpeedChanged)
    QML_ELEMENT
    QML_SINGLETON

public:
    explicit SearchBackend(QObject *parent = nullptr);

    QString currentCode();
    QDateTime currentDateTime();
    QDateTime serverDateTime();
    int days();
    bool simulationRunning();
    qreal simulationSpeed();

    void setCurrentCode(const QString &code);
    void setCurrentDateTime(const QDateTime &dt);
    void setSimulationRunning(bool r);
    void setServerDateTime(const QDateTime &dt);
    void setDays(int d);
    void setSimulationSpeed(qreal s);

    Q_INVOKABLE void sendCurrent(const QString &code, const QDateTime &dt, int countOfDays);
    Q_INVOKABLE void launchTick();
    Q_INVOKABLE void launchVolumeGraph();
    Q_INVOKABLE void launchBidAsk();
    Q_INVOKABLE void launchDayChart();
    Q_INVOKABLE void launchFavorite();

    Q_INVOKABLE void startSimulation(const QDateTime &dt);
    Q_INVOKABLE void stopSimulation();

private:
    QString m_currentCode;
    QDateTime m_currentDateTime;
    QDateTime m_serverDateTime;
    int m_days;
    bool m_simulationRunning;
    qreal m_simulationSpeed;

    bool launchApp(const QString &path, const QString &name);

private slots:
    void stockCodeChanged(QString code, QDateTime untilTime, int countOfDays);
    void timeInfoArrived(QDateTime dt);
    void setSimulationStatus(bool status);

signals:
    void currentCodeChanged();
    void currentDateTimeChanged();
    void daysChanged();
    void simulationRunningChanged();
    void simulationSpeedChanged();
    void serverDateTimeChanged();
};


#endif
