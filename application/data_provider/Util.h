#include <QDate>

namespace morning {
    class Util {
        public:
        static QDate convertToDate(unsigned int d) {
            unsigned int year = d / 10000;
            unsigned int month = d % 10000 / 100;
            unsigned int day = d % 100;
            return QDate(year, month, day);
        }
    };
};
