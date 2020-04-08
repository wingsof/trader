#include "topamount.h"
#include "../../stock_object.h"
#include "util/morning_timer.h"
#include "stock_server/time_info.h"
#include <QtAlgorithms>
#include <QDebug>


#define PICK_TIME_MSEC   10000


TopAmount::TopAmount(QMap<QString, StockObject *> *_obj, QObject *p)
: ChooserPlugin(_obj, p){
    pickTimer = new MorningTimer(PICK_TIME_MSEC, this);
    connect(pickTimer, SIGNAL(timeout()), SLOT(pick()));
}


TopAmount::~TopAmount() {}


void TopAmount::start() {
    pickTimer->start();
}


void TopAmount::pick() {
    qWarning() << "Pick";
    struct Candidates {
        QString code;
        unsigned long amount;
    };
    QMapIterator<QString, StockObject *> i(*(getStockObj()));
    QList<Candidates> candidates;
    while (i.hasNext()) {
        i.next();
        StockObject *stockObj = i.value();
        QList<StockObject::PeriodTickData *> ptd = stockObj->getPeriodData(TimeInfo::getInstance().getCurrentDateTime(), PICK_TIME_MSEC);
        Candidates c;
        unsigned long amount = 0;
        QListIterator<StockObject::PeriodTickData *> j(ptd);
        while (j.hasNext()) {
            amount += j.next()->amount;
        }
        c.code = stockObj->getCode();
        c.amount = amount;
        candidates.append(c);
    }

    auto amountLessThan = [](const Candidates &c1, const Candidates &c2) {
        return c1.amount < c2.amount;
    };

    QStringList codes;
    qSort(candidates.begin(), candidates.end(), amountLessThan);
    

    QList<Candidates>::reverse_iterator k;
    for (k = candidates.rbegin(); k != candidates.rend(); ++k) {
        codes.append((*k).code);
        qWarning() << "picked: " << (*k).code << ", amount: " << (*k).amount;
    }
    emit codePicked(codes);
}
