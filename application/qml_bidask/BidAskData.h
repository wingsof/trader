#ifndef BIDASK_DATA_H_
#define BIDASK_DATA_H_


#include <QList>
#include <iostream>
#include <QMap>
#include <QDebug>


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

    void setData(int price, int vol, bool isBuy) {
        mPrice = price;
        mVolume = vol;
        mIsBuy = isBuy;

        if (isBuy) {
            if (mBuyMap.contains(price))
                mBuyMap[price] += vol;
            else
                mBuyMap[price] = vol;
            mTotalBuy += (unsigned long long)vol;
        }
        else {
            if (mSellMap.contains(price))
                mSellMap[price] += vol;
            else
                mSellMap[price] = vol;
            mTotalSell += (unsigned long long)vol;
        }
    }
    void setPrice(int p) { mPrice = p; }
    void setVolume(int v) { mVolume = v; }
    void setIsBuy(bool b) { mIsBuy = b; }
    qreal getBuyRate() const {
        return mTotalBuy / float(mTotalBuy + mTotalSell);
    }

    int getVolumeByPrice(bool isBuy, int price) const {
        if (isBuy) {
            if (mBuyMap.contains(price))
                return mBuyMap[price];
        }
        else {
            if (mSellMap.contains(price))
                return mSellMap[price];
        }
        return 0;
    }

    QMap<int, int> mBuyMap;
    QMap<int, int> mSellMap;

    void clear() {
        mPrice = mVolume = 0;
        mTotalBuy = mTotalSell = 0;
        mIsBuy = false;
        mBuyMap.clear();
        mSellMap.clear();
    }

private:
    bool mIsBuy;
    int mPrice;
    int mVolume;
    unsigned long long mTotalBuy;
    unsigned long long mTotalSell;
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
    int getVolumeByPrice(bool isBuy, int price) const { return mTradeUnit.getVolumeByPrice(isBuy, price); }
    qreal getBuyRate() const { return mTradeUnit.getBuyRate(); }
    bool speculateIsViPrice(int price, bool isKospi) const;

private:
    QList<BidAskUnit> mBidSpread;
    QList<BidAskUnit> mAskSpread;
    TradeUnit mTradeUnit;

    bool mBidAskTickReceived;
    QList<qreal> mLowerViPrices;
    QList<qreal> mUpperViPrices;

    const BidAskUnit *getUnitByRow(int row) const;
    void fillBidSpread(CybosBidAskTickData *);
    void fillAskSpread(CybosBidAskTickData *d);
    void updateAskSpread(CybosBidAskTickData *d);
    void updateBidSpread(CybosBidAskTickData *d);

    void setViPrices(int openPrice);
private:
    bool checkPriceOrder(bool bid, CybosBidAskTickData *);


    void debugBidAskTick(CybosBidAskTickData *d);
    void debugTick(CybosTickData *d);

    void debugCurrentBidAsk();
};



#endif
