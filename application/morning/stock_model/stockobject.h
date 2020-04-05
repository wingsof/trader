#ifndef STOCK_OBJECT_H_
#define STOCK_OBJECT_H_


#include <QObject>


class StockObject {
Q_OBJECT
public:
    enum class Type { STOCK_TICK, BIDASK_TICK, SUBJECT_TICK, DAY_DATA, MINUTE_DATA };
};


#endif
