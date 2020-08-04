#include "MorningTickChartView.h"
#include "Util.h"
#include "MinuteData.h"
#include <QDebug>


#define TICK_SPACE_RATIO    (3.0/4.0)


MorningTickChartView::MorningTickChartView(QQuickItem *parent)
: QQuickPaintedItem(parent), yesterdayMinInfo(3) {
    //setOpaquePainting(true);
    //setAntialiasing(true);
    setAcceptedMouseButtons(Qt::AllButtons);
    //todayStartHour = 9;
    todayStartTime = QTime(8, 30);
    connect(DataProvider::getInstance(), &DataProvider::minuteTickUpdated,
            this, &MorningTickChartView::minuteTickUpdated);
    connect(DataProvider::getInstance(), &DataProvider::stockCodeChanged,
            this, &MorningTickChartView::setCurrentStock);
    connect(DataProvider::getInstance(), &DataProvider::dayDataReady, this, &MorningTickChartView::dayDataReceived);
    connect(DataProvider::getInstance(), &DataProvider::minuteDataReady, this, &MorningTickChartView::minuteDataReceived);

    // sequence is important, first MinuteData clear data and then call timeInfoArrived of MorningTickChartView
    DataProvider::getInstance()->collectMinuteData(3);
    connect(DataProvider::getInstance(), &DataProvider::timeInfoArrived, this, &MorningTickChartView::timeInfoArrived);

    DataProvider::getInstance()->startStockCodeListening();
    DataProvider::getInstance()->startStockTick();
}


void MorningTickChartView::wheelEvent(QWheelEvent *event) {
    if (event->orientation() == Qt::Vertical) {
        auto pos = event->pos();
        mScale = 1 + (float(event->delta())/1200);
        auto tm = QTransform()
                .translate(pos.x(), pos.y())
                .scale(mScale, mScale)
                .translate(-pos.x(), -pos.y());
        mTransform *= tm;
        update();
    }
}


void MorningTickChartView::mousePressEvent(QMouseEvent *event) {
    if (event->button() == Qt::LeftButton) {
        mPrevPoint = event->pos();
    }
    else if (event->button() == Qt::RightButton) {
        QPoint pos = mTransform.inverted().map(event->pos());
        mDrawHorizontalStartX = pos.x();
    }
}


void MorningTickChartView::mouseReleaseEvent(QMouseEvent *event) {
    mDrawHorizontalStartX = mDrawHorizontalCurrentX = 0.0;
    update();
}


void MorningTickChartView::mouseMoveEvent(QMouseEvent *event) {
    if (event->buttons() & Qt::LeftButton) {
        auto curPos = event->pos();
        auto offsetPos = curPos - mPrevPoint;
        auto tm = QTransform()
                .translate(offsetPos.x(), offsetPos.y());
        mPrevPoint = curPos;
        mTransform *= tm;
        update();
    }
    else if (event->buttons() & Qt::RightButton) {
        QPoint pos = mTransform.inverted().map(event->pos());
        mDrawHorizontalCurrentX = pos.x();
        update();
    }
}


void MorningTickChartView::resetData() {
    currentVolumeMin = currentVolumeMax = 0;
    pastMinuteDataReceived = false;
    mScale = 1.0;
    mDrawHorizontalCurrentX = 0.0;
    mDrawHorizontalStartX = 0.0;
    mTransform.reset();
    priceSteps.clear();
    yesterdayMinInfo.clear();
}


void MorningTickChartView::timeInfoArrived(QDateTime dt) {
    if (!currentDateTime.isValid() || (!DataProvider::getInstance()->isSimulation() && currentDateTime != dt)) {
        //qWarning() << "(MorningTickChartView) timeInfoArrived" << dt;
        currentDateTime = dt;
        sendRequestData();
    }
}


void MorningTickChartView::sendRequestData() {
    if (!currentStockCode.isEmpty() && currentDateTime.isValid()) {
        resetData();
        DataProvider::getInstance()->requestDayData(currentStockCode, 20, currentDateTime.addDays(-1));
    }
}


