#include "bulltable.h"

#include <QHeaderView>
#include <QStyledItemDelegate>
#include <QStyleOptionViewItem>
#include <QSize>
#include <QDebug>


class CardItemDelegate : public QStyledItemDelegate {
public:
    CardItemDelegate() : QStyledItemDelegate() {

    }

    QSize sizeHint(const QStyleOptionViewItem &option, const QModelIndex &index) const override{
        return QSize(200, 300);
        //return QStyledItemDelegate::sizeHint(option, index);
    }
    
    void paint(QPainter *painter, const QStyleOptionViewItem & vitem, const QModelIndex &index) const override{
        QStyledItemDelegate::paint(painter, vitem, index);
    }
};


BullTable::BullTable(QWidget *p)
: QTableView(p) {
    setGridStyle(Qt::NoPen);
    //horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    //verticalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    horizontalHeader()->hide();
    verticalHeader()->hide();

    horizontalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);
    verticalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);
    resizeRowsToContents();
    resizeColumnsToContents();
    delegate = new CardItemDelegate;
    setItemDelegate(delegate);
}


BullTable::~BullTable() {}
