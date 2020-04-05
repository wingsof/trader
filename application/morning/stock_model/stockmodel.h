#ifndef STOCK_MODEL_H_
#define STOCK_MODEL_H_


#include <QObject>
#include "stock_server/data_provider.h"
#include <QDate>


class StockModel : public QObject {
Q_OBJECT
public:
    StockModel();
    ~StockModel();

private:
    DataProvider & provider;     

private slots:
    void startSimulation(const QDate &);
};

#endif
