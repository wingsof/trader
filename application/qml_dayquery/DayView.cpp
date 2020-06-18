#include "DayView.h"
#include "DayDataProvider.h"
#include "StockSelectionThread.h"
#include "TickThread.h"
#include <QDebug>

DayView::DayView(QQuickItem *parent) : QQuickPaintedItem(parent) {
    qWarning() << "DayView constructor";
    dayData = new DayData;
    provider = new DayDataProvider;
    stockSelector = new StockSelectionThread(provider->getStub());
    tickThread = new TickThread(provider->getStub());

    connect(stockSelector, &StockSelectionThread::stockCodeChanged, this, &DayView::searchReceived);
    connect(provider, &DayDataProvider::dataReady, this, &DayView::dataReceived);
    connect(tickThread, &TickThread::tickArrived, this, &DayView::tickDataArrived);
    stockSelector->start();
    tickThread->start();
}


void DayView::searchReceived(QString code, QDateTime untilTime, int countOfDays) {
    search(code, untilTime, countOfDays);
}


void DayView::setStockCode(QString code) {
    qWarning() << "setStockCode " << code;
    if (code != stockCode) {
        code = stockCode;
        emit stockCodeChanged();
    }
}


void DayView::setCountDays(int count) {
    qWarning() << "setCountDays " << count;
    countDays = count;
    emit countDaysChanged();
}


void DayView::setUntilTime(QDateTime dt) {
    qWarning() << "setUntilTime " << dt;
    untilTime = dt;
    emit untilTimeChanged();
}


void DayView::search(QString _stockCode, QDateTime _untilTime, int _countDays) {
    if (stockCode != _stockCode ||
            countDays != _countDays ||
            untilTime != _untilTime) {
        stockCode = _stockCode;
        countDays = _countDays;
        untilTime = _untilTime;
        provider->requestDayData(stockCode, countDays, untilTime);     
        qWarning() << "search " << _stockCode << " " << _countDays << " " << _untilTime;
    }
}


void DayView::dataReceived(QString code, CybosDayDatas *datas) {
    dayData->setData(code, datas);
    update();
}

 
void DayView::fillBackground(QPainter *painter, const QSizeF &itemSize) {
    painter->save();
    QBrush brush(QColor("#FFFFFF"));
    painter->setBrush(brush);
    painter->setPen(Qt::NoPen);
    painter->drawRect(0, 0, itemSize.width(), itemSize.height());
    painter->restore();
}


void DayView::drawGridLine(QPainter *painter, const QSizeF &itemSize, qreal lineVerticalSpace, qreal endX, int spaceCount) {
    painter->save();
    QPen pen = painter->pen();
    pen.setWidth(1);
    pen.setColor(QColor("#d7d7d7"));
    painter->setPen(pen);
   
    for (int i = 1; i < spaceCount; i++) { // skip to draw first line
        QLineF line(0, lineVerticalSpace * i, endX, lineVerticalSpace * i);
        painter->drawLine(line);
    }

    painter->drawLine(QLineF(endX, 0, endX, lineVerticalSpace * 8));
    painter->restore();
}


void DayView::drawPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace) {
    painter->save();
    painter->setPen(Qt::NoPen);
    painter->setBrush(QBrush(QColor("#64ffff00")));
    for (int i = 0; i < DayData::PRICE_STEPS; i++) {
        qreal w = dayData->getVolumeStepWidth(i, dWidth);
        painter->drawRect(QRectF(startX, priceChartEndY - (priceHeightSpace * (i + 1)), w, priceHeightSpace));
    }
    painter->restore();
}


void DayView::drawForeignerPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace) {
    painter->save();
    painter->setPen(Qt::NoPen);
    for (int i = 0; i < DayData::PRICE_STEPS; i++) {
        qreal w = dayData->getForeignerStepWidth(i, dWidth);
        QColor volumeColor;
        if (w >= 0) 
            volumeColor.setNamedColor("#34ff0000");
        else
            volumeColor.setNamedColor("#340000ff");
        painter->setBrush(QBrush(volumeColor));
        painter->drawRect(QRectF(startX, priceChartEndY - (priceHeightSpace * (i + 1)), w, priceHeightSpace));
    }
    painter->restore();
}



