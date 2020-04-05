#include "mainwindow.h"
#include <QMdiArea>
#include <QMdiSubWindow>
#include "tick_view/tickwindow.h"
#include "stock_model/stockmodel.h"
#include "view/statusbar.h"
#include "view/bull_card/bullcard.h"


MainWindow::MainWindow(StockModel &_model, QWidget *parent)
: QMainWindow(parent), model(_model) {
    QMdiArea * mdiArea = new QMdiArea;
    TickWindow *w = new TickWindow;
    BullCard *bc = new BullCard(model);
    StatusBar * sb = new StatusBar;
    connect(sb, SIGNAL(startSimulation(const QDate &)), &model, SLOT(startSimulation(const QDate &)));

    QMdiSubWindow *s1 = mdiArea->addSubWindow(w);
    s1->setWindowFlags( (Qt::CustomizeWindowHint | Qt::WindowTitleHint) & ~Qt::WindowMinMaxButtonsHint & ~Qt::WindowCloseButtonHint );

    QMdiSubWindow *s2 = mdiArea->addSubWindow(bc);
    s2->setWindowFlags( (Qt::CustomizeWindowHint | Qt::WindowTitleHint) & ~Qt::WindowMinMaxButtonsHint & ~Qt::WindowCloseButtonHint );

    s1->resize(800, 480);
    s2->resize(800, 480);

    setCentralWidget(mdiArea);
    addToolBar(Qt::TopToolBarArea, sb);
    this->showMaximized();
}


MainWindow::~MainWindow() {
}


