#include <QApplication>
#include "testwidget.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    TestWidget w;
    w.show();

    app.exec();
}
