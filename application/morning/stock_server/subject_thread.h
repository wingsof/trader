#ifndef _SUBJECT_THREAD_H_
#define _SUBJECT_THREAD_H_


#include <QThread>
#include <iostream>
#include "stock_provider.grpc.pb.h"

using stock_api::CybosSubjectTickData;

class SubjectThread : public QThread {
Q_OBJECT
public:
    SubjectThread(std::shared_ptr<stock_api::Stock::Stub> stub);

protected:
    void run();

private:
    std::string code;
    std::shared_ptr<stock_api::Stock::Stub> stub_;

signals:
    void tickArrived(CybosSubjectTickData *);
};


#endif
