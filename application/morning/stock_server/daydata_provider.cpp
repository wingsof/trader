#include "daydata_provider.h"


DayDataProvider::DayDataProvider(std::shared_ptr<stock_api::Stock::Stub> stub)
: QObject(0) {
    stub_ = stub;
}
