#ifndef BIDASK_DATA_H_
#define BIDASK_DATA_H_


#include <QList>
#include <iostream>


#include "stock_provider.grpc.pb.h"
using stock_api::CybosBidAskTickData;
using stock_api::CybosTickData;

class BidAskUnit {
public:
    BidAskUnit(int price) {
        mPrice = price;
        mRemain = mDiff = 0;
    }

    int price() const { return mPrice; }
    int remain() const { return mRemain; }
    int diff() const { return mDiff; }
    void setCurrentRemain(int current) {
        if (remain() == 0)
            mRemain = current;
        else {
            mDiff = current - remain();
        }
    }

private:
    int mPrice;
    int mRemain;
    int mDiff;
};



class TradeUnit {
public:
    TradeUnit() {
        clear();
    }

    int volume() const { return mVolume; }
    int price() const { return mPrice; }
    bool isBuy() const { return mIsBuy; }

    void setPrice(int p) { mPrice = p; }
    void setVolume(int v) { mVolume = v; }
    void setIsBuy(bool b) { mIsBuy = b; }

    void clear() {
        mPrice = mVolume = 0;
        mIsBuy = false;
    }

private:
    bool mIsBuy;
    int mPrice;
    int mVolume;
};


class BidAskData {
public:
    BidAskData();

    void setTick(CybosTickData *d);
    void setBidAskTick(CybosBidAskTickData *d);
    void resetData();
    int getPriceByRow(int row) const;
    int getRemainByRow(int row) const;
    int getDiffByRow(int row) const;
    int getRowByPrice(int price) const;
    int getCurrentPrice() const { return mTradeUnit.price(); } 
    bool getIsCurrentBuy() const { return mTradeUnit.isBuy(); }
    int getCurrentVolume() const { return mTradeUnit.volume(); }

private:
    QList<BidAskUnit> mBidSpread;
    QList<BidAskUnit> mAskSpread;
    TradeUnit mTradeUnit;

    bool mBidAskTickReceived;

    const BidAskUnit *getUnitByRow(int row) const;
    void fillBidSpread(CybosBidAskTickData *);
    void fillAskSpread(CybosBidAskTickData *d);
    void updateAskSpread(CybosBidAskTickData *d);
    void updateBidSpread(CybosBidAskTickData *d);
private:
    bool checkPriceOrder(bool bid, CybosBidAskTickData *);


    void debugBidAskTick(CybosBidAskTickData *d);
    void debugTick(CybosTickData *d);

    void debugCurrentBidAsk();
};



#endif
