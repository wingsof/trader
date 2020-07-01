#include "DataProvider.h"
#include <grpc/grpc.h>
#include <grpcpp/channel.h>
#include <grpcpp/client_context.h>
#include <grpcpp/create_channel.h>
#include <grpcpp/security/credentials.h>
#include <google/protobuf/util/time_util.h>
#include "TickThread.h"
#include "TimeThread.h"
#include "BidAskThread.h"
#include "StockSelectionThread.h"
#include "SpeedStatistics.h"
#include "MinuteData.h"
#include "DayDataProvider.h"
#include "SimulationEvent.h"
#include "RunSimulation.h"


using grpc::Channel;
using grpc::ClientContext;
using grpc::ClientReader;
using grpc::ClientReaderWriter;
using grpc::ClientWriter;
using grpc::Status;
using google::protobuf::util::TimeUtil;
using google::protobuf::Timestamp;
using google::protobuf::Empty;

using stock_api::Stock;
using stock_api::StockCodeQuery;
using stock_api::StockQuery;
using stock_api::CybosDayData;
using stock_api::CodeList;
using stock_api::SimulationArgument;

using grpc::ClientContext;
using stock_api::StockQuery;

using stock_api::CybosTickData;
using stock_api::CybosDayDatas;
using stock_api::CybosBidAskTickData;
using stock_api::CybosSubjectTickData;
using google::protobuf::Timestamp;
using stock_api::SimulationStatus;


DataProvider::DataProvider()
: QObject(0) {
    //setenv("TZ", "UTC", 1);
    qRegisterMetaType<CybosTickData>("CybosTickData");
    qRegisterMetaType<CybosDayDatas>("CybosDayDatas");
    qRegisterMetaType<CybosBidAskTickData>("CybosBidAskTickData");
    qRegisterMetaType<CybosSubjectTickData>("CybosSubjectTickData");
    qRegisterMetaType<SimulationStatus>("SimulationStatus");
    qRegisterMetaType<Timestamp>("Timestamp");

    stub_ = Stock::NewStub(grpc::CreateChannel("localhost:50052", grpc::InsecureChannelCredentials()));

    speedStatistics = NULL;
    minuteData = NULL;
    timeThread = NULL;

    tickThread = new TickThread(stub_);
    bidAskThread = new BidAskThread(stub_);
    stockSelectionThread = new StockSelectionThread(stub_);
    dayDataProvider = new DayDataProvider(stub_);
    SimulationEvent *simulationEvent = new SimulationEvent(stub_);
    m_simulationStatus = _isSimulation() ? RUNNING: STOP;

    connect(tickThread, &TickThread::tickArrived, this, &DataProvider::tickArrived);
    connect(bidAskThread, &BidAskThread::tickArrived, this, &DataProvider::bidAskTickArrived);
    connect(stockSelectionThread, &StockSelectionThread::stockCodeChanged, this, &DataProvider::stockCodeReceived);
    connect(dayDataProvider, &DayDataProvider::dataReady, this, &DataProvider::dayDataReady);
    connect(dayDataProvider, &DayDataProvider::minuteDataReady, this, &DataProvider::minuteDataReady);
    connect(simulationEvent, &SimulationEvent::simulationStatusChanged, this, &DataProvider::setSimulationStatus);

    simulationEvent->start();
}


void DataProvider::stockCodeReceived(QString code, QDateTime untilTime, int countOfDays) {
    qWarning() << "receive stock code received : " << code << "\t" << untilTime;
    currentStockCode = code;

    if (minuteData != NULL)
        minuteData->setCurrentStockCode(code);

    emit stockCodeChanged(code, untilTime, countOfDays);
}


void DataProvider::createSpeedStatistics(int secs) {
    if (speedStatistics == NULL)
        speedStatistics = new SpeedStatistics(secs, this);
}


void DataProvider::convertTimeInfo(Timestamp *t) {
    long msec = TimeUtil::TimestampToMilliseconds(*t);
    emit timeInfoArrived(QDateTime::fromMSecsSinceEpoch(msec));
}


void DataProvider::startTimeListening() {
    if (timeThread == NULL) {
        timeThread = new TimeThread(stub_);
        connect(timeThread, &TimeThread::timeInfoArrived, this, &DataProvider::convertTimeInfo);
    }
}


void DataProvider::requestDayData(const QString &code, int countOfDays, const QDateTime &_untilTime) {
    dayDataProvider->requestDayData(code, countOfDays, _untilTime);
}


void DataProvider::requestMinuteData(const QString &code, const QDateTime &fromTime, const QDateTime &untilTime) {
    dayDataProvider->requestMinuteData(code, fromTime, untilTime);
}


void DataProvider::collectMinuteData(int min) {
    if (minuteData == NULL) {
        minuteData = new MinuteData(this, stub_, min, currentStockCode, isSimulation());
        connect(tickThread, &TickThread::tickArrived, minuteData, &MinuteData::stockTickArrived);
        connect(minuteData, &MinuteData::minuteTickUpdated, this, &DataProvider::minuteTickUpdated);
    }
}


void DataProvider::startStockTick() {
    tickThread->start();
}


void DataProvider::startBidAskTick() {
    bidAskThread->start();
}


void DataProvider::startStockCodeListening() {
    stockSelectionThread->start();
}


void DataProvider::startSimulation(const QDateTime &dt) {
    if (m_simulationStatus == STOP) {
        RunSimulation * rs = new RunSimulation(dt, stub_);
        connect(rs, &RunSimulation::finished, rs, &RunSimulation::deleteLater);
        rs->start();
        m_simulationStatus = STOP_TO_RUNNING;
    }
}


void DataProvider::stopSimulation() {
    if (m_simulationStatus == RUNNING) {
        _stopSimulation();
    }
}


void DataProvider::setSimulationStatus(SimulationStatus *status) {
    if ( (m_simulationStatus == RUNNING && status->simulation_on()) ||
        (m_simulationStatus == STOP && !status->simulation_on()))
        return;

    if (status->simulation_on())
        m_simulationStatus = RUNNING;
    else
        m_simulationStatus = STOP;

    if (minuteData != NULL) 
        minuteData->setSimulation(status->simulation_on());

    emit simulationStatusChanged(status->simulation_on());
}


bool DataProvider::isSimulation() {
    if (m_simulationStatus == STOP || m_simulationStatus == RUNNING_TO_STOP)
        return false;
    return true;
}


void DataProvider::setCurrentStock(const QString &code, const QDateTime &dt, int countOfDays) {
    stockSelectionThread->setCurrentStock(code, dt, countOfDays);
}


MinuteTick * DataProvider::getMinuteTick(const QString &code) {
    if (minuteData && !code.isEmpty())
        return minuteData->getMinuteTick(code);
    return nullptr;
}


void DataProvider::_stopSimulation() {
    ClientContext context;
    Empty * emptyReturn = new Empty;
    Empty empty;
    stub_->StopSimulation(&context, empty, emptyReturn);

    m_simulationStatus = RUNNING_TO_STOP;
}


bool DataProvider::_isSimulation() {
    ClientContext context;
    SimulationStatus * status = new SimulationStatus;
    Empty empty;
    stub_->GetSimulationStatus(&context, empty, status);
    return status->simulation_on();

}
