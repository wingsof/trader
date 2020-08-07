#ifndef CHOOSER_PLUGIN_H_
#define CHOOSER_PLUGIN_H_


#include <QObject>
#include <QMap>

class StockObject;

class ChooserPlugin : public QObject {
Q_OBJECT
public:
    ChooserPlugin(QMap<QString, StockObject *> *_obj, QObject *p=0);
    ~ChooserPlugin();

    QMap<QString, StockObject *> *getStockObj();
    virtual void start() = 0;

signals:
    void codePicked(QStringList);    

private:
    QMap<QString, StockObject *> *obj;
};


#endif
