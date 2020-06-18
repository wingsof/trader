#include <QGuiApplication>
#include <QQmlEngine>
#include <QQuickView>
#include <QQmlApplicationEngine>
#include <QScopedPointer>
#include "DayDataProvider.h"
//#include "stock_provider.grpc.pb.h"
#include "stock_provider.pb.h"

using stock_api::CybosTickData;
using stock_api::CybosDayDatas;
using stock_api::CybosBidAskTickData;
using stock_api::CybosSubjectTickData;
using google::protobuf::Timestamp;


int main(int argc, char *argv[]) {
    setenv("TZ", "UTC", 1);
    qRegisterMetaType<CybosTickData>("CybosTickData");
    qRegisterMetaType<CybosDayDatas>("CybosDayDatas");
    qRegisterMetaType<CybosBidAskTickData>("CybosBidAskTickData");
    qRegisterMetaType<CybosSubjectTickData>("CybosSubjectTickData");
    qRegisterMetaType<Timestamp>("Timestamp");

    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QGuiApplication app(argc, argv);

    QQmlApplicationEngine engine("main.qml");

    return app.exec();
}
