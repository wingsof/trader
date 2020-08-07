#include <QApplication>
#include <time.h>
#include "comparewidget.h"
#include "stock_provider.grpc.pb.h"
#include "data_provider.h"

using stock_api::CybosDayDatas;

int main(int argc, char *argv[]) {
    setenv("TZ", "UTC", 1);
    qRegisterMetaType<CybosDayDatas>("CybosDayDatas");

    QApplication app(argc, argv);

    DataProvider::getInstance().requestMinuteData("A005930");
    CompareWidget w;
    w.resize(1280, 1010);
    w.show();

    app.exec();
}