void MorningTickChartView::setCurrentStock(QString code) {
    if (currentStockCode != code) {
        currentStockCode = code;
        sendRequestData();
    }
}


void MorningTickChartView::minuteTickUpdated(QString code) {
    if (currentStockCode != code || !pastMinuteDataReceived)
        return;

    MinuteTick *mt = DataProvider::getInstance()->getMinuteTick(currentStockCode);
    //qWarning() << "(minute Tick) highest : " << mt->getHighestPrice() << ", lowest" << mt->getLowestPrice() << "highest volume: " << currentVolumeMax << "\tlowest volume: " << currentVolumeMin << "\t" << mt->getHighestVolume();
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
    if (count > 0) {
        const CybosDayData &d = data->day_data(count - 1);
        QDate date = morning::Util::convertToDate(d.date());
        DataProvider::getInstance()->requestMinuteData(currentStockCode, QDateTime(date, QTime(0, 0, 0)), QDateTime(date, QTime(23, 59, 0)));
    }
}


void MorningTickChartView::calculateMinMaxRange() {
    MinuteTick *mt = DataProvider::getInstance()->getMinuteTick(currentStockCode);
    int highest = yesterdayMinInfo.getHighestPrice();
    int lowest = yesterdayMinInfo.getLowestPrice();
    uint highestVolume = yesterdayMinInfo.getHighestVolume();
    qWarning() << "(yesterday) " << highest << ", " << lowest;
    setPriceSteps(highest, lowest);

    if (mt != NULL) {
        qWarning() << "(mt) " << mt->getHighestPrice() << ", " << mt->getLowestPrice();
        if (mt->getHighestPrice() > highest)
            highest = mt->getHighestPrice();

        // Start Simulation -> Launch Tick App -> Tick is arrived first but not lowest price is calculated yet
        if (mt->getLowestPrice() != 0 && mt->getLowestPrice() < lowest)
            lowest = mt->getLowestPrice();

        if (mt->getHighestVolume() > highestVolume)
            highestVolume = mt->getHighestVolume();

        updatePriceSteps(highest, lowest);
    }


    setVolumeMinMax(highestVolume, yesterdayMinInfo.getLowestVolume());
}


void MorningTickChartView::minuteDataReceived(QString code, CybosDayDatas *data) {
    if (currentStockCode != code) 
        return;

    int count = data->day_data_size();

    qWarning() << "(minuteDataReceived) : " << count;
    if (count > 0) {
        //qWarning() << "date : " << data->day_data(0).date();
        // TODO: consider when count is 0
        yesterdayMinInfo.setData(data);
        calculateMinMaxRange();
        update();
    }
    else {
        qWarning() << "NO MINUTE DATA";
    }
    pastMinuteDataReceived = true;
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
    //qWarning() << "volume max : " << currentVolumeMax << "\tvolume min : " << currentVolumeMin;
}


void MorningTickChartView::updateVolumeMax(uint h) {
    if (h > currentVolumeMax) {
        qWarning() << "CurrentVolumeMax : " << h;
        currentVolumeMax = h;
    }
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
    QLineF lineMiddle(cw * YESTERDAY_COLUMN_COUNT, 0, cw * YESTERDAY_COLUMN_COUNT, ch * (ROW_COUNT - 2));
    painter->drawLine(lineMiddle);

    pen.setColor(QColor("#d7d7d7"));
    painter->setPen(pen);
    QLineF lineRight(cw * PRICE_COLUMN_COUNT, 0, cw * PRICE_COLUMN_COUNT, ch * (ROW_COUNT - 2));
    painter->drawLine(lineRight);
    painter->restore(); 
}


