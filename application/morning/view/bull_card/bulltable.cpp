#include "bulltable.h"

#include <QHeaderView>
#include <QStyledItemDelegate>
#include <QStyleOptionViewItem>
#include <QSize>
#include <QPainter>
#include "stock_server/data_provider.h"
#include "view/bull_card/bullmodel.h"
#include <QDebug>


class CardItemDelegate : public QStyledItemDelegate {
public:
    CardItemDelegate() : QStyledItemDelegate() {

    }

    QSize sizeHint(const QStyleOptionViewItem &option, const QModelIndex &index) const override{
        return QSize(200, 130);
        //return QStyledItemDelegate::sizeHint(option, index);
    }
    
    void paint(QPainter *painter, const QStyleOptionViewItem & vitem, const QModelIndex &index) const override{
        const BullModel * model = qobject_cast<const BullModel *>(index.model());
        QString code = model->getCode(index.row(), index.column());
        if (code.length() > 0) {
            painter->save();
            QRect rect = vitem.rect;
            QString companyName = model->getCompanyName(code);
            QPixmap * pixmap = model->createTickChart(code, 30000);
            painter->drawPixmap(QRectF(rect.x(), rect.y(), 200, 100), *pixmap, QRect(0, 0, 200, 100));
            
            double profit = model->getCurrentProfit(code);
            QString profitStr = QString::number(profit, 'f', 2);
            QPen profitPen = painter->pen();
            if (profit > 0)
                profitPen.setColor(QColor(Qt::red));
            else
                profitPen.setColor(QColor(Qt::blue));

            painter->setPen(profitPen);
            painter->drawText(QRectF(rect.x(), rect.y() + 100, 50, 10), Qt::AlignCenter, profitStr);

            painter->fillRect(QRectF(rect.x() + 50, rect.y() + 100, 150, 10), QBrush(Qt::blue));
            painter->drawText(QRectF(rect.x(), rect.y() + 110, 200, 20), Qt::AlignCenter, companyName + " - " + code);
            painter->restore();
        }
        else {
            QStyledItemDelegate::paint(painter, vitem, index);
        }
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
