#include "BidAskModel.h"
#include <google/protobuf/util/time_util.h>
#include <QDebug>

using google::protobuf::util::TimeUtil;

PriceModel::PriceModel() {
    prices = new int[BidAskModel::STEPS * 2];
    remains = new uint[BidAskModel::STEPS * 2];
    remainDiff = new int[BidAskModel::STEPS * 2];
    for (int i = 0; i < BidAskModel::STEPS * 2; ++i) {
        prices[i] = 0;
        remains[i] = 0;
        remainDiff[i] = 0;
    }
    isBidaskReceived = false;
    currentVolume = 0;
    isBuy = false;
}


int PriceModel::getPrice(int i) {
    return prices[i];
}


uint PriceModel::getRemain(int i, bool isAsk) {
    if (isAsk) {
        if (i < BidAskModel::STEPS)
            return remains[i];
        else if (i == BidAskModel::STEPS && !isBuy)
            return currentVolume;
    }
    else {
        if (i >= BidAskModel::STEPS && i < BidAskModel::STEPS * 2)
            return remains[i];
        else if (i == BidAskModel::STEPS - 1 && isBuy)
            return currentVolume;
    }
    return 0;
}


int PriceModel::getRemainDiff(int i, bool isAsk) {
    if (isAsk && i >= BidAskModel::STEPS)
        return 0;
    else if (!isAsk && (i < BidAskModel::STEPS || i >= BidAskModel::STEPS * 2))
        return 0;

    return remainDiff[i];
}


int PriceModel::getIndexOfPrice(int price) {
    for (int i = 0; i < BidAskModel::STEPS * 2; i++) {
        if (prices[i] == price)
            return i;
    }
    return -1;
}


void PriceModel::setTick(CybosTickData *data) {
    currentVolume = data->volume();
    isBuy = data->buy_or_sell();
    for (int i = 0; i < BidAskModel::STEPS * 2; i++)
        remainDiff[i] = 0;

    if (!isBidaskReceived) {
        qWarning() << "not bidaskReceived: " << data->ask_price() << ", " << data->bid_price();
        prices[BidAskModel::STEPS - 1] = data->ask_price();             
        prices[BidAskModel::STEPS] = data->bid_price();
    }
    else {
        movePrices(data->ask_price(), data->bid_price());
        decreaseVolume(data->current_price(), currentVolume, isBuy);
    }
}

// left is minus, right is plus
void PriceModel::rotatePrices(int count, bool isAsk) {
    int orgPrices[10];
    uint orgRemains[10];
    int memIndex = 0;

    if (!isAsk)
        memIndex = 10;

    memcpy((void *)orgPrices, (void *)(prices + memIndex), sizeof(int) * 10);
    memcpy((void *)orgRemains, (void *)(remains + memIndex), sizeof(uint) * 10);

    if (count > 0) {
        memcpy((void *)(prices + memIndex + count), (void *)orgPrices, sizeof(int) * (10 - count));
        memcpy((void *)(remains + memIndex + count), (void *)orgRemains, sizeof(uint) * (10 - count));

        for (int i = memIndex; i < memIndex + count; i++) {
            prices[i] = 0;
            remains[i] = 0;
        }
    }
    else if (count < 0) {
        memcpy((void *)(prices + memIndex), (void *)(orgPrices - count), sizeof(int) * (10 + count));
        memcpy((void *)(remains + memIndex), (void *)(orgRemains - count), sizeof(uint) * (10 + count));

        for (int i = BidAskModel::STEPS + memIndex + count; i < BidAskModel::STEPS + memIndex; i++) {
            prices[i] = 0;
            remains[i] = 0;
        }
    }
}


