#ifndef STOCK_MODEL_H_
#define STOCK_MODEL_H_


#include <QObject>
#include "stock_server/data_provider.h"
#include <QDateTime>


class StockObject;

class StockModel : public QObject {
Q_OBJECT
public:
    StockModel();
    ~StockModel();

    DataProvider & getProvider() { return provider; }
    QString getCompanyName(const QString &code);
    qreal getCurrentProfit(const QString &code);

    QPixmap * createTickChart(const QString &code, int beforeDuration) const;

    StockObject * getStockObject(const QString &code) const;
    void setCurrentCode(const QString &code);

private:
    DataProvider & provider;     
    
    QString currentCode;

private slots:
    void startSimulation(QDateTime);

signals:
    void currentCodeChanged(const QString &);
};

#endif
