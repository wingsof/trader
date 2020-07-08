#ifndef VOLUME_PRICE_CHARTVIEW_H_
#define VOLUME_PRICE_CHARTVIEW_H_

#include <QQuickPaintedItem>
#include <QPainter>
#include "DataProvider.h"
#include "MinInfo.h"


class MorningTickChartView : public QQuickPaintedItem {
    Q_OBJECT
    QML_ELEMENT
public:
    enum {
        ROW_COUNT = 16,
        PRICE_ROW_COUNT = 10,
        PRICE_COLUMN_COUNT = 12,
        VOLUME_ROW_COUNT = 2,
        TIME_LABEL_ROW_COUNT = 2,
        SUBJECT_ROW_COUNT = 2,
        COLUMN_COUNT = 14,  // 6 * 2 + 2 (Label)
    };
    MorningTickChartView(QQuickItem *parent = 0);
    void paint(QPainter *painter);

private:
    QString currentStockCode;
    QList<int> priceSteps;
    MinInfo yesterdayMinInfo;
    uint currentVolumeMax;
    uint currentVolumeMin;
    int todayStartHour;
    bool pastMinuteDataReceived;
    QDateTime currentDateTime;

    void resetData();
    void sendRequestData();
    void calculateMinMaxRange();
    void setPriceSteps(int h, int l);
    void updatePriceSteps(int h, int l);
    void setVolumeMinMax(uint h, uint l);
    void updateVolumeMax(uint h);

    qreal mapPriceToPos(int price, qreal startY, qreal endY);
    qreal getCandleLineWidth(qreal w);
    qreal getTimeToXPos(uint time, qreal tickWidth, uint dataStartHour);
    qreal getVolumeHeight(uint v, qreal ch);

    void drawGridLine(QPainter *painter, qreal cw, qreal ch);
    void drawCandle(QPainter *painter, const CybosDayData &data, qreal startX, qreal horizontalGridStep, qreal priceChartEndY);
    void drawVolume(QPainter *painter, const CybosDayData &data, qreal startX, qreal tickWidth, qreal ch, qreal volumeEndY);
    void drawTimeLabels(QPainter *painter, qreal tickWidth, qreal cw, qreal ch, qreal startX, int startHour);
    void drawPriceLabels(QPainter *painter, qreal startX, qreal ch);
    void drawCurrentLineRange(QPainter *painter, MinuteTick * mt,const CybosDayData &data, qreal cw, qreal priceChartEndY);

private slots:
    void setCurrentStock(QString);
    void timeInfoArrived(QDateTime);
    void minuteTickUpdated(QString code);

    void dayDataReceived(QString code, CybosDayDatas *);
    void minuteDataReceived(QString code, CybosDayDatas *);
};

#endif
