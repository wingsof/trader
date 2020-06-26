#include "MorningTickChartView.h"
#include "Util.h"
#include "MinuteData.h"
#include <QDebug>


MorningTickChartView::MorningTickChartView(QQuickItem *parent)
: QQuickPaintedItem(parent) {
    todayStartHour = 9;
    connect(DataProvider::getInstance(), &DataProvider::minuteTickUpdated,
            this, &MorningTickChartView::minuteTickUpdated);
    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged,
            this, &MorningTickChartView::setCurrentStock);
    connect(DataProvider::getInstance(), &DataProvider::dayDataReady, this, &MorningTickChartView::dayDataReceived);
    connect(DataProvider::getInstance(), &DataProvider::minuteDataReady, this, &MorningTickChartView::minuteDataReceived);

    DataProvider::getInstance()->collectMinuteData(3);
    DataProvider::getInstance()->startStockCodeListening();
    DataProvider::getInstance()->startStockTick();
    // setCurrentStock("A005930", QDateTime(QDate(2020, 6, 12)), 0);
}


void MorningTickChartView::resetData() {
    currentVolumeMin = currentVolumeMax = 0;
    yesterdayMinInfo.clear();
}


void MorningTickChartView::setCurrentStock(QString code, QDateTime dt, int countOfDays) {
    Q_UNUSED(countOfDays);
    if (currentStockCode != code) {
        resetData();
        currentStockCode = code;
        qWarning() << "currentStock: " << currentStockCode;
        DataProvider::getInstance()->requestDayData(currentStockCode, 60, dt.addDays(-1));
    }
}


void MorningTickChartView::minuteTickUpdated(QString code) {
    if (currentStockCode != code)
        return;

    MinuteTick *mt = DataProvider::getInstance()->getMinuteTick(currentStockCode);
    //qWarning() << "highest : " << mt->getHighestPrice() << ", lowest" << mt->getLowestPrice() << "highest volume: " << currentVolumeMax << "\tlowest volume: " << currentVolumeMin;
    updatePriceSteps(mt->getHighestPrice(), mt->getLowestPrice());
    updateVolumeMax(mt->getHighestVolume());
    update(); 
}


qreal MorningTickChartView::mapPriceToPos(int price, qreal startY, qreal endY) {
    qreal priceGap = priceSteps.at(priceSteps.size() - 1) - priceSteps.at(0); 
    qreal positionGap = startY - endY; // device coordinate zero is started from upper
    qreal pricePosition = price - priceSteps.at(0);
    qreal result = startY - pricePosition * positionGap / priceGap;
    return result;
}


void MorningTickChartView::dayDataReceived(QString code, CybosDayDatas *data) {
    if (currentStockCode != code) 
        return;

    int count = data->day_data_size();
    qWarning() << "day data : " << count;
    if (count > 0) {
        const CybosDayData &d = data->day_data(count - 1);
        QDate date = morning::Util::convertToDate(d.date());
        DataProvider::getInstance()->requestMinuteData(currentStockCode, QDateTime(date, QTime(0, 0, 0)), QDateTime(date, QTime(23, 59, 0)));
    }
}


void MorningTickChartView::minuteDataReceived(QString code, CybosDayDatas *data) {
    if (currentStockCode != code) 
        return;
    //qWarning() << "minute data : " << data->day_data_size();
    int count = data->day_data_size();

    if (count > 0) {
        //qWarning() << "date : " << data->day_data(0).date();
        yesterdayMinInfo.setData(data);
        if (yesterdayMinInfo.isCloserToMaximum()) {
            setPriceSteps((int)(yesterdayMinInfo.getHighestPrice() * 1.05),
                            yesterdayMinInfo.getLowestPrice());
        }
        else {
            setPriceSteps(yesterdayMinInfo.getHighestPrice(),
                            (int)(yesterdayMinInfo.getLowestPrice() * 0.95));
        }
        setVolumeMinMax(yesterdayMinInfo.getHighestVolume(), yesterdayMinInfo.getLowestVolume());
        update();
    }
    else {
        qWarning() << "NO MINUTE DATA";
    }
}


