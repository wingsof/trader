#ifndef TIME_INFO_H_
#define TIME_INFO_H_

#include <QObject>
#include <QTimer>
#include <QDateTime>
#include <google/protobuf/timestamp.pb.h>
using google::protobuf::Timestamp;

class TimeInfo : public QObject {
Q_OBJECT
public:
    TimeInfo();

    static TimeInfo & getInstance() {
        static TimeInfo timeInfo;
        return timeInfo;
    }

    void setSimulationTime(Timestamp *);

public slots:
    void timeInfoArrived(Timestamp *);

private slots:
    void sendTimeInfo();

private:
    QTimer * timer;
    QDateTime currentDateTime;
    bool isSimulation;

public:
    QDateTime getCurrentDateTime();

signals:
    void timeChanged(QDateTime);
};

#endif
