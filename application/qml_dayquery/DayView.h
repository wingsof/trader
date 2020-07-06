#ifndef DAY_VIEW_H_
#define DAY_VIEW_H_

#include <QQuickPaintedItem>
#include <QDateTime>
#include <QPainter>
#include "DataProvider.h"
#include "stock_provider.grpc.pb.h"


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
    int   mapPosToPrice(int yPos, qreal startY, qreal endY);
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
    QML_ELEMENT

public:
    DayView(QQuickItem *parent = 0);
    void paint(QPainter *painter);

    void search(QString stockCode, QDateTime untilTime, int countDays);

private:
    void fillBackground(QPainter *painter, const QSizeF &itemSize);
    void drawGridLine(QPainter *painter, const QSizeF &itemSize, qreal lineVerticalSpace, qreal endX, int spaceCount);
    void drawPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace);
    void drawForeignerPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace);
    void drawInstitutionPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace);
    void drawPriceLabels(QPainter *painter, qreal startX, qreal priceChartEndY, qreal priceHeightSpace);
    void drawCandle(QPainter *painter, const CybosDayData *data, qreal startX, qreal horizontalGridStep, qreal priceChartEndY);
    qreal drawVolume(QPainter *painter, const CybosDayData *data, qreal startX, qreal horizontalGridStep, qreal volumeEndY, qreal priceChartEndY, bool divideBuySell);

protected:
    void mouseReleaseEvent(QMouseEvent *e);
    void mouseMoveEvent(QMouseEvent *e);
    void mousePressEvent(QMouseEvent *e);

private:
    QString stockCode;
    int countDays;
    QDateTime untilTime;
    DayData *dayData;
    qreal priceEndY;

    qreal drawHorizontalY;

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
