#ifndef MORNING_TIMER_H_
#define MORNING_TIMER_H_


#include <QObject>
#include <QTimer>
#include <QDateTime>


class MorningTimer : public QObject {
Q_OBJECT
public:
    MorningTimer(int _interval, QObject *p=0);
    ~MorningTimer();
    void start();

private:
    QTimer *timer;
    int interval;
    QDateTime lastProcessedTime;

private slots:
    void processTimeout();

signals:
    void timeout();

};


#endif
