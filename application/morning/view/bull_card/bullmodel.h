#ifndef BULL_MODEL_H_
#define BULL_MODEL_H_

#include <QObject>
#include <QVariant>
#include <QAbstractTableModel>
#include <QModelIndex>
#include <QStringList>


class StockModel;
class StockObject;


class BullModel : public QAbstractTableModel {
Q_OBJECT
public:
    BullModel(StockModel &model, QObject * p=0);
    ~BullModel();

    int rowCount(const QModelIndex &parent=QModelIndex()) const;
    int columnCount(const QModelIndex &parent=QModelIndex()) const;
    QVariant data(const QModelIndex & index, int role) const;
    void refresh();
    void next();

    QString getCode(int row, int column) const;
    QString getCompanyName(const QString &code) const;
    double getCurrentProfit(const QString &code) const;
    QPixmap * createTickChart(const QString &code, int beforeDuration) const;

private:
    StockModel &stockModel;
    QList<QStringList> codeCandidates;
    QStringList allCodes;


private slots:
    void codePicked(QStringList);
};


#endif
