#ifndef SNAPSHOT_REPORT_H_
#define SNAPSHOT_REPORT_H_

#include <iotream>


class SnapshotReport {
public:
    std::string code;
    unsigned long amount = 0;
    float profit = 0;
    unsigned long buy_volume = 0;
    unsigned long sell_volume = 0;
    float buy_speed = 100;
    float sell_speed = 100;
    unsigned int today_open = 0;
    unsigned int current_price = 0;
    bool is_kospi = false;
};


#endif