void PriceModel::movePrices(int askPrice, int bidPrice) {
    if (prices[BidAskModel::STEPS - 1] == askPrice &&
        prices[BidAskModel::STEPS] == bidPrice)
        return;
    else {
        qWarning() << "BidAsk and Tick BidAsk not matched";
        if (prices[BidAskModel::STEPS - 1] != askPrice) {
            int priceIndex = -1;
            for (int i = 0; i < BidAskModel::STEPS; i++) {
                if (prices[i] == askPrice) {
                    priceIndex = i;
                    break;
                }
            }
            //qWarning() << "ASK found index : " << priceIndex;
            if (priceIndex == -1) {
                //qWarning() << "ASK left rotate";
                rotatePrices(-1, true);
                prices[BidAskModel::STEPS - 1] = askPrice;
            }
            else {
                //qWarning() << "ASK right rotate : " << BidAskModel::STEPS - 1 - priceIndex;
                rotatePrices(BidAskModel::STEPS - 1 - priceIndex, true);
            }
        }

        if (prices[BidAskModel::STEPS] != bidPrice) {
            int priceIndex = -1;
            for (int i = BidAskModel::STEPS; i < BidAskModel::STEPS * 2; i++) {
                if (prices[i] == bidPrice) {
                    priceIndex = i;
                    break;
                }
            }
            //qWarning() << "BID found index : " << priceIndex;
            if (priceIndex == -1) {
                //qWarning() << "ASK right rotate";
                rotatePrices(1, false);
                prices[BidAskModel::STEPS] = bidPrice;
            }
            else {
                //qWarning() << "BID left rotate : " << BidAskModel::STEPS - priceIndex;
                rotatePrices(BidAskModel::STEPS - priceIndex, false);
            }
        }
    }
}


void PriceModel::decreaseVolume(int price, uint volume, bool isBuy) {
    int startIndex = 0;
    if (!isBuy)
        startIndex += BidAskModel::STEPS;

    for (int i = startIndex; i < startIndex + BidAskModel::STEPS; i++) {
        if (prices[i] == price) {
            if (volume >= remains[i]) 
                remains[i] = 0;
            else 
                remains[i] -= volume;

            remainDiff[i] = -(volume);
        }
    }
}


void PriceModel::replaceWithNewData(int newPrices[20], uint newRemains[20]) {
    int diff[20] = {0};

    if (isBidaskReceived) {
        for (int i = 0; i < BidAskModel::STEPS; i++) {
            for (int j = 0; j < BidAskModel::STEPS; j++) {
                if (newPrices[i] == prices[j]) {
                    diff[i] = newRemains[i] - remains[j];
                    break;
                }
            }
        }

        for (int i = BidAskModel::STEPS; i < BidAskModel::STEPS * 2; i++) {
            for (int j = BidAskModel::STEPS; j < BidAskModel::STEPS * 2; j++) {
                if (newPrices[i] == prices[j]) {
                    diff[i] = newRemains[i] - remains[j];
                    break;
                }
            }
        }
    }
    memcpy((void *)prices, (void *)newPrices, sizeof(int) * BidAskModel::STEPS * 2);
    memcpy((void *)remains, (void *)newRemains, sizeof(uint) * BidAskModel::STEPS * 2);
    memcpy((void *)remainDiff, (void *)diff, sizeof(int) * BidAskModel::STEPS * 2);
}


void PriceModel::setBidAskTick(CybosBidAskTickData *data) {
    int newPrices[BidAskModel::STEPS * 2] = {0};
    uint newRemains[BidAskModel::STEPS * 2] = {0};

    for (int i = 0; i < data->bid_prices_size(); i++) 
        newPrices[i + BidAskModel::STEPS] = data->bid_prices(i);

    for (int i = 0; i < data->ask_prices_size(); i++) 
        newPrices[BidAskModel::STEPS - i - 1] = data->ask_prices(i);

    for (int i = 0; i < data->bid_remains_size(); i++) 
        newRemains[i + BidAskModel::STEPS] = data->bid_remains(i);

    for (int i = 0; i < data->ask_remains_size(); i++)
        newRemains[BidAskModel::STEPS - i - 1] = data->ask_remains(i);
    currentVolume = 0;
    replaceWithNewData(newPrices, newRemains);
    isBidaskReceived = true;
}