void MorningTickChartView::setVolumeMinMax(uint h, uint l) {
    if (currentVolumeMax == 0) {
        currentVolumeMax = h;
        currentVolumeMin = l;
    }
    else {
        if (currentVolumeMin == 0 || l < currentVolumeMin)
            currentVolumeMin = l;

        if (h > currentVolumeMax)
            currentVolumeMax = h;
    }
    qWarning() << "volume max : " << currentVolumeMax << "\tvolume min : " << currentVolumeMin;
}


void MorningTickChartView::updateVolumeMax(uint h) {
    if (h > currentVolumeMax)
        currentVolumeMax = h;
}


void MorningTickChartView::drawGridLine(QPainter *painter, qreal cw, qreal ch) {
    painter->save();
    QPen pen = painter->pen();
    pen.setWidth(1);
    pen.setColor(QColor("#d7d7d7"));
    painter->setPen(pen);
  
    for (int i = 0; i < ROW_COUNT / 2 - 1; i++) {
        QLineF line(0, ch * 2 * (i+1), (cw) * PRICE_COLUMN_COUNT, ch * 2 * (i+1));
        painter->drawLine(line); 
    }

    pen.setColor(QColor("#ff0000"));
    painter->setPen(pen);
    QLineF lineMiddle(cw * PRICE_COLUMN_COUNT / 2, 0, cw * PRICE_COLUMN_COUNT / 2, ch * (ROW_COUNT - 2));
    painter->drawLine(lineMiddle);

    pen.setColor(QColor("#d7d7d7"));
    painter->setPen(pen);
    QLineF lineRight(cw * PRICE_COLUMN_COUNT, 0, cw * PRICE_COLUMN_COUNT, ch * (ROW_COUNT - 2));
    painter->drawLine(lineRight);
    painter->restore(); 
}


void MorningTickChartView::setPriceSteps(int h, int l) {
    priceSteps.clear();
    int priceGap = (h - l) / PRICE_ROW_COUNT;
    if (priceGap < 100)
        priceGap = 10;
    else
        priceGap = 100;

    int minimumUnit = l - (l % priceGap);
    int step = (h - minimumUnit) / PRICE_ROW_COUNT;
    step = step - (step % priceGap);
    while (step * PRICE_ROW_COUNT + minimumUnit < h) 
        step += priceGap;

    for (int i = 0; i < PRICE_ROW_COUNT + 1; i++) 
        priceSteps.append(minimumUnit + step * i);
    qWarning() << "steps : " << priceSteps;
}


void MorningTickChartView::updatePriceSteps(int h, int l) {
    if (priceSteps.count() == 0) {
        setPriceSteps((int)(h * 1.05), (int)(l * 0.95));
    }
    else {
        if (l < priceSteps.at(0)) 
            setPriceSteps(priceSteps.at(priceSteps.count() - 1), int(l * 0.95));

        if (h > priceSteps.at(priceSteps.count() - 1)) 
            setPriceSteps((int)(h * 1.05), priceSteps.at(0));
    }
}


qreal MorningTickChartView::getCandleLineWidth(qreal w) {
    if (w * 0.2 < 1.0)
        return 1.0;
    return (int)w * 0.2;
}


qreal MorningTickChartView::getVolumeHeight(uint v, qreal ch) {
    if (v < currentVolumeMin)
        return 0.0;

    qreal vRange = qreal(currentVolumeMax - currentVolumeMin);
    qWarning() << "vol diff : " << (v - currentVolumeMin) << "\tvRange : " << vRange << "\t ch : " << ch;
    return ch * VOLUME_ROW_COUNT * (v - currentVolumeMin) / vRange;
}


void MorningTickChartView::drawVolume(QPainter *painter, const CybosDayData &data, qreal startX, qreal tickWidth, qreal ch, qreal volumeEndY) {
    QColor color;
    painter->save();
    if (data.cum_sell_volume() > data.cum_buy_volume())
        color.setRgb(0, 0, 255);
    else
        color.setRgb(255, 0, 0);
    painter->setBrush(QBrush(color));
    painter->setPen(Qt::NoPen);
    qreal volumeHeight = getVolumeHeight(data.volume(), ch);
    qWarning() << "volume : " << data.volume() << "\t" << QRectF(startX, volumeEndY - volumeHeight, tickWidth, volumeHeight);
    painter->drawRect(QRectF(startX, volumeEndY - volumeHeight, tickWidth, volumeHeight));
    painter->restore();
}


