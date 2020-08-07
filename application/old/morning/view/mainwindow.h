#ifndef MAINWINDOW_H_
#define MAINWINDOW_H_

#include <QMainWindow>

class StockModel;

class MainWindow : public QMainWindow
{
Q_OBJECT

public:
    explicit MainWindow(StockModel &_model, QWidget *parent = 0);
    ~MainWindow();

private:
    StockModel &model;
};


#endif
