#ifndef BULL_MODEL_H_
#define BULL_MODEL_H_

#include <QObject>
#include <QVariant>
#include <QAbstractTableModel>
#include <QModelIndex>


class StockModel;


class BullModel : public QAbstractTableModel {
Q_OBJECT
public:
    BullModel(StockModel &model, QObject * p=0);
    ~BullModel();

    int rowCount(const QModelIndex &parent=QModelIndex()) const;
    int columnCount(const QModelIndex &parent=QModelIndex()) const;
    QVariant data(const QModelIndex & index, int role) const;
    void refresh();

private:
    StockModel &stockModel;
    int currentUpdateColumn;
};


#endif
