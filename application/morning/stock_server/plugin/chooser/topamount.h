#ifndef TOP_AMOUNT_H_
#define TOP_AMOUNT_H_


#include <QObject>
#include <QMap>
#include "chooserplugin.h"


class MorningTimer;


class TopAmount : public ChooserPlugin {
Q_OBJECT
public:
    TopAmount(QMap<QString, StockObject *> *_obj, QObject *p=0);
    ~TopAmount();
    void start();

private:
    MorningTimer * pickTimer;    

private slots:
    void pick(); 
};


#endif
