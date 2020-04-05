#include "bullmodel.h"
#include "stock_model/stockmodel.h"


#define TABLE_ROW_COUNT     10
#define TABLE_COLUMN_COUNT  6


BullModel::BullModel(StockModel &model, QObject *p)
: QAbstractTableModel(p), stockModel(model) {
    currentUpdateColumn = 0;
}


BullModel::~BullModel() {}


int BullModel::rowCount(const QModelIndex &p) const {
    return TABLE_ROW_COUNT;
}


int BullModel::columnCount(const QModelIndex &p) const {
    return TABLE_COLUMN_COUNT;
}


void BullModel::refresh() {
    currentUpdateColumn = 0;
    // Call update model
}


QVariant BullModel::data(const QModelIndex &index, int role) const {
    if (!index.isValid()) 
        return QVariant();
    else if (role == Qt::DisplayRole) 
        return "Hello World";

    return QVariant(); 
}
