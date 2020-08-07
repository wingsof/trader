#ifndef BULL_TABLE_H_
#define BULL_TABLE_H_


#include <QTableView>


class CardItemDelegate;


class BullTable : public QTableView {
Q_OBJECT
public:
    BullTable(QWidget *p=0);
    ~BullTable();

private:
    CardItemDelegate * delegate;
};


#endif