void DayView::drawInstitutionPriceDistribution(QPainter *painter, qreal startX, qreal dWidth, qreal priceChartEndY, qreal priceHeightSpace) {
    painter->save();
    painter->setPen(Qt::NoPen);
    for (int i = 0; i < DayData::PRICE_STEPS; i++) {
        qreal w = dayData->getInstitutionStepWidth(i, dWidth);
        QColor volumeColor;
        if (w >= 0) 
            volumeColor.setNamedColor("#34ff0000");
        else
            volumeColor.setNamedColor("#340000ff");
        painter->setBrush(QBrush(volumeColor));
        painter->drawRect(QRectF(startX, priceChartEndY - (priceHeightSpace * (i + 1)), w, priceHeightSpace));
    }
    painter->restore();
}


void DayView::drawPriceLabels(QPainter *painter, qreal startX, qreal priceChartEndY, qreal priceHeightSpace) {
    painter->save();
    QPen pen = painter->pen();
    pen.setColor(QColor("#000000"));
    painter->setPen(pen);
    const QList<int> & priceLabels = dayData->getPriceSteps();

    for (int i = 0; i < priceLabels.count() - 1; i++) {
        painter->drawText((int)startX, (int)(priceChartEndY - priceHeightSpace * i),
                            QString::number(priceLabels.at(i)));
    }
    painter->restore();
}


void DayView::drawCandle(QPainter *painter, const CybosDayData *data, qreal startX, qreal horizontalGridStep, qreal priceChartEndY) {
    QColor color;
    painter->save();
    if (data->close_price() >= data->start_price()) 
        color.setRgb(255, 0, 0);
    else 
        color.setRgb(0, 0, 255);
    QPen pen = painter->pen();
    painter->setBrush(QBrush(color));
    pen.setColor(color);

    qreal penWidth = getCandleLineWidth(horizontalGridStep);
    pen.setWidthF(penWidth);
    painter->setPen(pen);
    qreal candle_y_low = dayData->mapPriceToPos(data->lowest_price(), priceChartEndY, 0);
    qreal candle_y_high = dayData->mapPriceToPos(data->highest_price(), priceChartEndY, 0);
    qreal candle_y_open = dayData->mapPriceToPos(data->start_price(), priceChartEndY, 0);
    qreal candle_y_close = dayData->mapPriceToPos(data->close_price(), priceChartEndY, 0);

    qreal line_x = startX + (horizontalGridStep / 2);
    painter->drawLine(QLineF(line_x, candle_y_high, line_x, candle_y_low));
    painter->drawRect(QRectF(startX, candle_y_open, horizontalGridStep, candle_y_close - candle_y_open));

    painter->restore();
}


qreal DayView::drawVolume(QPainter *painter, const CybosDayData *data, qreal startX, qreal horizontalGridStep, qreal volumeEndY, qreal priceChartEndY, bool divideBuySell) {
    painter->save();
    qreal volume_bar_y = dayData->mapVolumeToPos(data->volume(), volumeEndY, priceChartEndY);

    if (divideBuySell) {
        qreal sell_volume_bar_height = dayData->getSellVolumeHeight(*data, volumeEndY - volume_bar_y);
        painter->setBrush(Qt::NoBrush);
        QPen pen;
        pen.setColor("#0000ff");
        painter->setPen(pen);
        painter->drawRect(QRectF(startX, volume_bar_y, horizontalGridStep, sell_volume_bar_height));
        pen.setColor(Qt::red);
        painter->setPen(pen);
        painter->drawRect(QRectF(startX, volume_bar_y + sell_volume_bar_height, horizontalGridStep, volumeEndY - volume_bar_y - sell_volume_bar_height));
    }
    else {
        painter->setBrush(QBrush(QColor("#ff0000")));
        painter->drawRect(QRectF(startX, volume_bar_y, horizontalGridStep, volumeEndY - volume_bar_y));
    }
    painter->restore();
    return volume_bar_y;
}