void MorningTickChartView::setPriceSteps(int h, int l) {
    qWarning() << "setPriceSteps : " << h << " " << l;
    int high = 0, low = 0;
    if (priceSteps.count() == 0) {
        high = int(h * 1.05);
        low = int(l * 0.95);
    }
    else {
        if (h == 0) {
            high = priceSteps.at(priceSteps.count() - 1);
            low = int(l * 0.95);
        }
        
        if (l == 0) {
            high = int(h * 1.05);
            low = priceSteps.at(0);
        }

        if (h != 0 && l != 0) {
            high = int(h * 1.05);
            low = int(l * 0.95);
        }
    }
    priceSteps.clear();


    int priceGap = (high - low) / PRICE_ROW_COUNT;
    qWarning() << "priceGap : " << high << " " << low << " gap: " << priceGap;
    if (priceGap < 100)
        priceGap = 10;
    else
        priceGap = 100;

    int minimumUnit = low - (low % priceGap);
    int step = (high - minimumUnit) / PRICE_ROW_COUNT;
    step = step - (step % priceGap);
    qWarning() << "minimumUnit : " << minimumUnit << " STEP : " << step << " HIGH : " << high << " SUM : " << step * PRICE_ROW_COUNT + minimumUnit;
    while (step * PRICE_ROW_COUNT + minimumUnit < high) 
        step += priceGap;
    qWarning() << "STEP 2 : " << step;

    for (int i = 0; i < PRICE_ROW_COUNT + 1; i++) 
        priceSteps.append(minimumUnit + step * i);
    qWarning() << "steps : " << priceSteps;
}


