#include "RecentListModel.h"
#include "StockStat.h"


#define CODE_ROLE       Qt::UserRole
#define YPROFIT_ROLE    (Qt::UserRole + 1)
#define TPROFIT_ROLE    (Qt::UserRole + 2)
#define YAMOUNT_ROLE    (Qt::UserRole + 3)
#define TAMOUNT_ROLE    (Qt::UserRole + 4)


RecentListModel::RecentListModel(QObject *parent)
: QAbstractListModel(parent) {
    connect(StockStat::instance(), &StockStat::stockCodeChanged, this, &RecentListModel::stockCodeChanged);
    connect(StockStat::instance(), &StockStat::stockListTypeChanged, this, &RecentListModel::stockListTypeChanged);
    connect(StockStat::instance(), &StockStat::infoUpdated, this, &RecentListModel::infoUpdated);
}


void RecentListModel::clearList() {
    if (recentList.count() == 0)
        return;

    beginResetModel();
    QMutableListIterator<RecentCode *> i(recentList);
    while (i.hasNext()) {
        RecentCode *rc = i.next();
        i.remove();
        delete rc;
    }
    endResetModel();
    qWarning() << "clear list list count : " << recentList.count();
}


void RecentListModel::refreshList() {
    if (!today.isValid())
        return;

    QStringList rcl = StockStat::instance()->getRecentSearch();

    if ( (rcl.count() < recentList.count()) || rcl.count() == 0) {
        qWarning() << "clear";
        clearList();
    }

    qWarning() << "Recent Search Result : " << rcl << "\tlist count : " << recentList.count();
    int listEndIndex = recentList.count() - 1;
    int rclEndIndex = rcl.count() - 1;
    while (listEndIndex >= 0 && rclEndIndex >= 0) {
        if (rcl.at(rclEndIndex) != recentList.at(listEndIndex)->code()) {
            clearList();
            break;
        }
        listEndIndex--;
        rclEndIndex--;
    }

    for (int i = rcl.count() - recentList.count() - 1; i >= 0; i--) {
        beginInsertRows(QModelIndex(), 0, 0);
        recentList.prepend(new RecentCode(rcl.at(i), today));
        endInsertRows();
    }
}


void RecentListModel::stockCodeChanged(QString code, QDateTime untilTime, int countOfDays) {
    Q_UNUSED(code);
    Q_UNUSED(countOfDays);
    qWarning() << "stockCodeChanged : " << untilTime;
    if (today.toMSecsSinceEpoch() != untilTime.toMSecsSinceEpoch()) {
        qWarning() << "time different";
        today = untilTime;
        refreshList();
    }
}


void RecentListModel::stockListTypeChanged(QString type) {
    qWarning() << "stockListTypeChanged : " << type;
    if (type == "recent") {
        refreshList();
    }
}


int RecentListModel::rowCount(const QModelIndex &parent) const {
    //qWarning() << parent << "rowCount : " << recentList.count();
    return recentList.count();
}


QString RecentListModel::uint64ToString(uint64_t amount) const {
    if (amount >= 1000000000) {
        qreal f = amount / 1000000000.0;
        return QString::number(f, 'f', 1) + " B";
    }
    else if (amount >= 1000000) {
        qreal f = amount / 1000000.0;
        return QString::number(f, 'f', 1) + " M";
    }
    else if (amount >= 1000) {
        qreal f = amount / 1000.0;
        return QString::number(f, 'f', 1) + " K";
    }

    return QString::number((uint)amount);
}


QVariant RecentListModel::data(const QModelIndex &index, int role) const {
    //qWarning() << "data\t" << index << "\trole: " << role;
    const RecentCode * rc = recentList.at(index.row());
    if (role == Qt::DisplayRole)
        return rc->name();
    else if (role == CODE_ROLE)
        return rc->code();
    else if (role == TPROFIT_ROLE)
        return QVariant(rc->todayProfit());
    else if (role == YPROFIT_ROLE)
        return QVariant(rc->yesterdayProfit());
    else if (role == YAMOUNT_ROLE)
        return uint64ToString(rc->yesterdayAmount());
    else if (role == TAMOUNT_ROLE)
        return uint64ToString(rc->todayAmount());

    return "";
}


void RecentListModel::infoUpdated(QString code) {
    for (int i = 0; i < recentList.count(); i++) {
        RecentCode * rc = recentList.at(i);
        if (rc->code() == code) {
            emit dataChanged(createIndex(i, 0), createIndex(i, 0));
            break;
        }
    }
}


void RecentListModel::currentSelectionChanged(int index) {
    if (index >= 0 && index < recentList.count()) {
        RecentCode * rc = recentList.at(index);
        StockStat::instance()->setCurrentCode(rc->code());
    }
}


RecentCode::RecentCode(const QString &_code, const QDateTime &_dt)
: QObject(nullptr), m_code(_code), m_today(_dt){
    m_name = StockStat::instance()->getInfo(m_code)->getName();
}


qreal RecentCode::yesterdayProfit() const {
    StockInfo * info = StockStat::instance()->getInfo(m_code);
    if (info->beforeYesterdayClosePrice() > 0) {
        qreal profit = ((qreal)info->getYesterdayData().close_price() - info->beforeYesterdayClosePrice()) / info->beforeYesterdayClosePrice() * 100.0;
        return profit;
    }
    return 0.0;
}


qreal RecentCode::todayProfit() const {
    StockInfo * info = StockStat::instance()->getInfo(m_code);
    if (info->todayCurrentPrice() > 0) {
        qreal profit = ((qreal)info->todayCurrentPrice() - info->getYesterdayData().close_price()) / info->getYesterdayData().close_price() * 100.0;
        return profit;
    }
    return 0.0;
}


uint64_t RecentCode::yesterdayAmount() const {
    StockInfo * info = StockStat::instance()->getInfo(m_code);
    return info->getYesterdayData().amount();
}


uint64_t RecentCode::todayAmount() const {
    StockInfo * info = StockStat::instance()->getInfo(m_code);
    return info->todayAmount();
}
