#include "chooserplugin.h"

ChooserPlugin::ChooserPlugin(QMap<QString, StockObject *> *_obj, QObject *p)
: QObject(p), obj(_obj) {

}


ChooserPlugin::~ChooserPlugin() {}


QMap<QString, StockObject *> * ChooserPlugin::getStockObj() {
    return obj;
}