BidAskModel::BidAskModel(QObject *parent)
: QAbstractTableModel(parent) {
    priceModel = new PriceModel;
    
    connect(DataProvider::getInstance(), &DataProvider::tickArrived,
            this, &BidAskModel::tickArrived);
    connect(DataProvider::getInstance(), &DataProvider::bidAskTickArrived,
            this, &BidAskModel::bidAskTickArrived);
    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged,
            this, &BidAskModel::setCurrentStock);

    DataProvider::getInstance()->startStockTick();
    DataProvider::getInstance()->startBidAskTick();
    DataProvider::getInstance()->startStockCodeListening();
    resetData();
}


BidAskModel::~BidAskModel() {
    delete priceModel;
}


void BidAskModel::resetData() {
    setTotalBidRemain(0);
    setTotalAskRemain(0);
    totalBidRemain = 0;
    totalAskRemain = 0;
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


QVariant BidAskModel::data(const QModelIndex &index, int role) const
{
    if (index.column() >= BidAskModel::ASK_DIFF_COLUMN &&
                index.column() <= BidAskModel::BID_DIFF_COLUMN &&
                index.row() >= BidAskModel::START_ROW && index.row() <= BidAskModel::STEPS * 2) {

        if (index.column() == BidAskModel::PRICE_COLUMN) {
            int price = priceModel->getPrice(index.row() - 1);
            if (price != 0)
                return QVariant(price);
        }
        else if (index.column() == BidAskModel::ASK_REMAIN_COLUMN || index.column() == BidAskModel::BID_REMAIN_COLUMN) {
            uint remain = priceModel->getRemain(index.row() - 1, index.column() == BidAskModel::ASK_REMAIN_COLUMN);
            if (remain != 0)
                return QVariant(remain);
        }
        else if (index.column() == BidAskModel::ASK_DIFF_COLUMN || index.column() == BidAskModel::BID_DIFF_COLUMN) {
            int remainDiff = priceModel->getRemainDiff(index.row() - 1, index.column() == BidAskModel::ASK_DIFF_COLUMN);
            if (remainDiff != 0)
                return QVariant(remainDiff);
        }
    }
    return QVariant(QString());
}


void BidAskModel::tickArrived(CybosTickData *data) {
    if (currentStockCode != QString::fromStdString(data->code()))
        return;

    long msec = TimeUtil::TimestampToMilliseconds(data->tick_date());
    //qWarning() << QDateTime::fromMSecsSinceEpoch(msec) << "\tcurrent: " << data->current_price() << ", volume: " << data->volume() << "\tBUY:" << data->buy_or_sell() << "\task: " << data->ask_price() << ", bid: " << data->bid_price();
    setYesterdayClose(data->current_price() - data->yesterday_diff());
    setHighlightPosition(data->current_price());
    priceModel->setTick(data);
    dataChanged(createIndex(1, 1), createIndex(20, 5));
}


void BidAskModel::setHighlightPosition(int price) {
    int index = priceModel->getIndexOfPrice(price);
    setHighlight(index >= 0?index+1:index);
}


void BidAskModel::bidAskTickArrived(CybosBidAskTickData *data) {
    if (currentStockCode != QString::fromStdString(data->code()))
        return;

    priceModel->setBidAskTick(data);
    setTotalAskRemain(data->total_ask_remain());
    setTotalBidRemain(data->total_bid_remain()); 
    //setHighlight(-1);
    dataChanged(createIndex(1, 1), createIndex(20, 5));
    long msec = TimeUtil::TimestampToMilliseconds(data->tick_date());
    //qWarning() << QDateTime::fromMSecsSinceEpoch(msec) << "\tASK: " << data->ask_prices(0) << "(" << data->ask_remains(0) << ")\t" << "BID: " << data->bid_prices(0) << "(" << data->bid_remains(0) << ")";
}


void BidAskModel::setHighlight(int row) {
    //qWarning() << "setHighlight: " << highlight << " to " << row;
    if (highlight != row) {
        highlight = row;
        emit highlightChanged();
    }
}
