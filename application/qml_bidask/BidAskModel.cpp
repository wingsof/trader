#include "BidAskModel.h"
#include <google/protobuf/util/time_util.h>
#include <QDebug>

using google::protobuf::util::TimeUtil;
using stock_api::OrderMsg;
using stock_api::OrderMethod;

#define VOLUME_DIFF_ROLE    (Qt::UserRole + 1)

BidAskModel::BidAskModel(QObject *parent)
: QAbstractTableModel(parent) {
    connect(DataProvider::getInstance(), &DataProvider::tickArrived,
            this, &BidAskModel::tickArrived);
    connect(DataProvider::getInstance(), &DataProvider::bidAskTickArrived,
            this, &BidAskModel::bidAskTickArrived);
    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged,
            this, &BidAskModel::setCurrentStock);
    connect(DataProvider::getInstance(), &DataProvider::timeInfoArrived, this, &BidAskModel::timeInfoArrived);

    DataProvider::getInstance()->startStockTick();
    DataProvider::getInstance()->startBidAskTick();
    DataProvider::getInstance()->startStockCodeListening();
    resetData();
}


BidAskModel::~BidAskModel() {}


void BidAskModel::timeInfoArrived(QDateTime dt) {
    if (!currentDateTime.isValid() || (!DataProvider::getInstance()->isSimulation() && currentDateTime != dt)) {
        currentDateTime = dt;
        resetData();
    }
}


void BidAskModel::resetData() {
    mData.resetData();

    setTotalBidRemain(0);
    setTotalAskRemain(0);
    setYesterdayClose(0);
    setHighlight(-1);
}


void BidAskModel::setTotalBidRemain(uint br) {
    if (br != totalBidRemain) {
        totalBidRemain = br;
        emit totalBidRemainChanged();
    }
}


void BidAskModel::setTotalAskRemain(uint br) {
    if (br != totalAskRemain) {
        totalAskRemain = br;
        emit totalAskRemainChanged();
    }
}


void BidAskModel::setCurrentStock(QString code) {
    if (currentStockCode != code) {
        resetData();
        currentStockCode = code;
        qWarning() << "currentStock: " << currentStockCode;
    }
}


void BidAskModel::setYesterdayClose(int yc) {
    if (yesterdayClose != yc) {
        yesterdayClose = yc;
        emit yesterdayCloseChanged();
    }
}


void BidAskModel::sell_immediately(int percentage) {
    if (mData.getCurrentPrice() > 0) {
        //DataProvider::getInstance()->sell(currentStockCode, mData.getCurrentPrice(), 0, percentage, OrderMsg::TRADE_IMMEDIATELY);
        qWarning() << "SELL IMMEDIATE ";
    }
}


void BidAskModel::buy_immediately(int percentage) {
    if (mData.getCurrentPrice() > 0) {
        DataProvider::getInstance()->buy(currentStockCode, mData.getCurrentPrice(), 0, percentage, OrderMethod::TRADE_IMMEDIATELY);
        qWarning() << "BUY IMMEDIATE";
    }
}


QVariant BidAskModel::data(const QModelIndex &index, int role) const
{
    if (index.column() >= BidAskModel::ASK_DIFF_COLUMN &&
                index.column() <= BidAskModel::BID_DIFF_COLUMN &&
                index.row() >= BidAskModel::START_ROW && index.row() <= BidAskModel::STEPS * 2) {

        if (index.column() == BidAskModel::PRICE_COLUMN) {
            int price = mData.getPriceByRow(index.row() - 1);
            if (price != 0)
                return QVariant(price);
        }
        else if ((index.column() == BidAskModel::ASK_REMAIN_COLUMN && index.row() >= START_ROW && index.row () <= START_ROW + 9) || 
                (index.column() == BidAskModel::BID_REMAIN_COLUMN && index.row() >= START_ROW + 10 && index.row() <= START_ROW + 19)) {
            if (role == Qt::DisplayRole) {
                int remain = mData.getRemainByRow(index.row() - 1);
                if (remain != 0)
                    return QVariant(remain);
            }
            else if (role == VOLUME_DIFF_ROLE) {
                int diff = mData.getDiffByRow(index.row() - 1);
                if (diff != 0)
                    return QVariant(diff);
            }
        }
        else if (index.row() == highlight && index.column() == BidAskModel::ASK_REMAIN_COLUMN && !mData.getIsCurrentBuy() && mData.getCurrentPrice() != 0) {
            return QVariant(mData.getCurrentVolume());
        }
        else if (index.row() == highlight && index.column() == BidAskModel::BID_REMAIN_COLUMN && mData.getIsCurrentBuy() && mData.getCurrentPrice() != 0) {
            return QVariant(mData.getCurrentVolume());
        }
    }
    return QVariant(QString());
}


void BidAskModel::tickArrived(CybosTickData *data) {
    if (currentStockCode != QString::fromStdString(data->code()))
        return;

    //long msec = TimeUtil::TimestampToMilliseconds(data->tick_date());
    //qWarning() << QDateTime::fromMSecsSinceEpoch(msec) << "\tcurrent: " << data->current_price() << ", volume: " << data->volume() << "\tBUY:" << data->buy_or_sell() << "\task: " << data->ask_price() << ", bid: " << data->bid_price();
    setYesterdayClose(data->current_price() - data->yesterday_diff());
    setHighlightPosition(data->current_price());
    mData.setTick(data);
    dataChanged(createIndex(1, 2), createIndex(20, 4));
}


void BidAskModel::setHighlightPosition(int price) {
    int index = mData.getRowByPrice(price);
    setHighlight(index >= 0?index+1:index);
}


void BidAskModel::bidAskTickArrived(CybosBidAskTickData *data) {
    if (currentStockCode != QString::fromStdString(data->code()))
        return;

    mData.setBidAskTick(data);
    setTotalAskRemain(data->total_ask_remain());
    setTotalBidRemain(data->total_bid_remain()); 
    //setHighlight(-1);
    dataChanged(createIndex(1, 2), createIndex(20, 4));
    //long msec = TimeUtil::TimestampToMilliseconds(data->tick_date());
    //qWarning() << QDateTime::fromMSecsSinceEpoch(msec) << "\tASK: " << data->ask_prices(0) << "(" << data->ask_remains(0) << ")\t" << "BID: " << data->bid_prices(0) << "(" << data->bid_remains(0) << ")";
}


void BidAskModel::setHighlight(int row) {
    //qWarning() << "setHighlight: " << highlight << " to " << row;
    if (highlight != row) {
        highlight = row;
        emit highlightChanged();
    }
}
