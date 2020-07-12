#include "TtopAmountListModel.h"
#include "StockStat.h"
#include <QDebug>


TtopAmountListModel::TtopAmountListModel(QObject *parent)
: AbstractListModel(parent) {
    mAccumulatedPeriod = false;
    mCatchPlus = true;
    qWarning() << "Constructor";
}


QStringList TtopAmountListModel::getServerList() {
    QStringList result = StockStat::instance()->getTtopAmountList(60, catchPlus(), accumulatedPeriod());
    qWarning() << "TtopAmountListModel getServerList return " << result.count();    
    return result;
}


void TtopAmountListModel::setCatchPlus(bool c) {
    if (mCatchPlus ^ c) {
        mCatchPlus = c;
        emit catchPlusChanged();
        refreshList();
    }
}


void TtopAmountListModel::setAccumulatedPeriod(bool a) {
    if (mAccumulatedPeriod ^ a) {
        mAccumulatedPeriod = a;
        emit accumulatedPeriodChanged();
        refreshList();
    }
}


void TtopAmountListModel::menuClicked(int index) {
    if (index == 0) {
        if (currentSelectIndex() >= itemList.count() || currentSelectIndex() == -1)
            return;

        const ListItem * li = itemList.at(currentSelectIndex());
        StockStat::instance()->addToFavorite(li->code());
    }
}


void TtopAmountListModel::checkStateChanged(int index, bool state) {
    if (index == 0)
        setAccumulatedPeriod(state); 
    else if (index == 1)
        setCatchPlus(state);
}
