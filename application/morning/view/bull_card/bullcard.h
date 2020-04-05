#ifndef BULL_CARD_H_
#define BULL_CARD_H_


#include <QWidget>
#include "stock_model/stockmodel.h"

class BullTable;
class BullModel;

class BullCard : public QWidget {
Q_OBJECT
public:
    explicit BullCard(StockModel & _model, QWidget *p=0);
    ~BullCard();

private:
    StockModel & model;
    BullTable * table;
    BullModel * bullmodel;
    int currentUpdateColumn;

public slots:
    void refresh();
    void next();
};


#endif