void MorningTickChartView::drawCandle(QPainter *painter, const CybosDayData &data, qreal startX, qreal horizontalGridStep, qreal priceChartEndY) {
    QColor color;
    painter->save();
    if (data.close_price() >= data.start_price()) 
        color.setRgb(255, 0, 0);
    else 
        color.setRgb(0, 0, 255);
    QPen pen = painter->pen();
    painter->setBrush(QBrush(color));
    pen.setColor(color);

    qreal penWidth = getCandleLineWidth(horizontalGridStep);
    pen.setWidthF(penWidth);
    painter->setPen(pen);
    qreal candle_y_low = mapPriceToPos(data.lowest_price(), priceChartEndY, 0);
    qreal candle_y_high = mapPriceToPos(data.highest_price(), priceChartEndY, 0);
    qreal candle_y_open = mapPriceToPos(data.start_price(), priceChartEndY, 0);
    qreal candle_y_close = mapPriceToPos(data.close_price(), priceChartEndY, 0);

    qreal line_x = startX + (horizontalGridStep / 2);
    painter->drawLine(QLineF(line_x, candle_y_high, line_x, candle_y_low));
    painter->drawRect(QRectF(startX, candle_y_open, horizontalGridStep, candle_y_close - candle_y_open));

    painter->restore();
}


qreal MorningTickChartView::getTimeToXPos(uint time, qreal tickWidth, uint dataStartHour) {
    QTime startTime = QTime((int)dataStartHour, 0, 0);
    QTime dataTime = QTime(int(time / 100), int(time % 100), 0);
    qreal diff = (dataTime.msecsSinceStartOfDay() - startTime.msecsSinceStartOfDay()) / 1000.0 / 180.0;
    //qWarning() << time << "\t" << tickWidth * 2 * diff << "\t" << diff << "\t" ;//<< tickWidth * PRICE_COLUMN_COUNT / 2;
    return tickWidth * 2 * diff;
}


void MorningTickChartView::drawPriceLabels(QPainter *painter, qreal startX, qreal ch) {
    painter->save();
    QPen pen = painter->pen();
    pen.setColor(QColor("#000000"));
    painter->setPen(pen);

    for (int i = 0; i < priceSteps.count() - 1; i++) {
        painter->drawText((int)startX, (int)(ch * PRICE_ROW_COUNT  - ch * i),
                            QString::number(priceSteps.at(i)));
    }
    painter->restore();
}


void MorningTickChartView::drawTimeLabels(QPainter *painter, qreal tickWidth, 
                                            qreal cw, qreal ch, qreal startX, int startHour) {
    painter->save();
    QPen pen;
    pen.setWidth(1);
    painter->setPen(pen);

    QTime t = QTime(int(startHour), 0, 0);
    qreal yPos = ch * (PRICE_ROW_COUNT + TIME_LABEL_ROW_COUNT + SUBJECT_ROW_COUNT);
    for (int i = 1; i < 14; i++) { //14
        t = t.addSecs(60 * 30); // 30 min
        QString label;
        qreal xPos = getTimeToXPos(uint(t.hour() * 100 + t.minute()), tickWidth, startHour);
        qreal lineHeight = ch / 6;
        if (i % 2 == 0) {
            label = QString::number(startHour + (i / 2));
            lineHeight = ch / 5;
            QLineF line(startX + xPos, 0, startX + xPos, yPos + lineHeight);
            pen.setColor(QColor("#d7d7d7"));
            painter->setPen(pen);
            painter->drawLine(line); 
            pen.setColor(Qt::black);
            painter->setPen(pen);
            painter->drawText(QRectF(startX + xPos - cw / 6,
                                    yPos + lineHeight, cw / 3, ch / 3),
                                Qt::AlignCenter, label);

        }
        else {
            QLineF line(startX + xPos, 0, startX + xPos, yPos + lineHeight);
            pen.setColor(QColor("#50d7d7d7"));
            painter->setPen(pen);
            painter->drawLine(line); 
        }
    }
    painter->restore();
}


