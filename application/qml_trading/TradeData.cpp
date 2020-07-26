#include "TradeData.h"
#include <google/protobuf/util/time_util.h>


using google::protobuf::util::TimeUtil;


TradeData::TradeData() {
    mCurrentPrice = 0;
}


bool TradeData::isMatched(const QString &orderNum, const QString &internalOrderNum) {
    if (mOrderNum == orderNum || mInternalOrderNum == internalOrderNum)
        return true;

    return false;
}


void TradeData::setData(const Report &r) {
    mInternalOrderNum = QString::fromStdString(r.internal_order_num());
    mOrderNum = QString::fromStdString(r.order_num());
    mCompanyName = QString::fromStdString(r.company_name());
    mCode = QString::fromStdString(r.code());
    mIsBuy = r.is_buy();
    mFlag = r.flag();
    mMethod = r.method();
    mHoldPrice = r.hold_price();
    mPrice = r.price();
    mQuantity = r.quantity();
    long msec = TimeUtil::TimestampToMilliseconds(r.last_update_datetime());
    mLastUpdateTime = QDateTime::fromMSecsSinceEpoch(msec);
}


bool TradeData::updateData(const Report &r) {
    mInternalOrderNum = QString::fromStdString(r.internal_order_num());
    mOrderNum = QString::fromStdString(r.order_num());
    mCompanyName = QString::fromStdString(r.company_name());
    mCode = QString::fromStdString(r.code());
    mIsBuy = r.is_buy();
    mFlag = r.flag();
    mMethod = r.method();
    mHoldPrice = r.hold_price();
    mPrice = r.price();
    mQuantity = r.quantity();
    long msec = TimeUtil::TimestampToMilliseconds(r.last_update_datetime());
    mLastUpdateTime = QDateTime::fromMSecsSinceEpoch(msec);
    return true;
}


QString TradeData::flagToString(OrderStatusFlag flag) const {
    switch(flag) {
    case OrderStatusFlag::STATUS_UNKNOWN:
        return QString("*");
    case OrderStatusFlag::STATUS_REGISTERED:
        return QString("등록");
    case OrderStatusFlag::STATUS_SUBMITTED:
        return QString("접수");
    case OrderStatusFlag::STATUS_TRADED:
        return QString("체결");
    case OrderStatusFlag::STATUS_DENIED:
        return QString("거절");
    case OrderStatusFlag::STATUS_CONFIRM:
        return QString("확인");
    case OrderStatusFlag::STATUS_AUTO_CUT:
        return QString("손절");
    default: break;
    }
    return QString("-");
}

QString TradeData::methodToString(OrderMethod method) const {
    switch(method) {
    case OrderMethod::TRADE_UNKNOWN:
        return QString("*");
    case OrderMethod::TRADE_IMMEDIATELY:
        return QString("IMM");
    case OrderMethod::TRADE_ON_BID_ASK_MEET:
        return QString("BA_MEET");
    case OrderMethod::TRADE_ON_PRICE:
        return QString("ON_PRICE");
    default: break;
    }
    return "-";
}


QVariant TradeData::getCurrentProfit() const {
    if (mCurrentPrice == 0 || mHoldPrice == 0)
        return QVariant(0);

    float profit = (mCurrentPrice - mHoldPrice) / float(mHoldPrice) * 100.0;
    return QVariant(profit);
}


QVariant TradeData::getDisplayData(int column) const {
    switch(column) {
    case 0:  return mCompanyName;
    case 1:  return (mIsBuy? "매수":"매도");
    case 2:  return QVariant(mCurrentPrice);
    case 3:  return QVariant(mHoldPrice);
    case 4:  return getCurrentProfit(); // hold_profit
    case 5:  return flagToString(mFlag);
    case 6:  return methodToString(mMethod);
    case 7:  return QVariant(mPrice);
    case 8:  return QVariant(mQuantity);
    case 9: return "ACTION";
    case 10:  return mCode;
    case 11: return (mOrderNum.length() > 0 ?mOrderNum:mInternalOrderNum);
    case 12: return mLastUpdateTime.toString("hh:mm");
    default: break;
    }
    return QVariant();
}
