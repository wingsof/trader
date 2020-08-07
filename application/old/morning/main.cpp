#include <QGuiApplication>
#include <QQmlEngine>
#include <QQuickView>

#include <memory>
#include "stock_server/stock_provider.grpc.pb.h"
#include "stock_server/stock_object.h"
#include "view/mainwindow.h"
#include "stock_model/stockmodel.h"
#include <time.h>

using stock_api::CybosTickData;
using stock_api::CybosDayDatas;
using stock_api::CybosBidAskTickData;
using google::protobuf::Timestamp;

time_t convertDateToTime(int year,
                         int month,
                         int day,
                         int hour=0,
                         int minute=0) {
    struct tm time_str;
    time_str.tm_year = year - 1900;
    time_str.tm_mon = month - 1;
    time_str.tm_mday = day;
    time_str.tm_hour = hour;
    time_str.tm_min = minute;
    time_str.tm_sec = 0;
    time_str.tm_isdst = -1;
    return mktime(&time_str);
}

int main(int argc, char *argv[]) {
    setenv("TZ", "UTC", 1);
    qRegisterMetaType<CybosTickData>("CybosTickData");
    qRegisterMetaType<CybosDayDatas>("CybosDayDatas");
    qRegisterMetaType<CybosBidAskTickData>("CybosBidAskTickData");
    qRegisterMetaType<CybosSubjectTickData>("CybosSubjectTickData");
    qRegisterMetaType<Timestamp>("Timestamp");
    qRegisterMetaType<StockObject::PeriodTickData>("StockObject::PeriodData");

    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);

    QGuiApplication app(argc, argv);
    QQuickView view;
    view.connect(view.engine(), &QQmlEngine::quit, &app, &QCoreApplication::quit);
    //view.setSource(QUrl("qrc:/resources/morning/morning.qml"));
    view.setSource(QUrl("./morning.qml"));
    view.setResizeMode(QQuickView::SizeRootObjectToView);
    view.show();
    return app.exec();
}
