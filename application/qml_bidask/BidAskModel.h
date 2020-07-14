#ifndef BIDASK_MODEL_H_
#define BIDASK_MODEL_H_

#include <qqml.h>
#include <QAbstractTableModel>
#include "DataProvider.h"

class PriceModel {
public:
    PriceModel();
    
    void setTick(CybosTickData *data);
    void setBidAskTick(CybosBidAskTickData *data);
    int getPrice(int i);
    uint getRemain(int i, bool isAsk);
    int getRemainDiff(int i, bool isAsk);
    int getIndexOfPrice(int price);

private:
    int *prices;
    uint *remains;
    int *remainDiff;
    int *firstPrices;
    bool isBidaskReceived;
    bool isBuy;
    uint currentVolume;

    void replaceWithNewData(int newPrices[20], uint newRemains[20]);
    void decreaseVolume(int price, uint volume, bool isBuy);
    void movePrices(int askPrice, int bidPrice);
    void rotatePrices(int count, bool isAsk);
};


class BidAskModel : public QAbstractTableModel {
    Q_OBJECT
    Q_PROPERTY(int highlight READ getHighlight WRITE setHighlight NOTIFY highlightChanged)
    Q_PROPERTY(int yesterdayClose READ getYesterdayClose WRITE setYesterdayClose NOTIFY yesterdayCloseChanged)
    Q_PROPERTY(int totalBidRemain READ getTotalBidRemain WRITE setTotalBidRemain NOTIFY totalBidRemainChanged)
    Q_PROPERTY(int totalAskRemain READ getTotalAskRemain WRITE setTotalAskRemain NOTIFY totalAskRemainChanged)
    QML_ELEMENT

public:
    enum {
        START_ROW = 1,
        ASK_DIFF_COLUMN = 1,
        ASK_REMAIN_COLUMN = 2,
        BID_REMAIN_COLUMN = 4,
        BID_DIFF_COLUMN = 5,
        PRICE_COLUMN = 3,
        COLUMN_COUNT = 7,
        ROW_COUNT = 22,
        STEPS = 10
    };
    
    BidAskModel(QObject *parent=nullptr);
    ~BidAskModel();

    int columnCount(const QModelIndex &parent = QModelIndex()) const override
    {
        Q_UNUSED(parent);
        return BidAskModel::COLUMN_COUNT;
    }

    int rowCount(const QModelIndex &parent = QModelIndex()) const override
    {
        Q_UNUSED(parent);
        return BidAskModel::ROW_COUNT;
    }

    QVariant data(const QModelIndex &index, int role) const override;

    QHash<int, QByteArray> roleNames() const override
    {
        return { {Qt::DisplayRole, "display"},
                 {Qt::UserRole + 1, "vdiff" };
    }

    void setHighlight(int row);
    int getHighlight() { return highlight; }

    void setYesterdayClose(int yc);
    int getYesterdayClose() { return yesterdayClose; }

    void setTotalBidRemain(uint br);
    void setTotalAskRemain(uint br);
    uint getTotalBidRemain() { return totalBidRemain; }
    uint getTotalAskRemain() { return totalAskRemain; }

    Q_INVOKABLE void sell_immediately();
    Q_INVOKABLE void buy_immediately();

private:
    int highlight;
    int yesterdayClose;
    uint totalBidRemain;
    uint totalAskRemain;

    QString currentStockCode;
    PriceModel *priceModel;

private:
    int getPriceByRow(int row) const ;
    uint getRemain(int row, int column) const;
    int getRemainDiff(int row, int column) const;
    void resetData();
    void setHighlightPosition(int price);

private slots:
    void tickArrived(CybosTickData *);
    void bidAskTickArrived(CybosBidAskTickData *);
    void setCurrentStock(QString);

signals:
    void highlightChanged();
    void yesterdayCloseChanged();
    void totalAskRemainChanged();
    void totalBidRemainChanged();
};


#endif