void DayView::paint(QPainter *painter) {
    QSizeF itemSize = size();
    int horizontalLineCount = 18;
    qreal verticalGridStep = itemSize.height() / horizontalLineCount;
    qreal priceLabelWidth = itemSize.width() / 10;
    qreal distributionWidth = (itemSize.width() - priceLabelWidth) / 3;

    painter->setRenderHint(QPainter::Antialiasing);

    fillBackground(painter, itemSize);
    drawGridLine(painter, itemSize, verticalGridStep * 2, itemSize.width() - priceLabelWidth,
                        (int)(horizontalLineCount / 2));

    if (!dayData->hasData() || dayData->countOfData() == 0)
        return;

    qreal priceEndY = verticalGridStep * 2 * 6; // price chart end Y
    drawPriceDistribution(painter, 0.0, distributionWidth, priceEndY, verticalGridStep);
    drawForeignerPriceDistribution(painter, distributionWidth, distributionWidth, priceEndY, verticalGridStep);
    drawInstitutionPriceDistribution(painter, distributionWidth * 2, distributionWidth, priceEndY, verticalGridStep);
    drawPriceLabels(painter, itemSize.width() - priceLabelWidth + 10, priceEndY, verticalGridStep);

    qreal volumeEndY = verticalGridStep * 2 * 7;

    int dataCount = dayData->countOfData() + 1; // prepare today (+1)
    if (dataCount < 30)
        dataCount = 30;

    // to draw 30 candle, 30 space for candle and 29 space for spacing between candle required
    qreal horizontalGridStep = (itemSize.width() - priceLabelWidth) / (dataCount * 2 - 1);

    // horizontalGridStep * 3 is for spacing to draw today data
    qreal startX = (itemSize.width() - priceLabelWidth) - horizontalGridStep * 3;

    QColor color;
    int currentDayOfWeek = 8; // 1 to 7 (Mon to Sun)
    int currentMonth = -1;
    for (int i = dayData->countOfData() - 1; i >= 0; i--) {
        const CybosDayData &data = dayData->getDayData(i);
        QDate d = dayData->convertToDate(data.date());

        if (currentMonth == -1)
            currentMonth = d.month();

        QPen pen;
        pen.setWidth(1);
        pen.setColor(QColor("#d7d7d7"));
        painter->setPen(pen);

        if (d.dayOfWeek() > currentDayOfWeek) {
            painter->drawLine(QLineF(startX + horizontalGridStep + horizontalGridStep / 2, 0, startX + horizontalGridStep + horizontalGridStep / 2, verticalGridStep * 2 * 8));
            const CybosDayData &previousData = dayData->getDayData(i + 1);
            QDate previousDate = dayData->convertToDate(previousData.date());
            QPen fPen(QColor("#000000"));
            painter->setPen(fPen);
            painter->drawText(QRectF(startX + horizontalGridStep * 2, verticalGridStep * 2 * 8, horizontalGridStep * 8, verticalGridStep), Qt::AlignLeft | Qt::AlignVCenter, previousDate.toString("M/dd"));
        }

        currentDayOfWeek = d.dayOfWeek();

        drawCandle(painter, &data, startX, horizontalGridStep, priceEndY);
        qreal volume_bar_y = drawVolume(painter, &data, startX, horizontalGridStep, volumeEndY, priceEndY, true);

        if (i - 1 >= 0) {
            qreal foreigner_volume_height = dayData->getForeignerBuyHeight(data, dayData->getDayData(i-1), volumeEndY - volume_bar_y);
            qreal institution_volume_height = dayData->getInstitutionBuyHeight(data, volumeEndY - volume_bar_y);
            // 4 cases: ++, +-, -+, --
            painter->setPen(Qt::NoPen);
            painter->setBrush(QBrush(Qt::green));
            painter->drawRect(QRectF(startX, volumeEndY - foreigner_volume_height, horizontalGridStep, foreigner_volume_height));

            painter->setBrush(QBrush(Qt::magenta));
            if (foreigner_volume_height * institution_volume_height < 0) 
                painter->drawRect(QRectF(startX, volumeEndY - institution_volume_height, horizontalGridStep, institution_volume_height));
            else 
                painter->drawRect(QRectF(startX, volumeEndY - foreigner_volume_height - institution_volume_height, horizontalGridStep, institution_volume_height));
        }
        currentMonth = d.month();
        startX -= horizontalGridStep * 2;
    }

    if (dayData->getTodayData()->close_price() != 0) {
        drawCandle(painter, dayData->getTodayData(), itemSize.width() - priceLabelWidth - horizontalGridStep, horizontalGridStep, priceEndY);
        QPen pen;
        pen.setColor("#ff0000");
        pen.setWidth(1);
        pen.setStyle(Qt::DashLine);
        painter->setPen(pen);
        qreal current_y = dayData->mapPriceToPos(dayData->getTodayData()->close_price(),
                                                priceEndY, 0);
        painter->drawLine(QLineF(0, current_y, itemSize.width() - priceLabelWidth, current_y));
        drawVolume(painter, dayData->getTodayData(), itemSize.width() - priceLabelWidth - horizontalGridStep, horizontalGridStep, volumeEndY, priceEndY, false);
        pen.setColor(QColor("#ff0000"));
        painter->setPen(pen);
        painter->drawText((int)itemSize.width() - priceLabelWidth + 50, 
                                (int)current_y,
                                 QString::number(dayData->getTodayData()->close_price()));
    }
}


