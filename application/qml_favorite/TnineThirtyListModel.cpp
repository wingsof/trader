#include "TnineThirtyListModel.h"
#include "StockStat.h"


TnineThirtyListModel::TnineThirtyListModel(QObject *parent)
: AbstractListModel(parent) {
}


QStringList TnineThirtyListModel::getServerList() {
    return StockStat::instance()->getTnineThirtyList();
}


void TnineThirtyListModel::menuClicked(int index) {
    Q_UNUSED(index);
}
