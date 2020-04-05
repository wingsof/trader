#include "stockmodel.h"
#include <QDebug>


/*
    StockModel provides various stock model to UI for interaction
    when UI send start signal(simulation or real)
    prepare stock object after reading code list
*/


StockModel::StockModel()
: QObject(0), provider(DataProvider::getInstance()) {
    //QStringList codes = provider->requestYesterdayTopAmount();
    //qWarning() << "code list " << codes;
}


StockModel::~StockModel() {}


void StockModel::startSimulation(const QDate &e) {

}
