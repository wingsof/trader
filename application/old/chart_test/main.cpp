#include <QApplication>
#include "testwidget.h"
#include "qwt_widget.h"
#include <time.h>

int main(int argc, char *argv[]) {
    setenv("TZ", "UTC", 1);
    QApplication app(argc, argv);
    QwtTestWidget w;
    w.show();

    app.exec();
}
