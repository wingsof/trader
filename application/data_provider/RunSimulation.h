#ifndef _RUN_SIMULATION_H_
#define _RUN_SIMULATION_H_


#include <QThread>
#include <QDateTime>
#include <iostream>
#include "stock_provider.grpc.pb.h"

using stock_api::SimulationArgument;

class RunSimulation : public QThread {
Q_OBJECT
public:
    RunSimulation(const QDateTime &dt, std::shared_ptr<stock_api::Stock::Stub> stub);

protected:
    void run();

private:
    std::shared_ptr<stock_api::Stock::Stub> stub_;
    QDateTime simulationStartTime;
};


#endif
