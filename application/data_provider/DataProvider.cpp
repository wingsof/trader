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
#include "AlarmThread.h"
#include "StockListThread.h"
#include "StockSelectionThread.h"
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
using stock_api::CompanyName;

using grpc::ClientContext;
using stock_api::StockQuery;

using stock_api::CybosTickData;
using stock_api::CybosDayDatas;
using stock_api::CybosBidAskTickData;
using stock_api::CybosSubjectTickData;
using google::protobuf::Timestamp;
using stock_api::SimulationStatus;
using stock_api::Option;


DataProvider::DataProvider()
: QObject(0) {
    qRegisterMetaType<CybosTickData>("CybosTickData");
    qRegisterMetaType<CybosDayDatas>("CybosDayDatas");
    qRegisterMetaType<CybosBidAskTickData>("CybosBidAskTickData");
    qRegisterMetaType<CybosSubjectTickData>("CybosSubjectTickData");
    qRegisterMetaType<SimulationStatus>("SimulationStatus");
    qRegisterMetaType<Timestamp>("Timestamp");
    qRegisterMetaType<CybosStockAlarm>("CybosStockAlarm");

    stub_ = Stock::NewStub(grpc::CreateChannel("localhost:50052", grpc::InsecureChannelCredentials()));

    minuteData = NULL;
    timeThread = NULL;
    alarmThread = NULL;
    stockListThread = NULL;

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
    startTimeListening();
}


void DataProvider::stockCodeReceived(QString code) {
    qWarning() << "receive stock code received : " << code;
    currentStockCode = code;

    if (minuteData != NULL)
        minuteData->setCurrentStockCode(code);

    emit stockCodeChanged(code);
}


void DataProvider::forceChangeStockCode(const QString &code) {
    stockCodeReceived(code);
}


void DataProvider::setCurrentDateTime(const QDateTime &dt) {
    _setCurrentDateTime(dt); 
}


void DataProvider::convertTimeInfo(Timestamp *t) {
    long msec = TimeUtil::TimestampToMilliseconds(*t);
    //qWarning() << "time arrived : " << QDateTime::fromMSecsSinceEpoch(msec);
    m_currentDateTime = QDateTime::fromMSecsSinceEpoch(msec);
    emit timeInfoArrived(m_currentDateTime);
}


void DataProvider::startTimeListening() {
    if (timeThread == NULL) {
        timeThread = new TimeThread(stub_);
        connect(timeThread, &TimeThread::timeInfoArrived, this, &DataProvider::convertTimeInfo);
        timeThread->start();
    }
}


void DataProvider::startAlarmListening() {
    if (alarmThread == NULL) {
        alarmThread = new AlarmThread(stub_);
        connect(alarmThread, &AlarmThread::alarmArrived, this, &DataProvider::alarmArrived);
        alarmThread->start();
    }
}


void DataProvider::startListTypeListening() {
    if (stockListThread == NULL) {
        stockListThread = new StockListThread(stub_);
        connect(stockListThread, &StockListThread::stockListChanged, this, &DataProvider::stockListTypeChanged);
        stockListThread->start();
    }
}


void DataProvider::requestDayData(const QString &code, int countOfDays, const QDateTime &_untilTime) {
    // TODO: Cache
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
        connect(this, &DataProvider::timeInfoArrived, minuteData, &MinuteData::timeInfoArrived);
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


void DataProvider::startSimulation() {
    if (m_simulationStatus == STOP) {
        RunSimulation * rs = new RunSimulation(stub_);
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


void DataProvider::setCurrentStock(const QString &code) {
    _setCurrentStock(code);
}


QString DataProvider::getCompanyName(const QString &code) {
    ClientContext context;
    CompanyName* cn = new CompanyName;
    StockCodeQuery scq;
    scq.set_code(code.toStdString());
    stub_->GetCompanyName(&context, scq, cn);
    return QString::fromStdString(cn->company_name());
}


MinuteTick * DataProvider::getMinuteTick(const QString &code) {
    if (minuteData && !code.isEmpty())
        return minuteData->getMinuteTick(code, currentDateTime());
    return nullptr;
}


QStringList DataProvider::getRecentSearch() {
    ClientContext context;
    CodeList * codeList = new CodeList;
    Empty empty;
    stub_->GetRecentSearch(&context, empty, codeList);
    QStringList list;
    for (int i = 0; i < codeList->codelist_size(); i++)
        list.append(QString::fromStdString(codeList->codelist(i)));
    return list;
}


QStringList DataProvider::getFavoriteList() {
    ClientContext context;
    CodeList * codeList = new CodeList;
    Empty empty;
    stub_->GetFavoriteList(&context, empty, codeList);
    QStringList list;
    for (int i = 0; i < codeList->codelist_size(); i++)
        list.append(QString::fromStdString(codeList->codelist(i)));
    return list;
}


QStringList DataProvider::getViList(int option, bool catchPlus) {
    ClientContext context;
    CodeList * codeList = new CodeList;
    Option opt;
    opt.set_type(option);
    opt.set_catch_plus(catchPlus);
    stub_->GetViList(&context, opt, codeList);
    QStringList list;
    for (int i = 0; i < codeList->codelist_size(); i++)
        list.append(QString::fromStdString(codeList->codelist(i)));
    return list;
}


QStringList DataProvider::getTtopAmountList(int option, bool catchPlus, bool useAccumulated) {
    ClientContext context;
    CodeList * codeList = new CodeList;
    Option opt;
    opt.set_type(option);
    opt.set_catch_plus(catchPlus);
    opt.set_use_accumulated(useAccumulated);
    stub_->GetTodayTopAmountList(&context, opt, codeList);
    QStringList list;
    for (int i = 0; i < codeList->codelist_size(); i++)
        list.append(QString::fromStdString(codeList->codelist(i)));
    return list;
}


TopList * DataProvider::getYtopAmountList() {
    ClientContext context;
    Timestamp ts = Timestamp(TimeUtil::TimeTToTimestamp(m_currentDateTime.toTime_t()));
    TopList * topList = new TopList;
    stub_->GetYesterdayTopAmountList(&context, ts, topList);
    qWarning() << "topList count : " << topList->codelist_size() << "\tdate" << topList->date() << "\tis_today_data" << topList->is_today_data();
    return topList;
}


void DataProvider::addToFavorite(const QString &code) {
    qWarning() << "DataProvider addToFavorite : " << code;
    ClientContext context;
    StockCodeQuery data; 
    data.set_code(code.toStdString());
    Empty empty;
    stub_->AddFavorite(&context, data, &empty);
}


void DataProvider::removeFromFavorite(const QString &code) {
    ClientContext context;
    StockCodeQuery data; 
    data.set_code(code.toStdString());
    Empty empty;
    stub_->RemoveFavorite(&context, data, &empty);
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


void DataProvider::_setCurrentStock(const QString &code) {
    ClientContext context;
    StockCodeQuery data;
    Empty empty;
    data.set_code(code.toStdString());
    stub_->SetCurrentStock(&context, data, &empty);
}


void DataProvider::_setCurrentDateTime(const QDateTime &dt) {
    ClientContext context;
    Timestamp data = Timestamp(TimeUtil::TimeTToTimestamp(dt.toTime_t()));
    Empty empty;
    stub_->SetCurrentDateTime(&context, data, &empty);

}