qreal DayView::getCandleLineWidth(qreal w) {
    if (w * 0.2 < 1.0)
        return 1.0;
    return (int)w * 0.2;
}


void DayView::tickDataArrived(CybosTickData *data) {
    if (!dayData->hasData() || dayData->countOfData() == 0)
        return;

    if (QString::fromStdString(data->code()) == stockCode &&
            data->market_type() == 50) {
        dayData->setTodayData(data->start_price(),
                                data->highest_price(),
                                data->lowest_price(),
                                data->current_price(),
                                data->cum_volume());
        update();
    }
}


DayData::DayData() : data(NULL) {
    todayData = new CybosDayData;
    todayData->set_close_price(0);        
}


DayData::~DayData() {
    delete todayData;
}


bool DayData::hasData() {
    if (data != NULL)
        return true;

    return false;
}


void DayData::setTodayData(int o, int h, int l, int c, unsigned long v) {
    todayData->set_start_price(o);
    todayData->set_highest_price(h);
    todayData->set_lowest_price(l);
    todayData->set_close_price(c);
    todayData->set_volume(v);
}


void DayData::setData(QString _code, CybosDayDatas *dayData) {
    code = _code;

    if (data != NULL) {
        data->clear_day_data();
        delete data;
    }
    data = dayData;
    qWarning() << "setData count : " << data->day_data_size();
    if (data->day_data_size() == 0)
        return;

    lowestPrice = data->day_data(0).lowest_price();
    highestPrice = data->day_data(0).highest_price();
    lowestVolume = data->day_data(0).volume();
    highestVolume = lowestVolume;
    for (int i = 1; i < data->day_data_size(); i++) {
        if (data->day_data(i).lowest_price() < lowestPrice) 
            lowestPrice = data->day_data(i).lowest_price();

        if (data->day_data(i).highest_price() > highestPrice)
            highestPrice = data->day_data(i).highest_price();

        if (data->day_data(i).volume() > highestVolume)
            highestVolume = data->day_data(i).volume();

        if (data->day_data(i).volume() < lowestVolume)
            lowestVolume = data->day_data(i).volume();
        //qWarning() << data->day_data(i).date() << "\tvolume:" << data->day_data(i).volume() << "\tfhold:" << data->day_data(i).foreigner_hold_volume() << "\tibuy:" << data->day_data(i).institution_buy_volume() << "\ticum_buy:" << data->day_data(i).institution_cum_buy_volume() << "\tfhold_rate:" << data->day_data(i).foreigner_hold_rate() << "\tcum_buy:" << data->day_data(i).cum_buy_volume() << "\tcum_sell" << data->day_data(i).cum_sell_volume();
    }
    setPriceSteps(lowestPrice, highestPrice);
    setPPS();
}


void DayData::setPPS() {
    for (int i = 0; i < data->day_data_size(); i++) {
        const CybosDayData &d = data->day_data(i);
        int averagePrice = (d.lowest_price() + d.highest_price() + d.start_price() + d.close_price()) / 4;
        int index = getIndexOfPriceSteps(averagePrice);
        if (index < 0) {
            qWarning() << "Cannot find PPS index, price: " << averagePrice << "\t steps: " << priceSteps;
            continue;
        }
        volumePPS[index] += d.volume();
        institutionPPS[index] += d.institution_buy_volume();

        if (i == 0)
            continue;

        const CybosDayData &prev = data->day_data(i-1);
        foreignerPPS[index] += d.foreigner_hold_volume() - prev.foreigner_hold_volume();
    }
}


int DayData::getIndexOfPriceSteps(int price) {
    for (int i = 0; i < priceSteps.count() - 1; i++) {
        if (price >= priceSteps.at(i) && price < priceSteps.at(i+1))
            return i;
    }
    return -1;
}


