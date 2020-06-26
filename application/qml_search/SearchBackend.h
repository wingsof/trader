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
    Q_PROPERTY(int days READ days WRITE setDays NOTIFY daysChanged)
    Q_PROPERTY(bool simulationRunning READ simulationRunning WRITE setSimulationRunning NOTIFY simulationRunningChanged)
    QML_ELEMENT
    QML_SINGLETON

public:
    explicit SearchBackend(QObject *parent = nullptr);

    QString currentCode();
    QDateTime currentDateTime();
    int days();
    bool simulationRunning();

    void setCurrentCode(const QString &code);
    void setCurrentDateTime(const QDateTime &dt);
    void setSimulationRunning(bool r);
    void setDays(int d);

    Q_INVOKABLE void sendCurrent(const QString &code, const QDateTime &dt, int countOfDays);
    Q_INVOKABLE void launchTick();
    Q_INVOKABLE void launchVolumeGraph();
    Q_INVOKABLE void launchBidAsk();
    Q_INVOKABLE void launchDayChart();

private:
    QString m_currentCode;
    QDateTime m_currentDateTime;
    int m_days;
    bool m_simulationRunning;

private slots:
    void stockCodeChanged(QString code, QDateTime untilTime, int countOfDays);

signals:
    void currentCodeChanged();
    void currentDateTimeChanged();
    void daysChanged();
    void simulationRunningChanged();
};


#endif
