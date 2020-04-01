#include <QApplication>
#include <memory>
#include "stock_server/data_provider.h"
#include "stock_server/stock_provider.grpc.pb.h"
#include "view/mainwindow.h"
#include <time.h>

using stock_api::CybosTickData;
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
    qRegisterMetaType<CybosBidAskTickData>("CybosBidAskTickData");
    qRegisterMetaType<CybosSubjectTickData>("CybosSubjectTickData");
    qRegisterMetaType<Timestamp>("Timestamp");
    QApplication app(argc, argv);
    MainWindow main;
    main.show();
    return app.exec();
}
