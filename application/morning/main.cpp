#include <QApplication>
#include <memory>
#include "data_provider.h"
#include "stock_provider.grpc.pb.h"
#include <time.h>

using stock_api::CybosTickData;
using stock_api::CybosBidAskTickData;

time_t convertDateToTime(int year, int month, int day) {
    struct tm time_str;
    time_str.tm_year = year - 1900;
    time_str.tm_mon = month - 1;
    time_str.tm_mday = day;
    time_str.tm_hour = 0;
    time_str.tm_min = 0;
    time_str.tm_sec = 0;
    time_str.tm_isdst = -1;
    return mktime(&time_str);
}

int main(int argc, char *argv[]) {
    qRegisterMetaType<CybosTickData>("CybosTickData");
    qRegisterMetaType<CybosBidAskTickData>("CybosBidAskTickData");
    QApplication app(argc, argv);
    DataProvider & provider = DataProvider::getInstance();
    provider.requestStockDayData(
        "A005930", convertDateToTime(2020, 3, 17),
        convertDateToTime(2020, 3, 20));
    provider.requestStockTick("A005930");
    provider.requestBidAskTick("A005930");
    return app.exec();
}