void DayData::setPriceSteps(int l, int h) {
    priceSteps.clear();
    volumePPS.clear();
    foreignerPPS.clear();
    institutionPPS.clear();

    //const int PRICE_STEPS = 12;
    int priceGap = (h - l) / 10;
    if (priceGap < 100)
        priceGap = 10;
    else
        priceGap = 100;

    int minimumUnit = l - (l % priceGap);
    int step = (h - minimumUnit) / 10;
    step = step - (step % priceGap);
    while (step * PRICE_STEPS + minimumUnit < h) 
        step += 5;

    for (int i = 0; i < PRICE_STEPS + 1; i++) 
        priceSteps.append(minimumUnit + step * i);

    for (int i = 0; i < PRICE_STEPS; i++) {
        volumePPS.append(0);
        foreignerPPS.append(0);
        institutionPPS.append(0);
    }
}


int DayData::countOfData() {
    if (data != NULL)
        return data->day_data_size();

    return 0;
}


qreal DayData::mapPriceToPos(int price, qreal startY, qreal endY) {
    qreal priceGap = priceSteps.at(priceSteps.size() - 1) - priceSteps.at(0); 
    qreal positionGap = startY - endY; // device coordinate zero is started from upper
    qreal pricePosition = price - lowestPrice;
    qreal result = startY - pricePosition * positionGap / priceGap;
    //qWarning() << "price : " << price << ", gap: " << priceGap << ", price pos: " << pricePosition << ", " << "Y : " << startY << ", " << endY << "\tresult : " << result;
    return result;
}

qreal DayData::mapVolumeToPos(unsigned long volume, qreal startY, qreal endY) {
    qreal positionGap = startY - endY;
    qreal bottomVolume = lowestVolume * 0.8; // to prevent lowest volume cannot be represented
    if (volume < bottomVolume)
        return startY;   
    
    qreal volumePosition = volume - bottomVolume;
    qreal volumeGap = highestVolume - bottomVolume;
    qreal result = startY - positionGap * volumePosition / volumeGap;
    return result;
}


qreal DayData::getSellVolumeHeight(const CybosDayData &data, qreal h) {
    unsigned long vol_sum = data.cum_buy_volume() + data.cum_sell_volume();
    return h * data.cum_sell_volume() / (qreal) vol_sum;
}


qreal DayData::getForeignerBuyHeight(const CybosDayData & data, const CybosDayData &prev, qreal h) {
    long diff = data.foreigner_hold_volume() - prev.foreigner_hold_volume();
    return h * diff / data.volume();
}


qreal DayData::getInstitutionBuyHeight(const CybosDayData & data, qreal h) {
    return h * data.institution_buy_volume() / data.volume();
}


qreal DayData::getVolumeStepWidth(int i, qreal w) {
    unsigned long volume_sum = 0;
    for (int j = 0; j < volumePPS.count(); j++) 
        volume_sum += volumePPS.at(j);

    return w * volumePPS.at(i) / volume_sum;
}


qreal DayData::getForeignerStepWidth(int i, qreal w) {
    unsigned long max_volume = 0;
    for (int j = 0; j < foreignerPPS.count(); j++) {
        if (qAbs(foreignerPPS.at(j)) > max_volume)
            max_volume = qAbs(foreignerPPS.at(j));
    }
    unsigned long volume_range = max_volume * 2;
    return w * foreignerPPS.at(i) / volume_range;
}


qreal DayData::getInstitutionStepWidth(int i, qreal w) {
    unsigned long max_volume = 0;
    for (int j = 0; j < institutionPPS.count(); j++) {
        if (qAbs(institutionPPS.at(j)) > max_volume)
            max_volume = qAbs(institutionPPS.at(j));
    }
    unsigned long volume_range = max_volume * 2;
    return w * institutionPPS.at(i) / volume_range;
}


const CybosDayData & DayData::getDayData(int i) {
    if (countOfData() <= i) {
        return CybosDayData();
    }
    return data->day_data(i);
}


const QList<int> & DayData::getPriceSteps() {
    return priceSteps;
}


CybosDayData *DayData::getTodayData() {
    return todayData;
}


QDate DayData::convertToDate(unsigned int d) {
    unsigned int year = d / 10000;
    unsigned int month = d % 10000 / 100;
    unsigned int day = d % 100;
    return QDate(year, month, day);
}