void MorningTickChartView::updatePriceSteps(int h, int l) {
    //qWarning() << "updatePriceSteps : " << h << " " << l;
    if (priceSteps.count() == 0) {
        setPriceSteps(h, l);
    }
    else {
        if (l * 0.97 < priceSteps.at(0))
            setPriceSteps(0, l);

        if (h * 1.03 > priceSteps.at(priceSteps.count() - 1)) 
            setPriceSteps(h, 0);
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
    //qWarning() << "vol diff : " << (v - currentVolumeMin) << "\tvRange : " << vRange << "\t ch : " << ch;
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
    if (data.volume() > 0) {
        qreal volumeHeight = getVolumeHeight(data.volume(), ch);
        painter->drawRect(QRectF(startX, volumeEndY - volumeHeight, tickWidth, volumeHeight));
    }
    painter->restore();
}


void MorningTickChartView::drawCandle(QPainter *painter, const CybosDayData &data, qreal startX, qreal horizontalGridStep, qreal priceChartEndY) {
    QColor color;
    painter->save();
    if (data.close_price() >= data.start_price()) {
        if (data.is_synchronized_bidding())
            color.setRgb(255, 165, 0);
        else
            color.setRgb(255, 0, 0);
    }
    else {
        if (data.is_synchronized_bidding())
            color.setRgb(173, 216, 230);
        else
            color.setRgb(0, 0, 255);
    }

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
    painter->setPen(Qt::NoPen);
    painter->drawRect(QRectF(startX, candle_y_open, horizontalGridStep, candle_y_close - candle_y_open));

    painter->restore();
}


qreal MorningTickChartView::getTimeToXPos(uint dataTime, qreal tickWidth, uint startTime) {
    QTime st(int(startTime / 100), int(startTime % 100), 0);
    QTime dt(int(dataTime / 100), int(dataTime % 100), 0);
    qreal diff = (dt.msecsSinceStartOfDay() - st.msecsSinceStartOfDay()) / 1000.0 / 180.0; // 3 min
    //qWarning() << time << "\t" << tickWidth * 2 * diff << "\t" << diff << "\t" ;//<< tickWidth * PRICE_COLUMN_COUNT / 2;
    return (tickWidth + (tickWidth * TICK_SPACE_RATIO)) * diff;
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


void MorningTickChartView::drawTimeLabels(QPainter *painter,
                                            qreal tickWidth,
                                            qreal cw, qreal ch,
                                            qreal startX,
                                            int cellCount,
                                            uint startTime) {
    painter->save();
    QPen pen;
    pen.setWidth(1);
    painter->setPen(pen);

    QTime t = QTime(startTime / 100, startTime % 100, 0);
    qreal yPos = ch * (PRICE_ROW_COUNT + TIME_LABEL_ROW_COUNT + SUBJECT_ROW_COUNT);
    for (int i = 0; i < cellCount * 2; i++) { 
        t = t.addSecs(60 * 30); // 30 min
        QString label;
        qreal xPos = getTimeToXPos(t.hour() * 100 + t.minute(), tickWidth, startTime);
        qreal lineHeight = ch / 6;
        if (t.minute() == 0) {
            label = QString::number(t.hour());
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


void MorningTickChartView::drawCurrentLineRange(QPainter *painter, MinuteTick *mt, qreal startX, const CybosDayData &data, qreal cw, qreal priceChartEndY) {
    painter->save();
    QPen pen;
    pen.setStyle(Qt::DashLine);
    pen.setWidth(1);
    if (data.is_synchronized_bidding())
        pen.setColor("#ff00ff");
    else
        pen.setColor("#ff0000");
    painter->setPen(pen);

    qreal current_y = mapPriceToPos(data.close_price(), priceChartEndY, 0);
    qreal upper_y = mapPriceToPos(data.close_price() * 1.03, priceChartEndY, 0);;
    qreal lower_y = mapPriceToPos(data.close_price() * 0.97, priceChartEndY, 0);;
    painter->drawLine(QLineF(0, current_y, cw * PRICE_COLUMN_COUNT, current_y));
    painter->drawText(int(cw * PRICE_COLUMN_COUNT + cw), int(current_y), QString::number(data.close_price()));
    pen.setColor("#90000000");
    painter->setPen(pen);
    painter->drawLine(QLineF(0, upper_y, cw * PRICE_COLUMN_COUNT, upper_y));
    painter->drawLine(QLineF(0, lower_y, cw * PRICE_COLUMN_COUNT, lower_y));

    if (mt->getYesterdayClose() != 0) {
        qreal yesterdayDiff = (int(data.close_price()) - mt->getYesterdayClose()) / (qreal)mt->getYesterdayClose() * 100.0;
        if (yesterdayDiff < 0)
            pen.setColor("#0000ff");
        else
            pen.setColor("#ff0000");
        painter->setPen(pen);
        painter->drawText(/*int(cw * PRICE_COLUMN_COUNT + cw)*/ startX + 10, int(current_y + 20), QString::number(yesterdayDiff, 'f', 1));
    }

    if (mt->getOpenPrice() != 0) {
        qreal openDiff = (int(data.close_price()) - mt->getOpenPrice()) / (qreal)mt->getOpenPrice() * 100.0;

        if (openDiff < 0) 
            pen.setColor("#0000ff");
        else
            pen.setColor("#ff0000");
        painter->setPen(pen);
        painter->drawText(/*int(cw * PRICE_COLUMN_COUNT + cw)*/ startX + 10, int(current_y - 20), QString::number(openDiff, 'f', 1));
    }

    painter->restore();
}


void MorningTickChartView::paint(QPainter *painter) {
    //qWarning() << "MorningTickChartView paint";
    //painter->setRenderHint(QPainter::Antialiasing);
    painter->setTransform(mTransform);
    QSizeF canvasSize = size();
    qreal cellHeight = canvasSize.height() / ROW_COUNT;
    qreal cellWidth = canvasSize.width() / COLUMN_COUNT;
    //qWarning() << canvasSize << "\t" << cellWidth * PRICE_COLUMN_COUNT / 2;

    drawGridLine(painter, cellWidth, cellHeight);
    if (priceSteps.count() == 0)
        return;

    drawPriceLabels(painter, canvasSize.width() - cellWidth * 2 + 10, cellHeight);
    qreal startX = 0;
    // normally 8:30 ~ 15:30 : 420 min / 3 : 140 ticks (0 ~ 10: count = 11)
    qreal todayTickCount = 141;
    qreal todaySpaceCount = todayTickCount - 1;
    // normally 9:00 ~ 15:30 : 390 min / 3 : 130 ticks
    qreal yesterdayTickCount = 131;
    qreal yesterdaySpaceCount = yesterdayTickCount - 1;

    AuxiliaryInfo aInfo(this);
    // Space width between tick is 2/3 tick width, area_width = (count + (count - 1) * 2/3) * tickWidth
    qreal todayTickWidth = cellWidth * TODAY_COLUMN_COUNT / (todayTickCount + todaySpaceCount * TICK_SPACE_RATIO);
    qreal yesterdayTickWidth = cellWidth * YESTERDAY_COLUMN_COUNT / (yesterdayTickCount + yesterdaySpaceCount * TICK_SPACE_RATIO);

    if (!yesterdayMinInfo.isEmpty()) {
        uint st = yesterdayMinInfo.get(0).time();
        drawTimeLabels(painter, yesterdayTickWidth, cellWidth, cellHeight, startX, YESTERDAY_COLUMN_COUNT, st);
        for (int i = 0; i < yesterdayMinInfo.count(); i++) {
            const CybosDayData &d = yesterdayMinInfo.get(i);
            qreal xPos = getTimeToXPos(d.time(), yesterdayTickWidth, st);
            aInfo.addPriceWithXAxis(startX + xPos, d.close_price(), d.highest_price());
            drawCandle(painter, d, startX + xPos, yesterdayTickWidth, cellHeight * PRICE_ROW_COUNT);
            drawVolume(painter, d, startX + xPos, yesterdayTickWidth, cellHeight, cellHeight * (PRICE_ROW_COUNT + VOLUME_ROW_COUNT));
        }
    }

    if (!currentStockCode.isEmpty()) {
        startX = cellWidth * YESTERDAY_COLUMN_COUNT + 1;
        MinuteTick *mt = DataProvider::getInstance()->getMinuteTick(currentStockCode);
        if (mt == NULL)
            return;

        const CybosDayDatas &queue = mt->getQueue();
        drawTimeLabels(painter, todayTickWidth, cellWidth, cellHeight, startX,
                        TODAY_COLUMN_COUNT, todayStartTime.hour() * 100 + todayStartTime.minute());
        
        for (int i = 0; i < queue.day_data_size(); i++) {
            const CybosDayData &d = queue.day_data(i);
            qreal xPos = getTimeToXPos(d.time(), todayTickWidth, todayStartTime.hour() * 100 + todayStartTime.minute());
            aInfo.addPriceWithXAxis(startX + xPos, d.close_price(), d.highest_price());
            drawCandle(painter, d, startX + xPos, todayTickWidth, cellHeight * PRICE_ROW_COUNT);
            drawVolume(painter, d, startX + xPos, todayTickWidth, cellHeight, cellHeight * (PRICE_ROW_COUNT + VOLUME_ROW_COUNT));
        }
        
        if (mt->getCurrent().start_price() != 0) {
            const CybosDayData &d = mt->getCurrent();
            qreal xPos = getTimeToXPos(d.time(), todayTickWidth, todayStartTime.hour() * 100 + todayStartTime.minute());
            drawCandle(painter, d, startX + xPos, todayTickWidth, cellHeight * PRICE_ROW_COUNT);
            drawVolume(painter, d, startX + xPos, todayTickWidth, cellHeight, cellHeight * (PRICE_ROW_COUNT + VOLUME_ROW_COUNT));
            aInfo.addPriceWithXAxis(startX + xPos, d.close_price(), d.highest_price());
            drawCurrentLineRange(painter, mt, startX + xPos, d, cellWidth, cellHeight * PRICE_ROW_COUNT);
        }
    }

    aInfo.drawAverageLine(painter, cellHeight * PRICE_ROW_COUNT);

    if (mDrawHorizontalStartX > 0 && mDrawHorizontalCurrentX > 0 &&
        mDrawHorizontalStartX < cellWidth * PRICE_COLUMN_COUNT &&
        mDrawHorizontalCurrentX < cellWidth * PRICE_COLUMN_COUNT)
        aInfo.drawCandleSelection(painter, mDrawHorizontalStartX, mDrawHorizontalCurrentX, cellHeight * PRICE_ROW_COUNT);
}
