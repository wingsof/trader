#include "YtopAmountListModel.h"
#include "StockStat.h"


YtopAmountListModel::YtopAmountListModel(QObject *parent)
: AbstractListModel(parent) {}


QStringList YtopAmountListModel::getServerList() {
    QStringList yt = StockStat::instance()->getYtopAmountList();
    QStringList display;
    for (int i = 0; i < 20; i++)  {
        if (i > yt.count() - 1)
            break;
        display.append(yt.at(i));
    }
    return display;
}


void YtopAmountListModel::menuClicked(int index) {
    Q_UNUSED(index);
}
