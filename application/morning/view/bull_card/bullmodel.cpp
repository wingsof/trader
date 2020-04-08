#include "bullmodel.h"
#include "stock_model/stockmodel.h"
#include "stock_server/data_provider.h"
#include <QVector>


#define TABLE_ROW_COUNT     10
#define TABLE_COLUMN_COUNT  6


BullModel::BullModel(StockModel &model, QObject *p)
: QAbstractTableModel(p), stockModel(model) {
    connect((QObject *)stockModel.getProvider().getChooser(), SIGNAL(codePicked(QStringList)), SLOT(codePicked(QStringList)));
}


BullModel::~BullModel() {}


int BullModel::rowCount(const QModelIndex &p) const {
    return TABLE_ROW_COUNT;
}


int BullModel::columnCount(const QModelIndex &p) const {
    return TABLE_COLUMN_COUNT;
}


void BullModel::next() {
    if (codeCandidates.count() > TABLE_COLUMN_COUNT) {
        QStringList codes = codeCandidates.at(0);
        codeCandidates.removeFirst();

        for (int i = 0; i < codes.count(); ++i)
            allCodes.removeAll(codes.at(i));

        emit dataChanged(createIndex(0, 0), createIndex(TABLE_ROW_COUNT - 1, TABLE_COLUMN_COUNT - 1));
    }
}


void BullModel::refresh() {
    emit layoutAboutToBeChanged();
    codeCandidates.clear();
    allCodes.clear();
    emit dataChanged(createIndex(0, 0), createIndex(TABLE_ROW_COUNT - 1, TABLE_COLUMN_COUNT - 1));
    emit layoutChanged();
}


QString BullModel::getCode(int row, int column) const{
    if (column < codeCandidates.count() and row < codeCandidates.at(column).count()) {
        return codeCandidates.at(column).at(row);
    }
    return QString();
}


QString BullModel::getCompanyName(const QString &code) const {
    return stockModel.getCompanyName(code);
}


double BullModel::getCurrentProfit(const QString &code) const {
    return stockModel.getCurrentProfit(code);
}


QPixmap * BullModel::createTickChart(const QString &code, int beforeDuration) const {
    return stockModel.createTickChart(code, beforeDuration);
}


void BullModel::codePicked(QStringList codes) {
    if (codes.isEmpty())
        return;

    QStringList newGroup;
    for (int i = 0; i < codes.count(); ++i) {
        if (!allCodes.contains(codes.at(i))) {
            newGroup << codes.at(i);
            allCodes << codes.at(i);
        }
    }

    if (newGroup.isEmpty())
        return;

    codeCandidates.append(newGroup);

    if (codeCandidates.count() < TABLE_COLUMN_COUNT) {
        int updateColumn = codeCandidates.count() - 1;
        QVector<int> roles;
        roles.append(Qt::DisplayRole);
        emit dataChanged(createIndex(0, updateColumn), createIndex(TABLE_ROW_COUNT - 1, updateColumn), roles);
    }
}


QVariant BullModel::data(const QModelIndex &index, int role) const {
    if (!index.isValid()) 
        return QVariant();
    else if (role == Qt::TextAlignmentRole) 
        return Qt::AlignCenter;
    else if (role == Qt::DisplayRole) {
        QString code = getCode(index.row(), index.column());
        if (code.length() > 0)
            return code;
    }

    return QVariant(); 
}
