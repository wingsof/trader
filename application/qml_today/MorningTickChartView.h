#ifndef VOLUME_PRICE_CHARTVIEW_H_
#define VOLUME_PRICE_CHARTVIEW_H_

#include <QQuickPaintedItem>
#include <QPainter>
#include <QTransform>
#include <QPair>
#include <QWheelEvent>
#include "DataProvider.h"
#include "MinInfo.h"
#include "AuxiliaryInfo.h"


class MorningTickChartView : public QQuickPaintedItem {
    Q_OBJECT
    QML_ELEMENT
public:
    enum {
        ROW_COUNT = 16,
        PRICE_ROW_COUNT = 10,
        TODAY_COLUMN_COUNT = 7,
        YESTERDAY_COLUMN_COUNT = 6,
        PRICE_COLUMN_COUNT = TODAY_COLUMN_COUNT + YESTERDAY_COLUMN_COUNT,
        VOLUME_ROW_COUNT = 2,
        TIME_LABEL_ROW_COUNT = 2,
        SUBJECT_ROW_COUNT = 2,
        COLUMN_COUNT = 15,  // 7 * 2 + 2 (Label)
    };
    MorningTickChartView(QQuickItem *parent = 0);
    void paint(QPainter *painter);

    qreal mapPriceToPos(int price, qreal startY, qreal endY);

private:
    QString currentStockCode;
    QList<int> priceSteps;
    MinInfo yesterdayMinInfo;
    uint currentVolumeMax;
    uint currentVolumeMin;
    QTime todayStartTime;
    bool pastMinuteDataReceived;
    QDateTime currentDateTime;
    QTransform mTransform;
    qreal mScale = 1.0;
    QPoint mPrevPoint;
    qreal mDrawHorizontalCurrentX = 0.0;
    qreal mDrawHorizontalStartX = 0.0;

    void resetData();
    void sendRequestData();
    void calculateMinMaxRange();
    void setPriceSteps(int h, int l);
    void updatePriceSteps(int h, int l);
    void setVolumeMinMax(uint h, uint l);
    void updateVolumeMax(uint h);
    void addToTimePricePair(QList<QPair<int,int> > &lp, const CybosDayData &);

    qreal getCandleLineWidth(qreal w);
    //qreal getTimeToXPos(uint time, qreal tickWidth, uint dataStartHour);
    qreal getTimeToXPos(uint t, qreal tickWidth, uint startTime);
    qreal getVolumeHeight(uint v, qreal ch);

    void drawGridLine(QPainter *painter, qreal cw, qreal ch);
    void drawCandle(QPainter *painter, const CybosDayData &data, qreal startX, qreal horizontalGridStep, qreal priceChartEndY);
    void drawVolume(QPainter *painter, const CybosDayData &data, qreal startX, qreal tickWidth, qreal ch, qreal volumeEndY);
    void drawTimeLabels(QPainter *painter, qreal tickWidth, qreal cw, qreal ch, qreal startX, int cellCount, uint startTime);
    void drawPriceLabels(QPainter *painter, qreal startX, qreal ch);
    void drawCurrentLineRange(QPainter *painter, MinuteTick * mt, qreal startX, const CybosDayData &data, qreal cw, qreal priceChartEndY);

protected:
    void wheelEvent(QWheelEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;

private slots:
    void setCurrentStock(QString);
    void timeInfoArrived(QDateTime);
    void minuteTickUpdated(QString code);

    void dayDataReceived(QString code, CybosDayDatas *);
    void minuteDataReceived(QString code, CybosDayDatas *);
};

#endif