void MorningTickChartView::drawCurrentLineRange(QPainter *painter, const CybosDayData &data, qreal cw, qreal priceChartEndY) {
    painter->save();
    QPen pen;
    pen.setStyle(Qt::DashLine);
    pen.setWidth(1);
    pen.setColor("#ff0000");
    painter->setPen(pen);

    qreal current_y = mapPriceToPos(data.close_price(), priceChartEndY, 0);
    qreal upper_y = mapPriceToPos(data.close_price() * 1.03, priceChartEndY, 0);;
    qreal lower_y = mapPriceToPos(data.close_price() * 0.97, priceChartEndY, 0);;
    painter->drawLine(QLineF(0, current_y, cw * PRICE_COLUMN_COUNT, current_y));
    painter->drawText(int(cw * PRICE_COLUMN_COUNT + cw), int(current_y), QString::number(data.close_price()));
    pen.setColor("#30000000");
    painter->setPen(pen);
    painter->drawLine(QLineF(0, upper_y, cw * PRICE_COLUMN_COUNT, upper_y));
    painter->drawLine(QLineF(0, lower_y, cw * PRICE_COLUMN_COUNT, lower_y));

    painter->restore();
}


void MorningTickChartView::paint(QPainter *painter) {
    painter->setRenderHint(QPainter::Antialiasing);
    QSizeF canvasSize = size();
    qreal cellHeight = canvasSize.height() / ROW_COUNT;
    qreal cellWidth = canvasSize.width() / COLUMN_COUNT;
    //qWarning() << canvasSize << "\t" << cellWidth * PRICE_COLUMN_COUNT / 2;

    drawGridLine(painter, cellWidth, cellHeight);
    drawPriceLabels(painter, canvasSize.width() - cellWidth * 2 + 10, cellHeight);
    qreal startX = 0;
    qreal tickCount = 131; // normally 9:00 ~ 15:30 : 390 min / 3 : 130 ticks
    qreal tickWidth = cellWidth * (PRICE_COLUMN_COUNT / 2)  / (tickCount * 2 - 1);
    if (!yesterdayMinInfo.isEmpty()) {
        uint dataStartHour = yesterdayMinInfo.get(0).time();
        drawTimeLabels(painter, tickWidth, cellWidth, cellHeight, startX, int(dataStartHour / 100));
        for (int i = 0; i < yesterdayMinInfo.count(); i++) {
            const CybosDayData &d = yesterdayMinInfo.get(i);
            qreal xPos = getTimeToXPos(d.time(), tickWidth, int(dataStartHour / 100));
            drawCandle(painter, d, startX + xPos, tickWidth, cellHeight * PRICE_ROW_COUNT);
            drawVolume(painter, d, startX + xPos, tickWidth, cellHeight, cellHeight * (PRICE_ROW_COUNT + VOLUME_ROW_COUNT));
        }
    }

    if (!currentStockCode.isEmpty()) {
        startX = cellWidth * (PRICE_COLUMN_COUNT  / 2) + 1;
        MinuteTick *mt = DataProvider::getInstance()->getMinuteTick(currentStockCode);
        if (mt == NULL)
            return;

        const CybosDayDatas &queue = mt->getQueue();
        drawTimeLabels(painter, tickWidth, cellWidth, cellHeight, startX, todayStartHour);

        for (int i = 0; i < queue.day_data_size(); i++) {
            const CybosDayData &d = queue.day_data(i);
            qreal xPos = getTimeToXPos(d.time(), tickWidth, todayStartHour);
            drawCandle(painter, d, startX + xPos, tickWidth, cellHeight * PRICE_ROW_COUNT);
            drawVolume(painter, d, startX + xPos, tickWidth, cellHeight, cellHeight * (PRICE_ROW_COUNT + VOLUME_ROW_COUNT));
        }

        if (mt->getCurrent().start_price() != 0) {
            const CybosDayData &d = mt->getCurrent();
            qreal xPos = getTimeToXPos(d.time(), tickWidth, todayStartHour);
            drawCandle(painter, d, startX + xPos, tickWidth, cellHeight * PRICE_ROW_COUNT);
            drawVolume(painter, d, startX + xPos, tickWidth, cellHeight, cellHeight * (PRICE_ROW_COUNT + VOLUME_ROW_COUNT));
            drawCurrentLineRange(painter, d, cellWidth, cellHeight * PRICE_ROW_COUNT);
        }
    }
}
