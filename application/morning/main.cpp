#include <QApplication>
#include <memory>
#include "data_provider.h"


int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    DataProvider::getInstance();
    return app.exec();
}
