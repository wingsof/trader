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

private slots:
    void timeInfoArrived(Timestamp *);
    void sendTimeInfo();

private:
    QTimer * timer;
    QDateTime currentDateTime;

signals:
    void timeChanged(QDateTime);
};

#endif
