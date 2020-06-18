#ifndef DAY_VIEW_H_
#define DAY_VIEW_H_

#include <QQuickPaintedItem>
#include <QDateTime>
#include <QPainter>
#include "stock_provider.grpc.pb.h"


using stock_api::CybosDayDatas;
using stock_api::CybosDayData;
using stock_api::CybosTickData;

class DayDataProvider;
class StockSelectionThread;
class TickThread;


class DayData {
public:
    static const int PRICE_STEPS = 12;

    DayData();
    ~DayData();

    int countOfData();
    void setData(QString, CybosDayDatas *);
    bool hasData();

    void setTodayData(int o, int h, int l, int c, unsigned long v);
    const CybosDayData &getDayData(int i);
    const QList<int> &getPriceSteps();
    qreal mapPriceToPos(int price, qreal startY, qreal endY);
    qreal mapVolumeToPos(unsigned long volume, qreal startY, qreal endY);
    QDate convertToDate(unsigned int d);
    qreal getSellVolumeHeight(const CybosDayData & data, qreal h);
    qreal getForeignerBuyHeight(const CybosDayData & data, const CybosDayData &prev, qreal h);
    qreal getInstitutionBuyHeight(const CybosDayData & data, qreal h);
    qreal getVolumeStepWidth(int i, qreal w);
    qreal getForeignerStepWidth(int i, qreal w);
    qreal getInstitutionStepWidth(int i, qreal w);
    CybosDayData *getTodayData();

private:
    CybosDayDatas *data;
    CybosDayData *todayData;
    QString code;
    int lowestPrice;
    int highestPrice;
    unsigned long lowestVolume;
    unsigned long highestVolume;
    QList<int> priceSteps;
    QList<unsigned long> volumePPS; // per price steps
    QList<long> foreignerPPS;
    QList<long> institutionPPS;

    void setPriceSteps(int l, int h);
    void setPPS();
    int getIndexOfPriceSteps(int price);
};

class DayView : public QQuickPaintedItem {
    Q_OBJECT
    Q_PROPERTY(QString stockCode READ getStockCode WRITE setStockCode NOTIFY stockCodeChanged)
    Q_PROPERTY(int countDays READ getCountDays WRITE setCountDays NOTIFY countDaysChanged)
    Q_PROPERTY(QDateTime untilTime READ getUntilTime WRITE setUntilTime NOTIFY untilTimeChanged)
    QML_ELEMENT

public:
    DayView(QQuickItem *parent = 0);
    void paint(QPainter *painter);


    Q_INVOKABLE void search(QString stockCode, QDateTime untilTime, int countDays);

    QString getStockCode() { return stockCode; }
    int getCountDays() { return countDays; }
    QDateTime getUntilTime() { return untilTime; }

    void setStockCode(QString code);
    void setUntilTime(QDateTime dt);
    void setCountDays(int count);

private:
    void fillBackground(QPainter *painter, const QSizeF &itemSize);
    void drawGridLine(QPainter *painter, const QSizeF &itemSize, qreal lineVerticalSpace, qreal endX, int spaceCount);
    void drawPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace);
    void drawForeignerPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace);
    void drawInstitutionPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace);
    void drawPriceLabels(QPainter *painter, qreal startX, qreal priceChartEndY, qreal priceHeightSpace);
    void drawCandle(QPainter *painter, const CybosDayData *data, qreal startX, qreal horizontalGridStep, qreal priceChartEndY);
    qreal drawVolume(QPainter *painter, const CybosDayData *data, qreal startX, qreal horizontalGridStep, qreal volumeEndY, qreal priceChartEndY, bool divideBuySell);

private:
    QString stockCode;
    int countDays;
    QDateTime untilTime;
    DayDataProvider *provider;
    StockSelectionThread *stockSelector;
    DayData *dayData;
    TickThread *tickThread;

    qreal getCandleLineWidth(qreal gap);

signals:
    void stockCodeChanged();
    void countDaysChanged();
    void untilTimeChanged();

private slots:
    void dataReceived(QString, CybosDayDatas *);
    void searchReceived(QString, QDateTime, int);
    void tickDataArrived(CybosTickData *);
};


#endif
