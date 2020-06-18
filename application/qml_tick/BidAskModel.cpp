#include "BidAskModel.h"
#include <QDebug>


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


void PriceModel::setTick(CybosTickData *data) {
    currentVolume = data->volume();
    isBuy = data->buy_or_sell();
    for (int i = 0; i < BidAskModel::STEPS * 2; i++)
        remainDiff[i] = 0;

    if (!isBidaskReceived) {
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

            if (priceIndex == -1) {
                rotatePrices(-1, true);
                prices[BidAskModel::STEPS - 1] = askPrice;
            }
            else {
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

            if (priceIndex == -1) {
                rotatePrices(1, false);
                prices[BidAskModel::STEPS] = bidPrice;
            }
            else {
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
                remains[i] = remains[i] - volume;
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
    bidPrices = new int[BidAskModel::STEPS];
    askPrices = new int[BidAskModel::STEPS];
    bidRemains = new uint[BidAskModel::STEPS];
    askRemains = new uint[BidAskModel::STEPS];
    bidRemainDiff = new int[BidAskModel::STEPS];
    askRemainDiff = new int[BidAskModel::STEPS];

    
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
    delete bidPrices;
    delete askPrices;
    delete bidRemains;
    delete askRemains;
}


void BidAskModel::resetData() {
    for (int i = 0; i < BidAskModel::STEPS; i++) {
        bidPrices[i] = 0;
        askPrices[i] = 0;
        bidRemains[i] = 0;
        askRemains[i] = 0;
        bidRemainDiff[i] = 0;
        askRemainDiff[i] = 0;
    }
    setTotalBidRemain(0);
    setTotalAskRemain(0);
    totalBidRemain = 0;
    totalAskRemain = 0;
    currentTick = NULL;
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


void BidAskModel::setCurrentStock(QString code, QDateTime dt, int countOfDays) {
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
            int price = getPriceByRow(index.row());
            if (price != 0)
                return QVariant(price);
        }
        else if (index.column() == BidAskModel::ASK_REMAIN_COLUMN || index.column() == BidAskModel::BID_REMAIN_COLUMN) {
            uint remain = getRemain(index.row(), index.column());
            if (remain != 0)
                return QVariant(remain);
        }
        else if (index.column() == BidAskModel::ASK_DIFF_COLUMN || index.column() == BidAskModel::BID_DIFF_COLUMN) {
            int remainDiff = getRemainDiff(index.row(), index.column());
            if (remainDiff != 0)
                return QVariant(remainDiff);
        }
    }
    return QVariant(QString());
}


int BidAskModel::getPriceByRow(int row) const {
    int index = row - BidAskModel::START_ROW;
    if (index < 0 || index >= BidAskModel::STEPS * 2)
        return 0;

    if (index >= BidAskModel::STEPS)
        return bidPrices[index - BidAskModel::STEPS];

    return askPrices[BidAskModel::STEPS - index - 1];
}


uint BidAskModel::getRemain(int row, int column) const {
    int index = row - BidAskModel::START_ROW;
    if (index < 0 || index >= BidAskModel::STEPS * 2)
        return 0;

    if (column == BidAskModel::ASK_REMAIN_COLUMN) {
        if (index < BidAskModel::STEPS)
            return askRemains[BidAskModel::STEPS - index - 1];        
        else if (index == BidAskModel::STEPS &&
                        currentTick != NULL &&
                        !currentTick->buy_or_sell())
            return currentTick->volume();
    }
    else if (column == BidAskModel::BID_REMAIN_COLUMN) {
        if (index >= BidAskModel::STEPS && index < BidAskModel::STEPS * 2)
            return bidRemains[index - BidAskModel::STEPS];
        else if (index == BidAskModel::STEPS - 1 &&
                        currentTick != NULL &&
                        currentTick->buy_or_sell())
            return currentTick->volume();
    }
    return 0;
}


int BidAskModel::getRemainDiff(int row, int column) const {
    int index = row - BidAskModel::START_ROW;
    if (index < 0 || index >= BidAskModel::STEPS * 2)
        return 0;

    if (column == BidAskModel::ASK_DIFF_COLUMN && index < BidAskModel::STEPS) {
        return askRemainDiff[BidAskModel::STEPS - index - 1];        
    }
    else if (column == BidAskModel::BID_DIFF_COLUMN && index >= BidAskModel::STEPS && index < BidAskModel::STEPS * 2) {
        return bidRemainDiff[index - BidAskModel::STEPS];
    }
    return 0;
}


void BidAskModel::tickArrived(CybosTickData *data) {
    if (currentStockCode != QString::fromStdString(data->code()))
        return;
    qWarning() << "current: " << data->current_price() << ", volume: " << data->volume() << "\tBUY:" << data->buy_or_sell();
    currentTick = data;
    int startRow = 10;
    int endRow = 11;
    setYesterdayClose(data->current_price() - data->yesterday_diff());
    setHighlightPosition();

    if (startRow > highlight)
        startRow = highlight;
    else if (endRow < highlight)
        endRow = highlight;
    dataChanged(createIndex(startRow, 1), createIndex(endRow, 5));
}


void BidAskModel::setHighlightPosition() {
    if (currentTick) {
        //qWarning() << "setHighlightPosition: " << currentTick->current_price();
        for (int i = 0; i < BidAskModel::STEPS; i++) {
            if (bidPrices[i] == currentTick->current_price()) {
                setHighlight(i + BidAskModel::STEPS + 1);
                return;
            }
        }
        for (int i = 0; i < BidAskModel::STEPS; i++) {
            if (askPrices[i] == currentTick->current_price()) {
                setHighlight(BidAskModel::STEPS - i);
                return;
            }
        }
    }
    else {
        setHighlight(-1);
    }
}


void BidAskModel::bidAskTickArrived(CybosBidAskTickData *data) {
    if (currentStockCode != QString::fromStdString(data->code()))
        return;

    bool priceChanged = false;

    for (int i = 0; i < data->ask_prices_size(); i++) {
        if (askPrices[i] != data->ask_prices(i))
            priceChanged = true;

        askPrices[i] = data->ask_prices(i);
    }
    
    for (int i = 0; i < data->bid_prices_size(); i++) {
        if (bidPrices[i] != data->bid_prices(i))
            priceChanged = true;

        bidPrices[i] = data->bid_prices(i);
    }

    if (priceChanged) {
        for (int i = 0; i < data->ask_remains_size(); i++)
            askRemains[i] = data->ask_remains(i);

        for (int i = 0; i < data->bid_remains_size(); i++)
            bidRemains[i] = data->bid_remains(i);
    }

    for (int i = 0; i < data->ask_remains_size(); i++) {
        if (askRemains[i] != 0) {
            askRemainDiff[i] = data->ask_remains(i) - askRemains[i];
        }
        askRemains[i] = data->ask_remains(i);
    }
    
    for (int i = 0; i < data->bid_remains_size(); i++) {
        if (bidRemains[i] != 0) {
            bidRemainDiff[i] = data->bid_remains(i) - bidRemains[i];
        }
        bidRemains[i] = data->bid_remains(i);
    }
    setTotalAskRemain(data->total_ask_remain());
    setTotalBidRemain(data->total_bid_remain()); 
    dataChanged(createIndex(1, 1), createIndex(20, 5));
    setHighlightPosition();

    qWarning() << "ASK: " << data->ask_prices(0) << "(" << data->ask_remains(0) << ")\t" << "BID: " << data->bid_prices(0) << "(" << data->bid_remains(0) << ")";
}


void BidAskModel::setHighlight(int row) {
    //qWarning() << "setHighlight: " << highlight << " to " << row;
    if (highlight != row) {
        highlight = row;
        emit highlightChanged();
    }
}
