#include <QApplication>
#include "testwidget.h"
#include "qwt_widget.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QwtTestWidget w;
    w.show();

    app.exec();
}
